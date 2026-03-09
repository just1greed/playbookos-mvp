from __future__ import annotations

from typing import Any

from playbookos.api.store import NotFoundError, StoreProtocol
from playbookos.domain.models import GoalStatus, MCPServerStatus, ReflectionStatus, RunStatus, SkillStatus
from playbookos.ingestion import SOPIngestionError, analyze_sop_source


SYSTEM_SUMMARY = (
    "PlaybookOS is an agent-operable control plane for Goal -> SOP -> Skill/MCP -> Task -> Run -> "
    "Acceptance -> Reflection -> Knowledge workflows. External agents should bootstrap from the agent manifest, "
    "inspect context, then convert human requests into concrete control-plane API calls."
)


OBJECT_TYPES: list[dict[str, Any]] = [
    {
        "kind": "goal",
        "label": "Goal",
        "purpose": "Top-level objective, constraints, and completion criteria.",
        "list_endpoint": "/api/goals",
        "create_endpoint": "/api/goals",
        "update_endpoint": "/api/goals/{goal_id}",
        "follow_up_actions": ["plan", "dispatch", "autopilot", "learning"],
    },
    {
        "kind": "playbook",
        "label": "SOP / Playbook",
        "purpose": "Structured SOP compiled from Markdown or imported spec.",
        "list_endpoint": "/api/playbooks",
        "create_endpoint": "/api/playbooks/import",
        "preferred_create_endpoint": "/api/playbooks/ingest",
        "update_endpoint": "/api/playbooks/{playbook_id}",
        "follow_up_actions": ["compile", "skill-drafts", "mcp-drafts"],
    },
    {
        "kind": "skill",
        "label": "Skill",
        "purpose": "Reusable capability with schemas, approval policy, and MCP dependencies.",
        "list_endpoint": "/api/skills",
        "create_endpoint": "/api/skills",
        "update_endpoint": "/api/skills/{skill_id}",
        "follow_up_actions": ["authoring-pack", "apply-authoring-pack", "create-version", "activate", "rollback"],
    },
    {
        "kind": "mcp_server",
        "label": "MCP Server",
        "purpose": "Registered external tool endpoint used by Skills and SOP steps.",
        "list_endpoint": "/api/mcp-servers",
        "create_endpoint": "/api/mcp-servers",
        "update_endpoint": "/api/mcp-servers/{mcp_server_id}",
        "follow_up_actions": ["probe"],
    },
    {
        "kind": "knowledge_base",
        "label": "Knowledge Base",
        "purpose": "Persistent knowledge artifacts referenced by tasks and learning loops.",
        "list_endpoint": "/api/knowledge-bases",
        "create_endpoint": "/api/knowledge-bases",
        "update_endpoint": "/api/knowledge-bases/{knowledge_id}",
        "follow_up_actions": [],
    },
    {
        "kind": "task",
        "label": "Task",
        "purpose": "Executable unit generated from a goal/playbook or created manually.",
        "list_endpoint": "/api/tasks",
        "create_endpoint": "/api/tasks",
        "update_endpoint": "/api/tasks/{task_id}",
        "follow_up_actions": ["accept", "complete"],
    },
    {
        "kind": "run",
        "label": "Run",
        "purpose": "Execution attempt for a task, including approval, reflection, and metrics.",
        "list_endpoint": "/api/runs",
        "create_endpoint": "/api/runs",
        "follow_up_actions": ["execute", "approve", "reject", "reflect"],
    },
    {
        "kind": "reflection",
        "label": "Reflection",
        "purpose": "Post-run proposal and publish workflow for SOP or skill improvement.",
        "list_endpoint": "/api/reflections",
        "create_endpoint": "/api/reflections",
        "follow_up_actions": ["evaluate", "approve", "reject", "publish"],
    },
]


WORKFLOWS: list[dict[str, Any]] = [
    {
        "name": "conversation_to_sop",
        "summary": "Turn a human conversation or Markdown SOP into a structured playbook plus skill and MCP guidance.",
        "steps": [
            "Call GET /api/agent/manifest once at startup.",
            "Call POST /api/agent/intake with the human request and optional markdown_sop.",
            "If markdown_sop is present, call POST /api/playbooks/ingest.",
            "Materialize missing skill drafts and MCP drafts based on intake guidance.",
            "Apply authoring pack to draft skills before operational use.",
        ],
    },
    {
        "name": "goal_to_execution",
        "summary": "Create a goal, plan tasks, dispatch runs, and manage approvals with PlaybookOS as control plane.",
        "steps": [
            "Create or update the Goal.",
            "Link a compiled playbook or ingest a new SOP.",
            "Plan tasks and dispatch runs.",
            "Review waiting_human runs and blocked goals from agent context.",
            "Reflect and publish improvements after execution.",
        ],
    },
    {
        "name": "delegated_operations",
        "summary": "Let an external agent manage the system in discovery, builder, operator, and steward modes.",
        "steps": [
            "Bootstrap from manifest and board snapshot.",
            "Operate in dry-run planning mode first via intake.",
            "Escalate high-risk actions to human approval.",
            "Use context polling to process approvals, reflections, and MCP health issues.",
        ],
    },
]


def build_agent_manifest() -> dict[str, Any]:
    return {
        "system_name": "PlaybookOS",
        "agent_skill": {
            "name": "playbookos-operator",
            "location": "skills/playbookos-operator/SKILL.md",
            "modes": ["discover", "builder", "operator", "steward"],
        },
        "version": "0.1.0",
        "summary": SYSTEM_SUMMARY,
        "bootstrap_sequence": [
            "GET /api/agent/manifest",
            "GET /api/agent/context",
            "POST /api/agent/intake",
            "Then call concrete control-plane endpoints for mutations.",
        ],
        "write_policy": {
            "intake_is_mutation_free": True,
            "preferred_pattern": "Use /api/agent/intake to build a plan, then execute explicit API calls.",
            "human_confirmation_recommended_for": [
                "approval decisions",
                "external communications",
                "deployments or production writes",
                "SOP publish and skill activation/rollback",
            ],
        },
        "object_types": OBJECT_TYPES,
        "primary_workflows": WORKFLOWS,
        "high_risk_actions": [
            {"action": "run.approve", "endpoint": "/api/runs/{run_id}/approve", "why": "May unblock irreversible side effects."},
            {"action": "run.reject", "endpoint": "/api/runs/{run_id}/reject", "why": "Changes goal/task lifecycle and may halt work."},
            {"action": "reflection.publish", "endpoint": "/api/reflections/{reflection_id}/publish", "why": "Publishes learning back into operational SOPs."},
            {"action": "skill.activate", "endpoint": "/api/skills/{skill_id}/activate", "why": "Changes active skill behavior for future runs."},
            {"action": "task.complete", "endpoint": "/api/tasks/{task_id}/complete", "why": "Advances task graph and downstream runs."},
        ],
        "discover_endpoints": [
            "/api/board",
            "/api/meta/enums",
            "/api/errors",
            "/api/runtime-settings",
        ],
    }


def build_agent_context(store: StoreProtocol) -> dict[str, Any]:
    goals = list(store.goals.list())
    runs = list(store.runs.list())
    skills = list(store.skills.list())
    playbooks = list(store.playbooks.list())
    mcps = list(store.mcp_servers.list())
    reflections = list(store.reflections.list())
    knowledge_updates = list(store.knowledge_updates.list())
    tasks = list(store.tasks.list())

    blocked_goals = [_entity_preview(item, title_attr="title") for item in goals if item.status == GoalStatus.BLOCKED][:5]
    waiting_human_runs = [_entity_preview(item) for item in runs if item.status == RunStatus.WAITING_HUMAN][:5]
    failed_runs = [_entity_preview(item) for item in runs if item.status == RunStatus.FAILED][:5]
    draft_skills = [_entity_preview(item, title_attr="name") for item in skills if item.status == SkillStatus.DRAFT][:5]
    draft_playbooks = [_entity_preview(item, title_attr="name") for item in playbooks if getattr(item.status, 'value', item.status) == 'draft'][:5]
    unhealthy_mcps = [_mcp_preview(item) for item in mcps if item.status in {MCPServerStatus.ERROR, MCPServerStatus.INACTIVE}][:5]
    proposed_reflections = [_entity_preview(item, title_attr="summary") for item in reflections if item.eval_status == ReflectionStatus.PROPOSED][:5]
    proposed_knowledge_updates = [_entity_preview(item, title_attr="title") for item in knowledge_updates if getattr(item.status, 'value', item.status) == 'proposed'][:5]
    ready_tasks = [_entity_preview(item, title_attr="name") for item in tasks if getattr(item.status, 'value', item.status) in {'ready', 'running'}][:5]

    suggestions: list[str] = []
    if waiting_human_runs:
        suggestions.append(f"Review {len(waiting_human_runs)} waiting_human run(s) before dispatching more work.")
    if blocked_goals:
        suggestions.append(f"Resolve {len(blocked_goals)} blocked goal(s) to reopen the execution pipeline.")
    if unhealthy_mcps:
        suggestions.append(f"Probe or fix {len(unhealthy_mcps)} MCP server(s) with inactive/error health state.")
    if draft_skills:
        suggestions.append(f"Apply authoring pack or activation workflow to {len(draft_skills)} draft skill(s).")
    if proposed_reflections or proposed_knowledge_updates:
        suggestions.append("Process learning loop items so approved improvements can be published.")
    if not suggestions:
        suggestions.append("System is relatively clear; bootstrap from board and continue normal goal/task operations.")

    return {
        "system_name": "PlaybookOS",
        "board": store.board_snapshot(),
        "focus": {
            "blocked_goals": blocked_goals,
            "waiting_human_runs": waiting_human_runs,
            "failed_runs": failed_runs,
            "draft_skills": draft_skills,
            "draft_playbooks": draft_playbooks,
            "unhealthy_mcp_servers": unhealthy_mcps,
            "proposed_reflections": proposed_reflections,
            "proposed_knowledge_updates": proposed_knowledge_updates,
            "ready_tasks": ready_tasks,
        },
        "suggested_next_actions": suggestions,
    }


def analyze_agent_intake(
    store: StoreProtocol,
    *,
    message: str,
    markdown_sop: str | None = None,
    resource_name: str | None = None,
    goal_id: str | None = None,
    allow_side_effects: bool = False,
) -> dict[str, Any]:
    raw_message = str(message or "").strip()
    if not raw_message and not str(markdown_sop or "").strip():
        raise ValueError("message or markdown_sop is required")

    normalized_text = " ".join(part for part in [raw_message, resource_name or ""] if part).lower()
    intents = _detect_intents(normalized_text, has_markdown=bool(str(markdown_sop or "").strip()))
    missing_information: list[str] = []
    follow_up_questions: list[str] = []
    operations: list[dict[str, Any]] = []
    sop_preview: dict[str, Any] | None = None

    if goal_id:
        try:
            store.goals.get(goal_id)
        except NotFoundError:
            missing_information.append(f"Referenced goal_id does not exist: {goal_id}")
            follow_up_questions.append("Which existing Goal should this request attach to?")

    if "goal" in intents:
        goal_payload = {
            "title": _derive_title(raw_message, fallback=resource_name or "New Goal"),
            "objective": raw_message or resource_name or "Define a new objective in PlaybookOS.",
            "constraints": [],
            "definition_of_done": [],
            "risk_level": "medium",
        }
        operations.append(
            {
                "id": "create_goal",
                "title": "Create Goal",
                "summary": "Create a new goal from the conversation request.",
                "method": "POST",
                "endpoint": "/api/goals",
                "payload": goal_payload,
                "risk_level": "low",
                "requires_confirmation": False,
                "depends_on": [],
            }
        )

    if str(markdown_sop or "").strip():
        try:
            analysis = analyze_sop_source(
                store,
                name=resource_name or _derive_title(raw_message, fallback="Conversation SOP"),
                source_text=str(markdown_sop),
                source_kind="markdown",
            )
        except SOPIngestionError as exc:
            raise ValueError(str(exc)) from exc
        sop_preview = {
            "name": analysis.name,
            "source_kind": analysis.source_kind,
            "step_count": analysis.step_count,
            "detected_mcp_servers": analysis.detected_mcp_servers,
            "parsing_notes": analysis.parsing_notes,
            "suggested_skills": [_skill_suggestion_dict(item) for item in analysis.suggested_skills],
            "tooling_guidance": _tooling_guidance_dict(analysis.tooling_guidance),
        }
        operations.append(
            {
                "id": "ingest_playbook",
                "title": "Ingest Markdown SOP",
                "summary": "Create a compiled playbook from the provided Markdown SOP.",
                "method": "POST",
                "endpoint": "/api/playbooks/ingest",
                "payload": {
                    "name": analysis.name,
                    "source_text": str(markdown_sop),
                    "source_kind": "markdown",
                    "source_uri": None,
                    "goal_id": goal_id,
                },
                "risk_level": "low",
                "requires_confirmation": False,
                "depends_on": [],
            }
        )
        for index, suggestion in enumerate(analysis.suggested_skills[:3]):
            operations.append(
                {
                    "id": f"create_skill_draft_{index}",
                    "title": f"Create draft skill: {suggestion.name}",
                    "summary": "Materialize a draft skill from SOP analysis and optionally bind steps.",
                    "method": "POST",
                    "endpoint": "/api/playbooks/{playbook_id}/skill-drafts",
                    "payload": {"suggestion_index": index, "bind_to_unassigned_steps": True},
                    "risk_level": "medium",
                    "requires_confirmation": False,
                    "depends_on": ["ingest_playbook"],
                }
            )
        missing_mcp_servers = list((analysis.tooling_guidance.missing_mcp_servers if analysis.tooling_guidance else []) or [])
        for server_name in missing_mcp_servers[:5]:
            operations.append(
                {
                    "id": f"create_mcp_draft_{server_name}",
                    "title": f"Create draft MCP: {server_name}",
                    "summary": "Create a draft MCP record for a tool required by the SOP.",
                    "method": "POST",
                    "endpoint": "/api/playbooks/{playbook_id}/mcp-drafts",
                    "payload": {"server_name": server_name},
                    "risk_level": "medium",
                    "requires_confirmation": False,
                    "depends_on": ["ingest_playbook"],
                }
            )
        if missing_mcp_servers:
            follow_up_questions.append("Do you want me to materialize the missing MCP drafts after ingesting the SOP?")
        if analysis.suggested_skills:
            follow_up_questions.append("Should draft skills be created and bound to unassigned steps automatically?")

    if "skill" in intents and sop_preview is None:
        operations.append(
            {
                "id": "create_skill",
                "title": "Create Skill",
                "summary": "Create a draft skill directly from the conversation request.",
                "method": "POST",
                "endpoint": "/api/skills",
                "payload": {
                    "name": resource_name or _derive_skill_name(raw_message),
                    "description": raw_message or "Draft skill created from conversation request.",
                    "required_mcp_servers": [],
                    "approval_policy": {},
                    "evaluation_policy": {},
                    "status": "draft",
                },
                "risk_level": "low",
                "requires_confirmation": False,
                "depends_on": [],
            }
        )
        follow_up_questions.append("Which MCP servers should this Skill depend on?")

    if "mcp" in intents and sop_preview is None:
        operations.append(
            {
                "id": "create_mcp",
                "title": "Register MCP server",
                "summary": "Create an MCP server record, then probe its health.",
                "method": "POST",
                "endpoint": "/api/mcp-servers",
                "payload": {
                    "name": resource_name or _derive_mcp_name(raw_message),
                    "transport": "streamable_http",
                    "endpoint": "",
                    "scopes": [],
                    "auth_config": {},
                    "status": "inactive",
                },
                "risk_level": "medium",
                "requires_confirmation": False,
                "depends_on": [],
            }
        )
        missing_information.append("MCP endpoint URL is required to create and probe a new MCP server.")
        follow_up_questions.append("What endpoint URL and minimum scopes should the MCP server use?")

    if "task" in intents:
        operations.append(
            {
                "id": "create_task",
                "title": "Create Task",
                "summary": "Create a task once goal_id and playbook_id are known.",
                "method": "POST",
                "endpoint": "/api/tasks",
                "payload": {
                    "goal_id": goal_id or "<goal_id>",
                    "playbook_id": "<playbook_id>",
                    "name": resource_name or _derive_title(raw_message, fallback="Conversation Task"),
                    "description": raw_message or "Task created from conversation request.",
                    "knowledge_base_ids": [],
                    "approval_required": False,
                    "queue_name": "default",
                    "priority": 0,
                },
                "risk_level": "low",
                "requires_confirmation": False,
                "depends_on": [],
            }
        )
        if not goal_id:
            missing_information.append("goal_id is required before a task can be created.")
            follow_up_questions.append("Which Goal should this Task belong to?")
        follow_up_questions.append("Which Playbook should this Task execute?")

    if "operator" in intents or "steward" in intents:
        operations.extend(
            [
                {
                    "id": "refresh_context",
                    "title": "Refresh agent context",
                    "summary": "Load board snapshot, blockers, approvals, and learning items.",
                    "method": "GET",
                    "endpoint": "/api/agent/context",
                    "payload": {},
                    "risk_level": "low",
                    "requires_confirmation": False,
                    "depends_on": [],
                },
                {
                    "id": "inspect_board",
                    "title": "Inspect board",
                    "summary": "Read global counts and system health before taking action.",
                    "method": "GET",
                    "endpoint": "/api/board",
                    "payload": {},
                    "risk_level": "low",
                    "requires_confirmation": False,
                    "depends_on": [],
                },
            ]
        )

    if not operations:
        operations.append(
            {
                "id": "bootstrap_manifest",
                "title": "Bootstrap manifest",
                "summary": "Load the agent manifest before taking more specific actions.",
                "method": "GET",
                "endpoint": "/api/agent/manifest",
                "payload": {},
                "risk_level": "low",
                "requires_confirmation": False,
                "depends_on": [],
            }
        )
        follow_up_questions.append("Do you want to create a Goal, ingest a Markdown SOP, register an MCP, create a Skill, or create a Task?")

    deduped_intents = list(dict.fromkeys(intents))
    deduped_missing = list(dict.fromkeys(missing_information))
    deduped_questions = list(dict.fromkeys(follow_up_questions))[:6]
    summary = _build_summary(deduped_intents, sop_preview, deduped_missing)
    return {
        "summary": summary,
        "execution_mode": "dry_run_plan_only",
        "allow_side_effects_requested": allow_side_effects,
        "detected_intents": deduped_intents,
        "missing_information": deduped_missing,
        "follow_up_questions": deduped_questions,
        "recommended_operations": operations,
        "sop_preview": sop_preview,
    }


def _detect_intents(text: str, *, has_markdown: bool) -> list[str]:
    intents: list[str] = []
    if has_markdown or _contains_any(text, ["sop", "playbook", "markdown", "流程", "操作手册", "剧本"]):
        intents.extend(["playbook", "skill", "mcp"])
    if _contains_any(text, ["goal", "目标", "objective"]):
        intents.append("goal")
    if _contains_any(text, ["skill", "技能"]):
        intents.append("skill")
    if _contains_any(text, ["mcp", "工具接入", "工具", "github", "slack", "notion", "jira", "email"]):
        intents.append("mcp")
    if _contains_any(text, ["task", "任务"]):
        intents.append("task")
    if _contains_any(text, ["托管", "manage", "operate", "dispatch", "审批", "approve", "review", "reflect", "发布", "publish"]):
        intents.extend(["operator", "steward"])
    return intents or ["discover"]


def _contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def _derive_title(message: str, *, fallback: str) -> str:
    cleaned = " ".join(str(message or "").split())
    if not cleaned:
        return fallback
    if len(cleaned) <= 72:
        return cleaned
    return cleaned[:69].rstrip() + "..."


def _derive_skill_name(message: str) -> str:
    base = _derive_title(message, fallback="Conversation Skill")
    return base if "skill" in base.lower() or "技能" in base else f"{base} Skill"


def _derive_mcp_name(message: str) -> str:
    lowered = str(message or "").lower()
    for candidate in ["github", "slack", "notion", "jira", "email", "calendar", "sheets"]:
        if candidate in lowered:
            return candidate
    return resource_safe_name(_derive_title(message, fallback="new-mcp"))


def resource_safe_name(value: str) -> str:
    lowered = "-".join(str(value or "").strip().lower().split())
    return lowered.strip("-") or "new-mcp"


def _entity_preview(item: Any, *, title_attr: str = "id") -> dict[str, Any]:
    title = getattr(item, title_attr, None) or getattr(item, "name", None) or getattr(item, "title", None) or getattr(item, "id", "")
    status = getattr(getattr(item, "status", None), "value", getattr(item, "status", None))
    return {"id": getattr(item, "id", ""), "title": title, "status": status}


def _mcp_preview(item: Any) -> dict[str, Any]:
    health = dict(getattr(item, "auth_config", {}) or {}).get("health")
    preview = _entity_preview(item, title_attr="name")
    preview["endpoint"] = getattr(item, "endpoint", "")
    preview["health"] = health
    return preview


def _skill_suggestion_dict(item: Any) -> dict[str, Any]:
    return {
        "name": item.name,
        "description": item.description,
        "required_mcp_servers": list(item.required_mcp_servers),
        "rationale": item.rationale,
        "sample_task_names": list(item.sample_task_names),
        "approval_hint": item.approval_hint,
    }


def _tooling_guidance_dict(item: Any) -> dict[str, Any] | None:
    if item is None:
        return None
    return {
        "summary": item.summary,
        "required_mcp_servers": list(item.required_mcp_servers),
        "suggested_skill_names": list(item.suggested_skill_names),
        "existing_skill_candidates": list(item.existing_skill_candidates),
        "existing_mcp_candidates": list(item.existing_mcp_candidates),
        "missing_mcp_servers": list(item.missing_mcp_servers),
        "action_items": list(item.action_items),
        "tool_requirements": [
            {
                "tool_name": requirement.tool_name,
                "purpose": requirement.purpose,
                "rationale": requirement.rationale,
                "related_steps": list(requirement.related_steps),
                "suggested_skill_name": requirement.suggested_skill_name,
                "suggested_mcp_server": requirement.suggested_mcp_server,
            }
            for requirement in item.tool_requirements
        ],
        "prompt_blocks": [
            {
                "key": block.key,
                "title": block.title,
                "objective": block.objective,
                "prompt": block.prompt,
            }
            for block in item.prompt_blocks
        ],
    }


def _build_summary(intents: list[str], sop_preview: dict[str, Any] | None, missing_information: list[str]) -> str:
    if sop_preview is not None:
        missing_mcp_count = len(((sop_preview.get("tooling_guidance") or {}).get("missing_mcp_servers") or []))
        return (
            f"Detected {len(intents)} intent(s); Markdown SOP preview extracted {sop_preview.get('step_count', 0)} step(s), "
            f"{len(sop_preview.get('suggested_skills', []))} suggested skill(s), and {missing_mcp_count} missing MCP draft candidate(s)."
        )
    if missing_information:
        return f"Detected intents: {', '.join(intents)}. Additional information is still required before safe execution."
    return f"Detected intents: {', '.join(intents)}. Recommended operations are ready for explicit API execution."
