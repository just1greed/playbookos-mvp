from __future__ import annotations

from dataclasses import dataclass

from playbookos.api.store import StoreProtocol
from playbookos.domain.models import KnowledgeBase, KnowledgeStatus, KnowledgeUpdate, KnowledgeUpdateStatus, utc_now


class KnowledgeUpdateError(ValueError):
    pass


@dataclass(slots=True)
class KnowledgeUpdateApplyResult:
    knowledge_update: KnowledgeUpdate
    knowledge_base: KnowledgeBase


class KnowledgeUpdater:
    def sync_for_run(self, store: StoreProtocol, run_id: str, *, source_reflection_id: str | None = None) -> KnowledgeUpdate:
        existing = next((item for item in store.knowledge_updates.list() if item.run_id == run_id), None)
        if existing is not None:
            return existing

        run = store.runs.get(run_id)
        task = store.tasks.get(run.task_id)
        goal = store.goals.get(task.goal_id)
        playbook = store.playbooks.get(task.playbook_id)
        linked_knowledge = [store.knowledge_bases.get(item_id) for item_id in task.knowledge_base_ids if item_id]
        primary_knowledge = linked_knowledge[0] if linked_knowledge else next((item for item in store.knowledge_bases.list() if item.goal_id == goal.id), None)
        output_text = str(run.metrics.get("output_text", "")).strip() or f"Outcome for task '{task.name}'"
        summary = (
            f"Capture reusable knowledge from task '{task.name}' and goal '{goal.title}' so similar work can reuse validated context."
        )
        if primary_knowledge is not None:
            title = f"Update knowledge · {primary_knowledge.name}"
            proposed_content = (
                f"{primary_knowledge.content}\n\n---\nRun insight from {task.name}:\n{output_text}\n\n"
                f"Recommended SOP context:\n- Playbook: {playbook.name}\n- Goal: {goal.title}\n- Trace: {run.trace_id or 'n/a'}"
            ).strip()
        else:
            title = f"Create knowledge · {task.name}"
            proposed_content = (
                f"Goal: {goal.title}\nTask: {task.name}\nPlaybook: {playbook.name}\n\n"
                f"Reusable knowledge extracted from execution:\n{output_text}\n\n"
                "Suggested usage:\n- Reuse for similar tasks\n- Feed future planning and review loops"
            ).strip()

        item = KnowledgeUpdate(
            goal_id=goal.id,
            task_id=task.id,
            run_id=run.id,
            knowledge_base_id=primary_knowledge.id if primary_knowledge is not None else None,
            source_reflection_id=source_reflection_id,
            title=title,
            summary=summary,
            proposed_content=proposed_content,
            rationale="Generated from run trace, linked knowledge context, and reflection-ready execution summary.",
        )
        store.knowledge_updates.save(item)
        return item

    def apply(self, store: StoreProtocol, knowledge_update_id: str, *, applied_by: str = "human") -> KnowledgeUpdateApplyResult:
        item = store.knowledge_updates.get(knowledge_update_id)
        if item.status == KnowledgeUpdateStatus.REJECTED:
            raise KnowledgeUpdateError("Rejected knowledge update cannot be applied")

        if item.knowledge_base_id is not None:
            knowledge_base = store.knowledge_bases.get(item.knowledge_base_id)
            knowledge_base.content = item.proposed_content
            knowledge_base.status = KnowledgeStatus.ACTIVE
            knowledge_base.updated_at = utc_now()
        else:
            task = store.tasks.get(item.task_id)
            knowledge_base = KnowledgeBase(
                goal_id=item.goal_id,
                name=item.title.replace("Create knowledge · ", "").replace("Update knowledge · ", ""),
                description=item.summary,
                content=item.proposed_content,
                source_uri=f"playbookos://knowledge-updates/{item.id}",
                status=KnowledgeStatus.ACTIVE,
            )
            store.knowledge_bases.save(knowledge_base)
            task.knowledge_base_ids = list(dict.fromkeys([*task.knowledge_base_ids, knowledge_base.id]))
            task.updated_at = utc_now()
            store.tasks.save(task)
            item.knowledge_base_id = knowledge_base.id

        store.knowledge_bases.save(knowledge_base)
        item.status = KnowledgeUpdateStatus.APPLIED
        item.applied_by = applied_by
        item.updated_at = utc_now()
        store.knowledge_updates.save(item)
        return KnowledgeUpdateApplyResult(knowledge_update=item, knowledge_base=knowledge_base)

    def reject(self, store: StoreProtocol, knowledge_update_id: str, *, rejected_by: str = "human") -> KnowledgeUpdate:
        item = store.knowledge_updates.get(knowledge_update_id)
        item.status = KnowledgeUpdateStatus.REJECTED
        item.applied_by = rejected_by
        item.updated_at = utc_now()
        store.knowledge_updates.save(item)
        return item


def sync_knowledge_update_for_run(store: StoreProtocol, run_id: str, *, source_reflection_id: str | None = None) -> KnowledgeUpdate:
    return KnowledgeUpdater().sync_for_run(store, run_id, source_reflection_id=source_reflection_id)


def apply_knowledge_update_in_store(store: StoreProtocol, knowledge_update_id: str, *, applied_by: str = "human") -> KnowledgeUpdateApplyResult:
    return KnowledgeUpdater().apply(store, knowledge_update_id, applied_by=applied_by)


def reject_knowledge_update_in_store(store: StoreProtocol, knowledge_update_id: str, *, rejected_by: str = "human") -> KnowledgeUpdate:
    return KnowledgeUpdater().reject(store, knowledge_update_id, rejected_by=rejected_by)
