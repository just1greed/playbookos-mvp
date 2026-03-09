from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from playbookos.api.store import StoreProtocol
from playbookos.domain.models import Playbook, PlaybookStatus, Skill, SkillStatus, utc_now
from playbookos.supervisor import append_event


class SOPIngestionError(ValueError):
    pass


@dataclass(slots=True)
class SkillSuggestion:
    name: str
    description: str
    required_mcp_servers: list[str] = field(default_factory=list)
    rationale: str = ""
    sample_task_names: list[str] = field(default_factory=list)
    approval_hint: str = ""


@dataclass(slots=True)
class ToolRequirement:
    tool_name: str
    purpose: str
    rationale: str
    related_steps: list[str] = field(default_factory=list)
    suggested_skill_name: str = ""
    suggested_mcp_server: str = ""


@dataclass(slots=True)
class PromptBlock:
    key: str
    title: str
    objective: str
    prompt: str


@dataclass(slots=True)
class ToolingGuidance:
    summary: str
    required_mcp_servers: list[str] = field(default_factory=list)
    suggested_skill_names: list[str] = field(default_factory=list)
    existing_skill_candidates: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    tool_requirements: list[ToolRequirement] = field(default_factory=list)
    prompt_blocks: list[PromptBlock] = field(default_factory=list)


@dataclass(slots=True)
class SOPIngestionResult:
    playbook: Playbook
    step_count: int
    detected_mcp_servers: list[str] = field(default_factory=list)
    suggested_skills: list[SkillSuggestion] = field(default_factory=list)
    parsing_notes: list[str] = field(default_factory=list)
    tooling_guidance: ToolingGuidance | None = None


@dataclass(slots=True)
class SkillMaterializationResult:
    playbook: Playbook
    skill: Skill
    suggestion_index: int
    bound_step_count: int = 0


class SOPCompiler:
    _tool_aliases = {
        "github": ["github", "git", "pull request", "repo"],
        "slack": ["slack", "channel", "notify", "announcement"],
        "notion": ["notion", "doc", "docs", "wiki"],
        "jira": ["jira", "ticket", "issue"],
        "email": ["email", "mail", "inbox"],
        "sheets": ["sheet", "spreadsheet", "excel"],
        "calendar": ["calendar", "meeting", "schedule"],
    }

    _skill_profiles = {
        "writer": {
            "name": "SOP Writer",
            "description": "Draft, refine, and publish structured written deliverables from a playbook.",
            "keywords": ["draft", "write", "publish", "document", "summarize", "note"],
            "approval_hint": "Enable approval for external publication or customer-facing copy.",
        },
        "researcher": {
            "name": "Research Analyst",
            "description": "Collect, compare, and synthesize source material before execution.",
            "keywords": ["research", "analyze", "investigate", "collect", "compare", "review"],
            "approval_hint": "Keep manual review for low-confidence or conflicting source material.",
        },
        "operator": {
            "name": "Workflow Operator",
            "description": "Execute checklist-driven operational steps and keep the run moving.",
            "keywords": ["run", "execute", "perform", "complete", "follow", "prepare"],
            "approval_hint": "Use HITL gates around irreversible actions and account-level changes.",
        },
        "communicator": {
            "name": "Stakeholder Communicator",
            "description": "Coordinate updates, notifications, and handoffs across people and systems.",
            "keywords": ["notify", "send", "share", "communicate", "announce", "follow up"],
            "approval_hint": "Require approval before sending external or executive communications.",
        },
        "builder": {
            "name": "Implementation Builder",
            "description": "Implement changes, produce artifacts, and validate technical outcomes.",
            "keywords": ["build", "implement", "code", "fix", "deploy", "test"],
            "approval_hint": "Add review gates before deployment, migration, or production writes.",
        },
    }

    def ingest(
        self,
        store: StoreProtocol,
        *,
        name: str,
        source_text: str,
        source_kind: str = "markdown",
        source_uri: str | None = None,
        goal_id: str | None = None,
    ) -> SOPIngestionResult:
        normalized_text = str(source_text or "").strip()
        if not normalized_text:
            raise SOPIngestionError("SOP source text is required")
        if goal_id is not None:
            store.goals.get(goal_id)

        compiled_spec, parsing_notes = self._compile_source(source_kind, normalized_text)
        step_count = len(compiled_spec.get("steps", []))
        detected_mcp_servers = list(compiled_spec.get("mcp_servers", []))
        suggested_skills = self._suggest_skills(compiled_spec.get("steps", []), detected_mcp_servers)
        tooling_guidance = self._build_tooling_guidance(
            store,
            playbook_name=name,
            steps=compiled_spec.get("steps", []),
            detected_mcp_servers=detected_mcp_servers,
            suggested_skills=suggested_skills,
        )
        compiled_spec["source_text"] = normalized_text
        compiled_spec["source_format"] = source_kind
        compiled_spec["parser_version"] = "heuristic-v2-markdown-tooling"
        compiled_spec["skill_suggestions"] = [self._skill_to_dict(item) for item in suggested_skills]
        compiled_spec["parsing_notes"] = list(parsing_notes)
        compiled_spec["tooling_guidance"] = self._tooling_guidance_to_dict(tooling_guidance)

        playbook = Playbook(
            name=name,
            source_kind=source_kind,
            source_uri=source_uri or self._build_manual_uri(name),
            goal_id=goal_id,
            compiled_spec=compiled_spec,
            status=PlaybookStatus.COMPILED if step_count else PlaybookStatus.DRAFT,
        )
        store.playbooks.save(playbook)
        append_event(
            store,
            entity_type="playbook",
            entity_id=playbook.id,
            event_type="playbook.ingested",
            payload={
                "goal_id": goal_id,
                "step_count": step_count,
                "mcp_servers": detected_mcp_servers,
                "suggested_skill_count": len(suggested_skills),
            },
            source="human",
        )
        return SOPIngestionResult(
            playbook=playbook,
            step_count=step_count,
            detected_mcp_servers=detected_mcp_servers,
            suggested_skills=suggested_skills,
            parsing_notes=parsing_notes,
            tooling_guidance=tooling_guidance,
        )

    def _compile_source(self, source_kind: str, source_text: str) -> tuple[dict[str, Any], list[str]]:
        normalized_kind = str(source_kind or "markdown").strip().lower()
        if normalized_kind == "json":
            return self._compile_json(source_text)
        return self._compile_text(source_text)

    def _compile_json(self, source_text: str) -> tuple[dict[str, Any], list[str]]:
        try:
            payload = json.loads(source_text)
        except json.JSONDecodeError as exc:
            raise SOPIngestionError(f"Invalid JSON SOP source: {exc.msg}") from exc

        if isinstance(payload, dict):
            steps = payload.get("steps", [])
            mcp_servers = payload.get("mcp_servers", [])
        elif isinstance(payload, list):
            steps = payload
            mcp_servers = []
        else:
            raise SOPIngestionError("JSON SOP source must be an object or array")

        compiled_spec = {
            "steps": self._normalize_steps(steps),
            "mcp_servers": self._normalize_mcp_servers(mcp_servers),
        }
        notes = ["Parsed structured JSON SOP payload."]
        if not compiled_spec["steps"]:
            notes.append("JSON source did not include explicit steps; manual refinement is recommended.")
        return compiled_spec, notes

    def _compile_text(self, source_text: str) -> tuple[dict[str, Any], list[str]]:
        lines = [line.rstrip() for line in source_text.splitlines()]
        step_lines: list[str] = []
        section_hint = ""
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue
            if re.match(r"^#{1,6}\s+", line):
                section_hint = re.sub(r"^#{1,6}\s+", "", line).strip()
                continue
            if re.match(r"^(?:[-*+]\s+|\d+[.)]\s+|\[[xX ]\]\s+)", line):
                step_lines.append(re.sub(r"^(?:[-*+]\s+|\d+[.)]\s+|\[[xX ]\]\s+)", "", line).strip())
                continue
            if len(line.split()) >= 4 and self._looks_like_instruction(line):
                step_lines.append(line)

        if not step_lines:
            paragraphs = [part.strip() for part in re.split(r"\n\s*\n", source_text) if part.strip()]
            step_lines = paragraphs[:8]

        steps = self._normalize_steps(step_lines)
        mcp_servers = self._detect_mcp_servers(source_text)
        notes = ["Parsed unstructured SOP text with heuristic step extraction."]
        if section_hint:
            notes.append(f"Detected primary section heading: {section_hint}.")
        if not mcp_servers:
            notes.append("No MCP servers detected automatically; confirm tool requirements manually.")
        return {"steps": steps, "mcp_servers": mcp_servers}, notes

    def _normalize_steps(self, raw_steps: list[Any]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for index, raw_step in enumerate(raw_steps):
            if isinstance(raw_step, dict):
                name = str(raw_step.get("name") or raw_step.get("title") or f"Step {index + 1}").strip()
                description = str(raw_step.get("description") or raw_step.get("instruction") or name).strip()
                normalized.append({**raw_step, "name": name, "description": description})
                continue
            text = str(raw_step or "").strip()
            if not text:
                continue
            normalized.append(
                {
                    "name": self._step_name(text, index),
                    "description": text,
                    "instruction": text,
                    "priority": index,
                }
            )
        return normalized

    def _normalize_mcp_servers(self, raw_servers: list[Any]) -> list[str]:
        seen: set[str] = set()
        normalized: list[str] = []
        for raw_server in raw_servers:
            name = str(raw_server or "").strip().lower()
            if not name or name in seen:
                continue
            seen.add(name)
            normalized.append(name)
        return normalized

    def _detect_mcp_servers(self, source_text: str) -> list[str]:
        text = source_text.lower()
        detected: list[str] = []
        for server_name, aliases in self._tool_aliases.items():
            if any(alias in text for alias in aliases):
                detected.append(server_name)
        return detected

    def _suggest_skills(self, steps: list[dict[str, Any]], detected_mcp_servers: list[str]) -> list[SkillSuggestion]:
        score_map: dict[str, int] = {key: 0 for key in self._skill_profiles}
        example_steps: dict[str, list[str]] = {key: [] for key in self._skill_profiles}
        for step in steps:
            content = f"{step.get('name', '')} {step.get('description', '')}".lower()
            matched = False
            for profile_key, profile in self._skill_profiles.items():
                if any(keyword in content for keyword in profile["keywords"]):
                    score_map[profile_key] += 1
                    example_steps[profile_key].append(str(step.get("name") or step.get("description") or ""))
                    matched = True
            if not matched:
                score_map["operator"] += 1
                example_steps["operator"].append(str(step.get("name") or step.get("description") or ""))

        ranked_profiles = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
        suggestions: list[SkillSuggestion] = []
        for profile_key, score in ranked_profiles:
            if score <= 0:
                continue
            profile = self._skill_profiles[profile_key]
            suggestions.append(
                SkillSuggestion(
                    name=profile["name"],
                    description=profile["description"],
                    required_mcp_servers=self._mcp_subset_for_profile(profile_key, detected_mcp_servers),
                    rationale=f"Matched {score} extracted SOP step(s) to this skill profile.",
                    sample_task_names=example_steps[profile_key][:3],
                    approval_hint=profile["approval_hint"],
                )
            )
            if len(suggestions) >= 3:
                break

        if not suggestions:
            suggestions.append(
                SkillSuggestion(
                    name="General SOP Operator",
                    description="Execute a mixed playbook with manual review gates where needed.",
                    required_mcp_servers=list(detected_mcp_servers),
                    rationale="Fallback suggestion because the parser could not confidently classify the SOP.",
                    approval_hint="Start in draft mode and require approval for external side effects.",
                )
            )
        return suggestions

    def _mcp_subset_for_profile(self, profile_key: str, detected_mcp_servers: list[str]) -> list[str]:
        if profile_key == "writer":
            preferred = {"notion", "github", "email"}
        elif profile_key == "communicator":
            preferred = {"slack", "email", "calendar"}
        elif profile_key == "builder":
            preferred = {"github", "jira"}
        elif profile_key == "researcher":
            preferred = {"notion", "sheets", "jira"}
        else:
            preferred = set(detected_mcp_servers)
        subset = [item for item in detected_mcp_servers if item in preferred]
        return subset or list(detected_mcp_servers)


    def _build_tooling_guidance(
        self,
        store: StoreProtocol,
        *,
        playbook_name: str,
        steps: list[dict[str, Any]],
        detected_mcp_servers: list[str],
        suggested_skills: list[SkillSuggestion],
    ) -> ToolingGuidance:
        tool_requirements = self._tool_requirements(steps, detected_mcp_servers, suggested_skills)
        existing_candidates = self._existing_skill_candidates(store, detected_mcp_servers, suggested_skills)
        suggested_skill_names = [item.name for item in suggested_skills]
        required_mcp_servers = list(detected_mcp_servers)
        if required_mcp_servers:
            mcp_summary = ", ".join(required_mcp_servers)
            summary = f"该 Markdown SOP 识别出 {len(required_mcp_servers)} 个外部工具域：{mcp_summary}。建议先确认 MCP，再上传或创建对应 Skill。"
        else:
            summary = "该 Markdown SOP 尚未稳定识别出外部工具，请用工具发现提示词人工确认后再配置 Skill / MCP。"
        action_items = [
            f"先确认这份 SOP 需要的 MCP：{', '.join(required_mcp_servers) if required_mcp_servers else '请人工确认工具域'}。",
            f"优先上传或创建这些 Skill：{', '.join(suggested_skill_names[:3]) if suggested_skill_names else 'General SOP Operator'}。",
            "把 Skill 绑定到涉及外部系统的步骤，再应用 Authoring Wizard 补齐 schema、审批策略与评测策略。",
        ]
        if existing_candidates:
            action_items.append(f"仓库里已有可复用 Skill 候选：{', '.join(existing_candidates[:3])}。可先复用，再决定是否新建。")
        action_items.append("当前版本重点支持 Markdown SOP；附件、多格式解析和 MCP 真正注册流后续再补。")
        prompt_blocks = self._build_prompt_blocks(
            playbook_name=playbook_name,
            steps=steps,
            tool_requirements=tool_requirements,
            required_mcp_servers=required_mcp_servers,
            suggested_skill_names=suggested_skill_names,
        )
        return ToolingGuidance(
            summary=summary,
            required_mcp_servers=required_mcp_servers,
            suggested_skill_names=suggested_skill_names,
            existing_skill_candidates=existing_candidates,
            action_items=action_items,
            tool_requirements=tool_requirements,
            prompt_blocks=prompt_blocks,
        )

    def _tool_requirements(
        self,
        steps: list[dict[str, Any]],
        detected_mcp_servers: list[str],
        suggested_skills: list[SkillSuggestion],
    ) -> list[ToolRequirement]:
        requirements: list[ToolRequirement] = []
        for server_name in detected_mcp_servers:
            aliases = self._tool_aliases.get(server_name, [server_name])
            related_steps: list[str] = []
            for step in steps:
                content = f"{step.get('name', '')} {step.get('description', '')}".lower()
                if any(alias in content for alias in aliases):
                    related_steps.append(str(step.get("name") or step.get("description") or server_name))
            if not related_steps:
                related_steps = [str(step.get("name") or step.get("description") or "") for step in steps[:2] if str(step.get("name") or step.get("description") or "").strip()]
            suggested_skill_name = next((item.name for item in suggested_skills if server_name in item.required_mcp_servers), suggested_skills[0].name if suggested_skills else "General SOP Operator")
            requirements.append(
                ToolRequirement(
                    tool_name=server_name,
                    purpose=self._tool_purpose(server_name),
                    rationale=self._tool_rationale(server_name, related_steps),
                    related_steps=related_steps[:3],
                    suggested_skill_name=suggested_skill_name,
                    suggested_mcp_server=server_name,
                )
            )
        return requirements

    def _existing_skill_candidates(
        self,
        store: StoreProtocol,
        detected_mcp_servers: list[str],
        suggested_skills: list[SkillSuggestion],
    ) -> list[str]:
        detected = set(detected_mcp_servers)
        suggestion_names = {item.name.lower() for item in suggested_skills}
        candidates: list[str] = []
        for skill in store.skills.list():
            overlap = detected & set(skill.required_mcp_servers)
            name_hit = skill.name.lower() in suggestion_names
            if not overlap and not name_hit:
                continue
            label = skill.name
            if overlap:
                label = f"{label} ({', '.join(sorted(overlap))})"
            candidates.append(label)
        return list(dict.fromkeys(candidates))[:5]

    def _build_prompt_blocks(
        self,
        *,
        playbook_name: str,
        steps: list[dict[str, Any]],
        tool_requirements: list[ToolRequirement],
        required_mcp_servers: list[str],
        suggested_skill_names: list[str],
    ) -> list[PromptBlock]:
        step_lines = [f"- {step.get('name') or step.get('description') or 'step'}" for step in steps[:8]]
        requirement_lines = [
            f"- tool={item.tool_name}; purpose={item.purpose}; steps={', '.join(item.related_steps) or 'n/a'}; skill={item.suggested_skill_name or 'n/a'}"
            for item in tool_requirements
        ]
        prompt_common = "\n".join(step_lines) or "- n/a"
        tool_common = "\n".join(requirement_lines) or "- tool=manual_review; purpose=Confirm tools manually"
        mcp_list = ", ".join(required_mcp_servers) or "manual confirmation required"
        skill_list = ", ".join(suggested_skill_names) or "General SOP Operator"
        return [
            PromptBlock(
                key="tool_discovery",
                title="工具发现提示词",
                objective="从 Markdown SOP 中识别需要接入的工具域、对应 MCP，以及每个步骤依赖的外部能力。",
                prompt=(
                    "你是 PlaybookOS 的 tool discovery planner。请只基于下面这份 Markdown SOP，输出 JSON，不要输出解释性散文。\n\n"
                    "输出 JSON 结构：{\n"
                    '  "tools": [{"tool_name": "", "why_needed": "", "related_steps": [], "suggested_mcp_server": "", "risk_level": "low|medium|high"}],\n'
                    '  "skills": [{"skill_name": "", "covered_steps": [], "required_mcp_servers": [], "why": ""}],\n'
                    '  "gaps": [{"type": "missing_mcp|missing_skill", "name": "", "reason": ""}]\n'
                    "}\n\n"
                    f"SOP 名称：{playbook_name}\n"
                    f"步骤：\n{prompt_common}\n\n"
                    f"当前启发式识别结果：\n{tool_common}\n\n"
                    "要求：\n"
                    "1. 优先识别真正需要接入的外部系统，而不是泛化的抽象动作。\n"
                    "2. 每个 tool 都要回指 SOP 里的步骤证据。\n"
                    "3. 如果无法确定，请显式写进 gaps，而不是猜测。"
                ),
            ),
            PromptBlock(
                key="skill_upload",
                title="Skill 上传提示词",
                objective="根据 SOP 步骤和已识别工具，设计应该上传/创建的 Skill 及其最小职责边界。",
                prompt=(
                    "你是 PlaybookOS 的 skill authoring copilot。请根据 SOP 与工具需求，给出建议上传的 Skill 清单。\n\n"
                    "输出 JSON 结构：{\n"
                    '  "skills": [{"name": "", "description": "", "covered_steps": [], "required_mcp_servers": [], "approval_mode": "manual_review|auto_execute", "evaluation_focus": []}]\n'
                    "}\n\n"
                    f"SOP 名称：{playbook_name}\n"
                    f"步骤：\n{prompt_common}\n\n"
                    f"建议优先 Skill：{skill_list}\n"
                    f"需要的 MCP：{mcp_list}\n\n"
                    "要求：\n"
                    "1. Skill 要尽量高内聚，不要把所有步骤塞进一个大 Skill。\n"
                    "2. 涉及外发、发布、部署、写系统动作时，默认给 manual_review。\n"
                    "3. required_mcp_servers 只保留真正执行所需的最小集合。"
                ),
            ),
            PromptBlock(
                key="mcp_upload",
                title="MCP 接入提示词",
                objective="把 SOP 中识别出的工具需求翻译成用户需要补齐的 MCP 接入清单与最小权限范围。",
                prompt=(
                    "你是 PlaybookOS 的 MCP onboarding planner。请把 SOP 所需工具整理成 MCP 接入清单。\n\n"
                    "输出 JSON 结构：{\n"
                    '  "mcp_servers": [{"name": "", "purpose": "", "minimum_scopes": [], "write_actions": [], "related_skills": []}],\n'
                    '  "review_points": []\n'
                    "}\n\n"
                    f"SOP 名称：{playbook_name}\n"
                    f"需要的 MCP：{mcp_list}\n"
                    f"工具证据：\n{tool_common}\n\n"
                    "要求：\n"
                    "1. minimum_scopes 必须体现最小权限原则。\n"
                    "2. 如果某个 MCP 只需要读能力，不要给写权限。\n"
                    "3. 把需要人工确认的高风险写操作列进 review_points。"
                ),
            ),
        ]

    def _tool_purpose(self, server_name: str) -> str:
        purposes = {
            "github": "读取或提交代码、PR、仓库状态",
            "slack": "发送通知、同步频道状态、触发协作沟通",
            "notion": "读取或更新文档、知识页、SOP 草稿",
            "jira": "读取或更新工单、任务状态、问题跟踪",
            "email": "发送邮件、外部沟通、回执确认",
            "sheets": "读取或更新表格数据",
            "calendar": "查询日程、安排会议、同步时间",
        }
        return purposes.get(server_name, "执行与该外部系统相关的 SOP 步骤")

    def _tool_rationale(self, server_name: str, related_steps: list[str]) -> str:
        if related_steps:
            return f"SOP 中这些步骤明显依赖 {server_name}：" + "; ".join(related_steps[:3])
        return f"SOP 中出现了与 {server_name} 相关的动作或实体，需要进一步人工确认其接入方式。"

    def _step_name(self, text: str, index: int) -> str:
        parts = re.split(r"[.;:，。]", text, maxsplit=1)
        candidate = parts[0].strip()[:80]
        return candidate or f"Step {index + 1}"

    def _looks_like_instruction(self, line: str) -> bool:
        lowered = line.lower()
        return any(
            lowered.startswith(prefix)
            for prefix in (
                "collect",
                "draft",
                "prepare",
                "review",
                "publish",
                "send",
                "update",
                "confirm",
                "检查",
                "准备",
                "发布",
                "同步",
                "发送",
            )
        )

    def _skill_to_dict(self, skill: SkillSuggestion) -> dict[str, Any]:
        return {
            "name": skill.name,
            "description": skill.description,
            "required_mcp_servers": list(skill.required_mcp_servers),
            "rationale": skill.rationale,
            "sample_task_names": list(skill.sample_task_names),
            "approval_hint": skill.approval_hint,
        }

    def _tool_requirement_to_dict(self, item: ToolRequirement) -> dict[str, Any]:
        return {
            "tool_name": item.tool_name,
            "purpose": item.purpose,
            "rationale": item.rationale,
            "related_steps": list(item.related_steps),
            "suggested_skill_name": item.suggested_skill_name,
            "suggested_mcp_server": item.suggested_mcp_server,
        }

    def _prompt_block_to_dict(self, item: PromptBlock) -> dict[str, Any]:
        return {
            "key": item.key,
            "title": item.title,
            "objective": item.objective,
            "prompt": item.prompt,
        }

    def _tooling_guidance_to_dict(self, item: ToolingGuidance) -> dict[str, Any]:
        return {
            "summary": item.summary,
            "required_mcp_servers": list(item.required_mcp_servers),
            "suggested_skill_names": list(item.suggested_skill_names),
            "existing_skill_candidates": list(item.existing_skill_candidates),
            "action_items": list(item.action_items),
            "tool_requirements": [self._tool_requirement_to_dict(requirement) for requirement in item.tool_requirements],
            "prompt_blocks": [self._prompt_block_to_dict(block) for block in item.prompt_blocks],
        }

    def _build_manual_uri(self, name: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", str(name or "manual").strip().lower()).strip("-") or "manual"
        return f"playbookos://ingested/playbook/{slug}-{int(utc_now().timestamp())}"


def ingest_sop_in_store(
    store: StoreProtocol,
    *,
    name: str,
    source_text: str,
    source_kind: str = "markdown",
    source_uri: str | None = None,
    goal_id: str | None = None,
) -> SOPIngestionResult:
    return SOPCompiler().ingest(
        store,
        name=name,
        source_text=source_text,
        source_kind=source_kind,
        source_uri=source_uri,
        goal_id=goal_id,
    )


def materialize_suggested_skill_in_store(
    store: StoreProtocol,
    playbook_id: str,
    *,
    suggestion_index: int = 0,
    bind_to_unassigned_steps: bool = False,
) -> SkillMaterializationResult:
    playbook = store.playbooks.get(playbook_id)
    suggestions = list(playbook.compiled_spec.get("skill_suggestions", []))
    if not suggestions:
        raise SOPIngestionError("Playbook does not contain any skill suggestions")
    if suggestion_index < 0 or suggestion_index >= len(suggestions):
        raise SOPIngestionError(f"Skill suggestion index {suggestion_index} is out of range")

    suggestion = suggestions[suggestion_index]
    skill_name = str(suggestion.get("name") or f"{playbook.name} Skill").strip()
    existing_names = {item.name for item in store.skills.list()}
    if skill_name in existing_names:
        skill_name = f"{skill_name} · {playbook.name}"

    required_mcp_servers = [str(item).strip() for item in suggestion.get("required_mcp_servers", []) if str(item).strip()]
    skill = Skill(
        name=skill_name,
        description=str(suggestion.get("description") or f"Draft skill generated from playbook {playbook.name}.").strip(),
        input_schema={
            "type": "object",
            "properties": {
                "goal": {"type": "string"},
                "task": {"type": "string"},
                "context": {"type": "object"},
            },
        },
        output_schema={
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "artifacts": {"type": "array"},
                "follow_ups": {"type": "array"},
            },
        },
        required_mcp_servers=required_mcp_servers,
        approval_policy={
            "hint": str(suggestion.get("approval_hint") or "Require human review before irreversible actions."),
            "mode": "manual_review",
        },
        evaluation_policy={
            "source": "sop_ingestion",
            "playbook_id": playbook.id,
            "sample_task_names": list(suggestion.get("sample_task_names", [])),
        },
        status=SkillStatus.DRAFT,
    )
    store.skills.save(skill)

    bound_step_count = 0
    if bind_to_unassigned_steps:
        steps = []
        for step in list(playbook.compiled_spec.get("steps", [])):
            if not isinstance(step, dict):
                steps.append(step)
                continue
            if step.get("assigned_skill_id") or step.get("skill_id"):
                steps.append(step)
                continue
            updated_step = dict(step)
            updated_step["assigned_skill_id"] = skill.id
            steps.append(updated_step)
            bound_step_count += 1
        playbook.compiled_spec = {**playbook.compiled_spec, "steps": steps}
        playbook.updated_at = utc_now()
        store.playbooks.save(playbook)

    append_event(
        store,
        entity_type="skill",
        entity_id=skill.id,
        event_type="skill.draft_materialized",
        payload={
            "playbook_id": playbook.id,
            "suggestion_index": suggestion_index,
            "bound_step_count": bound_step_count,
        },
        source="human",
    )
    return SkillMaterializationResult(
        playbook=playbook,
        skill=skill,
        suggestion_index=suggestion_index,
        bound_step_count=bound_step_count,
    )
