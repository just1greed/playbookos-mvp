import unittest

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Goal, KnowledgeBase, KnowledgeUpdateStatus, Playbook
from playbookos.executor.service import DeterministicExecutorAdapter, execute_run_in_store
from playbookos.knowledge import apply_knowledge_update_in_store, reject_knowledge_update_in_store
from playbookos.orchestrator.service import dispatch_goal_in_store
from playbookos.planner.service import plan_goal_in_store
from playbookos.reflection.service import reflect_run_in_store


class KnowledgeUpdateFlowTestCase(unittest.TestCase):
    def test_reflection_creates_knowledge_update_for_linked_knowledge(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Knowledge loop", objective="Learn into reusable memory"))
        knowledge = store.knowledge_bases.save(
            KnowledgeBase(
                goal_id=goal.id,
                name="Execution notes",
                description="Reusable notes",
                content="Initial context",
            )
        )
        playbook = store.playbooks.save(
            Playbook(
                name="Knowledge playbook",
                source_kind="markdown",
                source_uri="file:///tmp/knowledge.md",
                goal_id=goal.id,
                compiled_spec={
                    "steps": [
                        {"name": "Use context", "knowledge_base_ids": [knowledge.id]},
                    ]
                },
            )
        )

        plan_goal_in_store(store, goal.id)
        task = store.tasks.list()[0]
        self.assertEqual(task.knowledge_base_ids, [knowledge.id])

        dispatch = dispatch_goal_in_store(store, goal.id)
        run_id = dispatch.created_run_ids[0]
        result = execute_run_in_store(store, run_id, adapter=DeterministicExecutorAdapter())
        reflection = reflect_run_in_store(store, run_id)
        knowledge_update = store.knowledge_updates.list()[0]

        self.assertEqual(result.metrics["knowledge_item_count"], 1)
        self.assertIsNotNone(reflection.knowledge_update_id)
        self.assertEqual(knowledge_update.knowledge_base_id, knowledge.id)
        self.assertEqual(knowledge_update.source_reflection_id, reflection.reflection.id)
        self.assertEqual(knowledge_update.status, KnowledgeUpdateStatus.PROPOSED)

    def test_apply_and_reject_knowledge_update(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Apply knowledge", objective="Persist learning"))
        store.playbooks.save(
            Playbook(
                name="Apply playbook",
                source_kind="markdown",
                source_uri="file:///tmp/apply.md",
                goal_id=goal.id,
                compiled_spec={"steps": ["Collect lesson"]},
            )
        )

        plan_goal_in_store(store, goal.id)
        dispatch = dispatch_goal_in_store(store, goal.id)
        run_id = dispatch.created_run_ids[0]
        execute_run_in_store(store, run_id, adapter=DeterministicExecutorAdapter())
        reflect_run_in_store(store, run_id)
        knowledge_update = store.knowledge_updates.list()[0]

        applied = apply_knowledge_update_in_store(store, knowledge_update.id, applied_by="reviewer-1")
        self.assertEqual(applied.knowledge_update.status, KnowledgeUpdateStatus.APPLIED)
        self.assertEqual(applied.knowledge_base.status.value, "active")

        rejected_update = store.knowledge_updates.save(
            type(knowledge_update)(
                goal_id=knowledge_update.goal_id,
                task_id=knowledge_update.task_id,
                run_id=knowledge_update.run_id,
                title="Reject me",
                summary="Rejected proposal",
                proposed_content="Do not keep this content",
            )
        )
        rejected = reject_knowledge_update_in_store(store, rejected_update.id, rejected_by="reviewer-2")
        self.assertEqual(rejected.status, KnowledgeUpdateStatus.REJECTED)


if __name__ == "__main__":
    unittest.main()
