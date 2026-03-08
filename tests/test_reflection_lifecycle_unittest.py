import tempfile
import unittest
from pathlib import Path

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Goal, Playbook, PlaybookStatus, ReflectionStatus
from playbookos.executor.service import DeterministicExecutorAdapter, execute_run_in_store
from playbookos.orchestrator.service import dispatch_goal_in_store
from playbookos.persistence.sqlite_store import SQLiteStore
from playbookos.planner.service import plan_goal_in_store
from playbookos.reflection.service import (
    approve_reflection_in_store,
    evaluate_reflection_in_store,
    publish_reflection_in_store,
    reflect_run_in_store,
)


class ReflectionLifecycleTestCase(unittest.TestCase):
    def test_evaluate_approve_publish_creates_new_playbook_version(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Lifecycle goal", objective="Upgrade SOP safely"))
        original_playbook = store.playbooks.save(
            Playbook(
                name="Lifecycle playbook",
                source_kind="markdown",
                source_uri="file:///tmp/lifecycle.md",
                goal_id=goal.id,
                version="0.1.0",
                compiled_spec={"steps": ["Collect", "Execute"], "mcp_servers": ["plane"]},
            )
        )

        plan_goal_in_store(store, goal.id)
        dispatch = dispatch_goal_in_store(store, goal.id)
        run_id = dispatch.created_run_ids[0]
        execute_run_in_store(store, run_id, adapter=DeterministicExecutorAdapter())
        reflection_result = reflect_run_in_store(store, run_id)
        evaluation = evaluate_reflection_in_store(store, reflection_result.reflection.id)
        approved = approve_reflection_in_store(store, reflection_result.reflection.id, approved_by="reviewer")
        publish_result = publish_reflection_in_store(store, reflection_result.reflection.id)

        self.assertTrue(evaluation.passed)
        self.assertEqual(approved.approval_status, "approved")
        self.assertEqual(publish_result.reflection.eval_status, ReflectionStatus.PUBLISHED)
        self.assertEqual(publish_result.playbook.version, "0.1.1")
        self.assertEqual(publish_result.playbook.status, PlaybookStatus.ACTIVE)
        self.assertEqual(store.playbooks.get(original_playbook.id).status, PlaybookStatus.DEPRECATED)
        self.assertGreater(len(publish_result.playbook.compiled_spec.get("patch_history", [])), 0)

    def test_sqlite_persists_published_target_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "playbookos.db"
            store = SQLiteStore(db_path)
            goal = store.goals.save(Goal(title="Persist reflection", objective="Keep published version"))
            store.playbooks.save(
                Playbook(
                    name="Persist playbook",
                    source_kind="markdown",
                    source_uri="file:///tmp/persist.md",
                    goal_id=goal.id,
                    version="1.0.0",
                    compiled_spec={"steps": ["Step 1"]},
                )
            )
            plan_goal_in_store(store, goal.id)
            dispatch = dispatch_goal_in_store(store, goal.id)
            run_id = dispatch.created_run_ids[0]
            execute_run_in_store(store, run_id, adapter=DeterministicExecutorAdapter())
            reflection = reflect_run_in_store(store, run_id)
            evaluate_reflection_in_store(store, reflection.reflection.id)
            approve_reflection_in_store(store, reflection.reflection.id)
            publish_reflection_in_store(store, reflection.reflection.id)

            second_store = SQLiteStore(db_path)
            persisted = second_store.reflections.get(reflection.reflection.id)
            self.assertEqual(persisted.published_target_version, "1.0.1")


if __name__ == "__main__":
    unittest.main()
