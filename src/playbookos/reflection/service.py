from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from playbookos.api.store import StoreProtocol
from playbookos.domain.models import KnowledgeUpdate, Playbook, PlaybookStatus, Reflection, ReflectionStatus, RunStatus, utc_now
from playbookos.knowledge import sync_knowledge_update_for_run
from playbookos.supervisor import append_event, ensure_worker_session_for_run, record_child_session, refresh_goal_supervisor_session


class ReflectionError(ValueError):
    pass


@dataclass(slots=True)
class RunReflectionResult:
    reflection: Reflection
    proposal_type: str
    target: str
    knowledge_update_id: str | None = None


@dataclass(slots=True)
class ReflectionEvaluationResult:
    reflection: Reflection
    passed: bool
    score: float
    replay_run_ids: list[str]


@dataclass(slots=True)
class ReflectionPublishResult:
    reflection: Reflection
    playbook: Playbook


@dataclass(slots=True)
class LearningSummary:
    goal_id: str
    run_count: int
    failed_run_count: int
    reflection_ids: list[str] = field(default_factory=list)
    knowledge_update_ids: list[str] = field(default_factory=list)
    failure_categories: dict[str, int] = field(default_factory=dict)
    suggested_playbook_patches: list[dict[str, Any]] = field(default_factory=list)
    suggested_knowledge_updates: list[dict[str, Any]] = field(default_factory=list)


class SOPReflector:
    def reflect_run(self, store: StoreProtocol, run_id: str) -> RunReflectionResult:
        existing = next((item for item in store.reflections.list() if item.run_id == run_id), None)
        if existing is not None:
            existing_knowledge_update = next((item for item in store.knowledge_updates.list() if item.run_id == run_id), None)
            refresh_goal_supervisor_session(store, store.tasks.get(store.runs.get(run_id).task_id).goal_id)
            return RunReflectionResult(
                reflection=existing,
                proposal_type=existing.proposal.get("proposal_type", "unknown"),
                target=existing.proposal.get("target", "unknown"),
                knowledge_update_id=existing_knowledge_update.id if existing_knowledge_update is not None else None,
            )

        run = store.runs.get(run_id)
        task = store.tasks.get(run.task_id)
        playbook = store.playbooks.get(task.playbook_id)

        failure_category = self._failure_category(run, task)
        proposal = self._proposal_for_run(run, task, playbook)
        reflection = Reflection(
            run_id=run.id,
            failure_category=failure_category,
            summary=proposal["summary"],
            proposal=proposal,
            eval_status=ReflectionStatus.PROPOSED,
            approval_status="pending",
        )
        store.reflections.save(reflection)
        knowledge_update = sync_knowledge_update_for_run(store, run.id, source_reflection_id=reflection.id)
        worker_session = ensure_worker_session_for_run(store, run.id)
        record_child_session(
            store,
            goal_id=task.goal_id,
            parent_session_id=worker_session.id,
            title="Subsession · Reflection and learning",
            task_id=task.id,
            run_id=run.id,
            objective="Review execution outcome and produce SOP / knowledge improvements",
            input_context={
                "failure_category": failure_category,
                "proposal_type": proposal["proposal_type"],
                "target": proposal["target"],
            },
            output_context={
                "reflection_id": reflection.id,
                "knowledge_update_id": knowledge_update.id,
                "changes": proposal.get("changes", []),
            },
            summary=proposal["summary"],
        )
        append_event(
            store,
            entity_type="reflection",
            entity_id=reflection.id,
            event_type="reflection.created",
            payload={"goal_id": task.goal_id, "task_id": task.id, "run_id": run.id, "knowledge_update_id": knowledge_update.id},
        )
        refresh_goal_supervisor_session(store, task.goal_id)
        return RunReflectionResult(
            reflection=reflection,
            proposal_type=proposal["proposal_type"],
            target=proposal["target"],
            knowledge_update_id=knowledge_update.id,
        )

    def evaluate_reflection(self, store: StoreProtocol, reflection_id: str) -> ReflectionEvaluationResult:
        reflection = store.reflections.get(reflection_id)
        run = store.runs.get(reflection.run_id)
        task = store.tasks.get(run.task_id)
        sibling_runs = [
            item for item in store.runs.list() if store.tasks.get(item.task_id).playbook_id == task.playbook_id
        ]
        replay_run_ids = [item.id for item in sibling_runs]
        changes = reflection.proposal.get("changes", [])

        candidate_count = len(replay_run_ids)
        change_count = len(changes)
        passed = candidate_count >= 1 and change_count >= 1
        score = min(1.0, 0.4 + candidate_count * 0.15 + change_count * 0.1)
        reflection.eval_status = ReflectionStatus.APPROVED if passed else ReflectionStatus.REJECTED
        reflection.updated_at = utc_now()
        reflection.proposal["evaluation"] = {
            "replay_run_ids": replay_run_ids,
            "candidate_count": candidate_count,
            "change_count": change_count,
            "score": score,
            "passed": passed,
        }
        store.reflections.save(reflection)
        append_event(
            store,
            entity_type="reflection",
            entity_id=reflection.id,
            event_type="reflection.evaluated",
            payload={"run_id": run.id, "task_id": task.id, "goal_id": task.goal_id, "passed": passed, "score": score},
            source="system",
        )
        refresh_goal_supervisor_session(store, task.goal_id)
        return ReflectionEvaluationResult(
            reflection=reflection,
            passed=passed,
            score=score,
            replay_run_ids=replay_run_ids,
        )

    def approve_reflection(self, store: StoreProtocol, reflection_id: str, *, approved_by: str = "human") -> Reflection:
        reflection = store.reflections.get(reflection_id)
        if reflection.eval_status != ReflectionStatus.APPROVED:
            raise ReflectionError("Reflection must pass evaluation before approval")
        reflection.approval_status = "approved"
        reflection.approved_by = approved_by
        reflection.updated_at = utc_now()
        store.reflections.save(reflection)
        run = store.runs.get(reflection.run_id)
        task = store.tasks.get(run.task_id)
        append_event(
            store,
            entity_type="reflection",
            entity_id=reflection.id,
            event_type="reflection.approved",
            payload={"goal_id": task.goal_id, "task_id": task.id, "run_id": run.id},
            source=approved_by,
        )
        refresh_goal_supervisor_session(store, task.goal_id)
        return reflection

    def reject_reflection(self, store: StoreProtocol, reflection_id: str, *, approved_by: str = "human") -> Reflection:
        reflection = store.reflections.get(reflection_id)
        reflection.approval_status = "rejected"
        reflection.approved_by = approved_by
        reflection.updated_at = utc_now()
        store.reflections.save(reflection)
        run = store.runs.get(reflection.run_id)
        task = store.tasks.get(run.task_id)
        append_event(
            store,
            entity_type="reflection",
            entity_id=reflection.id,
            event_type="reflection.rejected",
            payload={"goal_id": task.goal_id, "task_id": task.id, "run_id": run.id},
            source=approved_by,
        )
        refresh_goal_supervisor_session(store, task.goal_id)
        return reflection

    def publish_reflection(self, store: StoreProtocol, reflection_id: str) -> ReflectionPublishResult:
        reflection = store.reflections.get(reflection_id)
        if reflection.eval_status != ReflectionStatus.APPROVED:
            raise ReflectionError("Reflection must be evaluation-approved before publish")
        if reflection.approval_status != "approved":
            raise ReflectionError("Reflection must be human-approved before publish")

        run = store.runs.get(reflection.run_id)
        task = store.tasks.get(run.task_id)
        playbook = store.playbooks.get(task.playbook_id)

        published_playbook = self._publish_new_playbook_version(store, playbook, reflection)
        reflection.eval_status = ReflectionStatus.PUBLISHED
        reflection.published_target_version = published_playbook.version
        reflection.proposal["published_playbook_id"] = published_playbook.id
        reflection.updated_at = utc_now()
        store.reflections.save(reflection)
        append_event(
            store,
            entity_type="reflection",
            entity_id=reflection.id,
            event_type="reflection.published",
            payload={"goal_id": task.goal_id, "task_id": task.id, "run_id": run.id, "playbook_id": published_playbook.id, "version": published_playbook.version},
            source="human",
        )
        refresh_goal_supervisor_session(store, task.goal_id)
        return ReflectionPublishResult(reflection=reflection, playbook=published_playbook)

    def analyze_goal(self, store: StoreProtocol, goal_id: str) -> LearningSummary:
        tasks = [task for task in store.tasks.list() if task.goal_id == goal_id]
        task_ids = {task.id for task in tasks}
        runs = [run for run in store.runs.list() if run.task_id in task_ids]
        run_ids = {run.id for run in runs}
        reflections = [reflection for reflection in store.reflections.list() if reflection.run_id in run_ids]
        knowledge_updates = [item for item in store.knowledge_updates.list() if item.run_id in run_ids]
        failure_categories = Counter(reflection.failure_category for reflection in reflections)

        suggested_playbook_patches: list[dict[str, Any]] = []
        for reflection in reflections:
            if reflection.proposal.get("proposal_type") == "sop_patch":
                suggested_playbook_patches.append(reflection.proposal)

        suggested_knowledge_updates = [
            {
                "id": item.id,
                "title": item.title,
                "summary": item.summary,
                "status": item.status.value,
                "knowledge_base_id": item.knowledge_base_id,
            }
            for item in knowledge_updates
        ]

        return LearningSummary(
            goal_id=goal_id,
            run_count=len(runs),
            failed_run_count=sum(1 for run in runs if run.status == RunStatus.FAILED),
            reflection_ids=[reflection.id for reflection in reflections],
            knowledge_update_ids=[item.id for item in knowledge_updates],
            failure_categories=dict(failure_categories),
            suggested_playbook_patches=suggested_playbook_patches,
            suggested_knowledge_updates=suggested_knowledge_updates,
        )

    def _failure_category(self, run, task) -> str:
        if run.status == RunStatus.SUCCEEDED:
            return "success-pattern"
        if task.approval_required or run.status == RunStatus.WAITING_HUMAN:
            return "approval-bottleneck"
        if run.error_class:
            return run.error_class
        return "execution-variance"

    def _proposal_for_run(self, run, task, playbook) -> dict[str, Any]:
        steps = playbook.compiled_spec.get("steps", [])
        if run.status == RunStatus.SUCCEEDED:
            return {
                "proposal_type": "sop_patch",
                "target": "playbook",
                "summary": f"Promote successful pattern from task '{task.name}' into SOP preflight and reusable templates.",
                "changes": [
                    {"op": "prepend_step", "description": f"Add preflight checklist before '{task.name}'"},
                    {"op": "capture_template", "description": "Persist successful inputs/outputs as reusable task template"},
                ],
                "source_run_id": run.id,
                "playbook_id": playbook.id,
                "step_count": len(steps),
            }

        if task.approval_required or run.status == RunStatus.WAITING_HUMAN:
            return {
                "proposal_type": "sop_patch",
                "target": "playbook",
                "summary": f"Reduce approval bottlenecks around '{task.name}' with clearer MCP scope and decision rules.",
                "changes": [
                    {"op": "insert_step", "description": "Add approval rubric and MCP permission checklist before sensitive action"},
                    {"op": "add_guardrail", "description": "Split read-only and write actions into separate SOP branches"},
                ],
                "source_run_id": run.id,
                "playbook_id": playbook.id,
                "step_count": len(steps),
            }

        return {
            "proposal_type": "sop_patch",
            "target": "playbook",
            "summary": f"Improve reliability of '{task.name}' by adding retries, validation, and richer context capture.",
            "changes": [
                {"op": "insert_step", "description": "Add pre-execution validation for MCP inputs and task prerequisites"},
                {"op": "append_step", "description": "Add retry and fallback branch for transient tool failures"},
                {"op": "capture_signal", "description": "Record task inputs, outputs, and trace for replay evaluation"},
            ],
            "source_run_id": run.id,
            "playbook_id": playbook.id,
            "step_count": len(steps),
        }

    def _publish_new_playbook_version(self, store: StoreProtocol, playbook: Playbook, reflection: Reflection) -> Playbook:
        current = playbook
        current.status = PlaybookStatus.DEPRECATED
        current.updated_at = utc_now()
        store.playbooks.save(current)

        published_spec = self._apply_changes(current.compiled_spec, reflection.proposal.get("changes", []), reflection.id)
        published_playbook = Playbook(
            goal_id=current.goal_id,
            name=current.name,
            source_kind=current.source_kind,
            source_uri=current.source_uri,
            compiled_spec=published_spec,
            version=_increment_version(current.version),
            status=PlaybookStatus.ACTIVE,
        )
        store.playbooks.save(published_playbook)
        return published_playbook

    def _apply_changes(self, compiled_spec: dict[str, Any], changes: list[dict[str, Any]], reflection_id: str) -> dict[str, Any]:
        updated = {**compiled_spec}
        steps = list(updated.get("steps", []))
        guardrails = list(updated.get("guardrails", []))
        templates = list(updated.get("templates", []))
        signals = list(updated.get("signals", []))
        patch_history = list(updated.get("patch_history", []))

        for change in changes:
            op = change.get("op")
            description = change.get("description", "Generated patch")
            generated_step = {
                "name": description,
                "description": description,
                "generated_by_reflection": reflection_id,
            }
            if op == "prepend_step":
                steps.insert(0, generated_step)
            elif op == "append_step":
                steps.append(generated_step)
            elif op == "insert_step":
                insert_at = 1 if steps else 0
                steps.insert(insert_at, generated_step)
            elif op == "add_guardrail":
                guardrails.append({"description": description, "generated_by_reflection": reflection_id})
            elif op == "capture_template":
                templates.append({"description": description, "generated_by_reflection": reflection_id})
            elif op == "capture_signal":
                signals.append({"description": description, "generated_by_reflection": reflection_id})
            patch_history.append({"reflection_id": reflection_id, **change})

        updated["steps"] = steps
        if guardrails:
            updated["guardrails"] = guardrails
        if templates:
            updated["templates"] = templates
        if signals:
            updated["signals"] = signals
        updated["patch_history"] = patch_history
        return updated



def _increment_version(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return f"{version}.1"
    major, minor, patch = (int(part) for part in parts)
    return f"{major}.{minor}.{patch + 1}"



def reflect_run_in_store(store: StoreProtocol, run_id: str) -> RunReflectionResult:
    return SOPReflector().reflect_run(store, run_id)



def evaluate_reflection_in_store(store: StoreProtocol, reflection_id: str) -> ReflectionEvaluationResult:
    return SOPReflector().evaluate_reflection(store, reflection_id)



def approve_reflection_in_store(store: StoreProtocol, reflection_id: str, *, approved_by: str = "human") -> Reflection:
    return SOPReflector().approve_reflection(store, reflection_id, approved_by=approved_by)



def reject_reflection_in_store(store: StoreProtocol, reflection_id: str, *, approved_by: str = "human") -> Reflection:
    return SOPReflector().reject_reflection(store, reflection_id, approved_by=approved_by)



def publish_reflection_in_store(store: StoreProtocol, reflection_id: str) -> ReflectionPublishResult:
    return SOPReflector().publish_reflection(store, reflection_id)



def analyze_goal_learning(store: StoreProtocol, goal_id: str) -> LearningSummary:
    return SOPReflector().analyze_goal(store, goal_id)
