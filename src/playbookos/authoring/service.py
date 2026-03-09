from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from playbookos.api.store import StoreProtocol
from playbookos.domain.models import Playbook, Skill, utc_now
from playbookos.supervisor import append_event


class SkillAuthoringError(ValueError):
    pass


@dataclass(slots=True)
class SkillAuthoringPack:
    skill_id: str
    skill_name: str
    playbook_id: str | None
    playbook_name: str | None
    recommended_input_schema: dict[str, Any]
    recommended_output_schema: dict[str, Any]
    recommended_approval_policy: dict[str, Any]
    recommended_evaluation_policy: dict[str, Any]
    checklist: list[str] = field(default_factory=list)
    risk_signals: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    linked_step_names: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SkillAuthoringApplyResult:
    skill: Skill
    authoring_pack: SkillAuthoringPack
    applied_fields: list[str] = field(default_factory=list)


class SkillAuthoringWizard:
    def build_pack(self, store: StoreProtocol, skill_id: str) -> SkillAuthoringPack:
        skill = store.skills.get(skill_id)
        playbook = self._linked_playbook(store, skill)
        step_names = self._step_names(playbook)
        sample_task_names = list(skill.evaluation_policy.get("sample_task_names", []))
        checklist = sample_task_names or step_names[:6]
        risk_signals = self._risk_signals(skill, playbook, step_names)
        approval_mode = "manual_review" if risk_signals else "auto_execute"
        approval_targets = self._approval_targets(skill, step_names)
        notes = [
            f"Linked playbook: {playbook.name if playbook else 'n/a'}.",
            f"Detected {len(step_names)} step(s) and {len(skill.required_mcp_servers)} MCP server(s).",
        ]
        if risk_signals:
            notes.append("Risk signals detected; keep a human gate before external or irreversible actions.")
        else:
            notes.append("No high-risk signals detected; a lighter approval policy is acceptable.")

        pack = SkillAuthoringPack(
            skill_id=skill.id,
            skill_name=skill.name,
            playbook_id=playbook.id if playbook else None,
            playbook_name=playbook.name if playbook else None,
            recommended_input_schema={
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "Goal title or objective for this execution."},
                    "task": {"type": "string", "description": "Task summary assigned to the skill."},
                    "context": {"type": "object", "description": "Structured task, playbook, and runtime context."},
                    "knowledge_items": {"type": "array", "description": "Optional linked knowledge snippets."},
                },
                "required": ["goal", "task", "context"],
            },
            recommended_output_schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Human-readable result summary."},
                    "outcome": {"type": "string", "description": "Final outcome or state transition."},
                    "artifacts": {"type": "array", "description": "Produced artifacts or URIs."},
                    "follow_ups": {"type": "array", "description": "Suggested next actions."},
                    "blockers": {"type": "array", "description": "Blockers or unmet requirements."},
                },
                "required": ["summary", "outcome"],
            },
            recommended_approval_policy={
                "mode": approval_mode,
                "requires_human_for": approval_targets,
                "reason": "; ".join(risk_signals) if risk_signals else "No high-risk side effects detected from the linked playbook.",
            },
            recommended_evaluation_policy={
                **skill.evaluation_policy,
                "source": "authoring_wizard",
                "playbook_id": playbook.id if playbook else skill.evaluation_policy.get("playbook_id"),
                "checklist": checklist,
                "success_signals": [
                    "Output matches declared schema",
                    "SOP steps are covered or explicitly skipped with rationale",
                    "External side effects are called out clearly",
                ],
            },
            checklist=checklist,
            risk_signals=risk_signals,
            notes=notes,
            linked_step_names=step_names,
        )
        return pack

    def apply_pack(self, store: StoreProtocol, skill_id: str) -> SkillAuthoringApplyResult:
        skill = store.skills.get(skill_id)
        pack = self.build_pack(store, skill_id)
        applied_fields: list[str] = []

        merged_input = self._merge_schema(pack.recommended_input_schema, skill.input_schema)
        if merged_input != skill.input_schema:
            skill.input_schema = merged_input
            applied_fields.append("input_schema")

        merged_output = self._merge_schema(pack.recommended_output_schema, skill.output_schema)
        if merged_output != skill.output_schema:
            skill.output_schema = merged_output
            applied_fields.append("output_schema")

        merged_approval = {**pack.recommended_approval_policy, **dict(skill.approval_policy)}
        if merged_approval != skill.approval_policy:
            skill.approval_policy = merged_approval
            applied_fields.append("approval_policy")

        merged_evaluation = {**pack.recommended_evaluation_policy, **dict(skill.evaluation_policy)}
        if merged_evaluation != skill.evaluation_policy:
            skill.evaluation_policy = merged_evaluation
            applied_fields.append("evaluation_policy")

        if applied_fields:
            skill.updated_at = utc_now()
            store.skills.save(skill)
            append_event(
                store,
                entity_type="skill",
                entity_id=skill.id,
                event_type="skill.authoring_pack_applied",
                payload={
                    "playbook_id": pack.playbook_id,
                    "applied_fields": applied_fields,
                },
                source="human",
            )

        return SkillAuthoringApplyResult(skill=skill, authoring_pack=pack, applied_fields=applied_fields)

    def _linked_playbook(self, store: StoreProtocol, skill: Skill) -> Playbook | None:
        playbook_id = skill.evaluation_policy.get("playbook_id")
        if playbook_id:
            try:
                return store.playbooks.get(playbook_id)
            except Exception:
                return None
        linked_task = next((item for item in store.tasks.list() if item.assigned_skill_id == skill.id), None)
        if linked_task is None:
            return None
        try:
            return store.playbooks.get(linked_task.playbook_id)
        except Exception:
            return None

    def _step_names(self, playbook: Playbook | None) -> list[str]:
        if playbook is None:
            return []
        step_names: list[str] = []
        for step in list(playbook.compiled_spec.get("steps", [])):
            if isinstance(step, dict):
                name = str(step.get("name") or step.get("title") or step.get("description") or "").strip()
            else:
                name = str(step or "").strip()
            if name:
                step_names.append(name)
        return step_names

    def _risk_signals(self, skill: Skill, playbook: Playbook | None, step_names: list[str]) -> list[str]:
        signals: list[str] = []
        joined = " ".join(step_names).lower()
        if any(keyword in joined for keyword in ["publish", "deploy", "notify", "email", "send", "delete", "rollback"]):
            signals.append("Linked SOP contains external or irreversible actions")
        if any(server in {"github", "slack", "email", "jira"} for server in skill.required_mcp_servers):
            signals.append("Skill requests write-capable MCP integrations")
        if playbook and any(isinstance(step, dict) and (step.get("approval_required") or step.get("requires_approval")) for step in playbook.compiled_spec.get("steps", [])):
            signals.append("Playbook already declares approval gates in its steps")
        return signals

    def _approval_targets(self, skill: Skill, step_names: list[str]) -> list[str]:
        targets = []
        if any(server in {"email", "slack"} for server in skill.required_mcp_servers):
            targets.append("outbound_communications")
        if any(server in {"github", "jira"} for server in skill.required_mcp_servers):
            targets.append("system_mutations")
        if any("publish" in step.lower() or "deploy" in step.lower() for step in step_names):
            targets.append("publication_or_release")
        return list(dict.fromkeys(targets)) or ["manual_review"]

    def _merge_schema(self, recommended: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
        current = dict(current or {})
        if not current:
            return dict(recommended)
        merged = {**recommended, **current}
        if isinstance(recommended.get("properties"), dict) or isinstance(current.get("properties"), dict):
            merged["properties"] = {**dict(recommended.get("properties", {})), **dict(current.get("properties", {}))}
        if recommended.get("required") or current.get("required"):
            merged["required"] = list(dict.fromkeys([*list(recommended.get("required", [])), *list(current.get("required", []))]))
        return merged


def build_skill_authoring_pack_in_store(store: StoreProtocol, skill_id: str) -> SkillAuthoringPack:
    return SkillAuthoringWizard().build_pack(store, skill_id)


def apply_skill_authoring_pack_in_store(store: StoreProtocol, skill_id: str) -> SkillAuthoringApplyResult:
    return SkillAuthoringWizard().apply_pack(store, skill_id)
