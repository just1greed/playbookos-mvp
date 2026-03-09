import unittest

from playbookos.api.store import InMemoryStore, NotFoundError
from playbookos.domain.models import Artifact, Goal, KnowledgeBase, Playbook, Reflection, Run, Skill, Task


class InMemoryStoreTestCase(unittest.TestCase):
    def test_board_snapshot_counts_entities(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Ship API", objective="Expose control plane endpoints"))
        playbook = store.playbooks.save(
            Playbook(name="Onboarding", source_kind="markdown", source_uri="file:///tmp/onboarding.md")
        )
        store.skills.save(
            Skill(name="Writer", description="Draft and edit SOP content", input_schema={}, output_schema={})
        )
        store.knowledge_bases.save(
            KnowledgeBase(name="Context pack", description="Reusable notes", content="Important context for execution")
        )
        task = store.tasks.save(
            Task(
                goal_id=goal.id,
                playbook_id=playbook.id,
                name="Create run",
                description="Prepare a runnable unit of work",
            )
        )
        run = store.runs.save(Run(task_id=task.id, worker_type="agents-sdk"))
        store.artifacts.save(
            Artifact(
                run_id=run.id,
                kind="run_report",
                title="Execution report",
                uri="playbookos://runs/demo/report.json",
                mime_type="application/json",
            )
        )
        store.reflections.save(
            Reflection(
                run_id=run.id,
                failure_category="missing-context",
                summary="Collect more preflight inputs",
                proposal={"action": "add checklist"},
            )
        )

        snapshot = store.board_snapshot()

        self.assertEqual(snapshot["goals"]["draft"], 1)
        self.assertEqual(snapshot["playbooks"]["draft"], 1)
        self.assertEqual(snapshot["skills"]["draft"], 1)
        self.assertEqual(snapshot["knowledge_bases"]["draft"], 1)
        self.assertEqual(snapshot["tasks"]["inbox"], 1)
        self.assertEqual(snapshot["runs"]["queued"], 1)
        self.assertEqual(snapshot["artifacts"]["run_report"], 1)
        self.assertEqual(snapshot["reflections"]["proposed"], 1)

    def test_missing_entity_raises_not_found(self) -> None:
        store = InMemoryStore()

        with self.assertRaises(NotFoundError):
            store.goals.get("missing")


if __name__ == "__main__":
    unittest.main()
