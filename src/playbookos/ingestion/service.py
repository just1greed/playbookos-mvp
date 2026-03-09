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
class SOPIngestionResult:
    playbook: Playbook
    step_count: int
    detected_mcp_servers: list[str] = field(default_factory=list)
    suggested_skills: list[SkillSuggestion] = field(default_factory=list)
    parsing_notes: list[str] = field(default_factory=list)


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
        compiled_spec["source_text"] = normalized_text
        compiled_spec["source_format"] = source_kind
        compiled_spec["parser_version"] = "heuristic-v1"
        compiled_spec["skill_suggestions"] = [self._skill_to_dict(item) for item in suggested_skills]
        compiled_spec["parsing_notes"] = list(parsing_notes)

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
