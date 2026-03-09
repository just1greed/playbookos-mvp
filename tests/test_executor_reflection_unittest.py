import unittest

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Goal, GoalStatus, Playbook, RunStatus, TaskStatus
from playbookos.executor.service import DeterministicExecutorAdapter, autopilot_goal_in_store, execute_run_in_store
from playbookos.orchestrator.service import dispatch_goal_in_store
from playbookos.planner.service import plan_goal_in_store
from playbookos.reflection.service import analyze_goal_learning, reflect_run_in_store


class ExecutorReflectionTestCase(unittest.TestCase):
    def test_execute_run_generates_trace_and_marks_review(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Execute goal", objective="Run executor"))
        store.playbooks.save(
            Playbook(
                name="Execution playbook",
                source_kind="markdown",
                source_uri="file:///tmp/executor.md",
                goal_id=goal.id,
                compiled_spec={"steps": ["Step 1"], "mcp_servers": ["plane", "github"]},
            )
        )

        plan_goal_in_store(store, goal.id)
        dispatch = dispatch_goal_in_store(store, goal.id)
        run_id = dispatch.created_run_ids[0]
        result = execute_run_in_store(store, run_id, adapter=DeterministicExecutorAdapter())
        task = store.tasks.get(store.runs.get(run_id).task_id)
        artifact = store.artifacts.get(result.artifact_ids[0])

        self.assertEqual(result.status, RunStatus.SUCCEEDED)
        self.assertTrue(result.trace_id)
        self.assertEqual(len(result.artifact_ids), 1)
        self.assertEqual(artifact.run_id, run_id)
        self.assertEqual(artifact.kind, "run_report")
        self.assertEqual(artifact.metadata["run_status"], RunStatus.SUCCEEDED.value)
        self.assertEqual(task.status, TaskStatus.REVIEW)

    def test_reflect_run_creates_sop_patch_proposal(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Reflect goal", objective="Learn from success"))
        store.playbooks.save(
            Playbook(
                name="Reflection playbook",
                source_kind="markdown",
                source_uri="file:///tmp/reflection.md",
                goal_id=goal.id,
                compiled_spec={"steps": ["Step 1"]},
            )
        )

        plan_goal_in_store(store, goal.id)
        dispatch = dispatch_goal_in_store(store, goal.id)
        run_id = dispatch.created_run_ids[0]
        execute_run_in_store(store, run_id, adapter=DeterministicExecutorAdapter())
        reflection = reflect_run_in_store(store, run_id)

        self.assertEqual(reflection.proposal_type, "sop_patch")
        self.assertEqual(reflection.target, "playbook")
        self.assertIn("changes", reflection.reflection.proposal)
        self.assertIsNotNone(reflection.knowledge_update_id)

    def test_autopilot_drives_similar_tasks_and_learning_summary(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Batch goal", objective="Run many similar tasks"))
        store.playbooks.save(
            Playbook(
                name="Batch playbook",
                source_kind="markdown",
                source_uri="file:///tmp/batch.md",
                goal_id=goal.id,
                compiled_spec={
                    "steps": [
                        "Prepare context",
                        "Execute standard action",
                        {"name": "Manager approval", "depends_on": ["Execute standard action"], "requires_approval": True},
                    ],
                    "mcp_servers": ["plane", "slack", "github"],
                },
            )
        )

        plan_goal_in_store(store, goal.id)
        result = autopilot_goal_in_store(store, goal.id, adapter=DeterministicExecutorAdapter())
        learning = analyze_goal_learning(store, goal.id)

        self.assertGreaterEqual(len(result.executed_run_ids), 2)
        self.assertGreaterEqual(len(result.reflection_ids), 2)
        self.assertEqual(store.goals.get(goal.id).status, GoalStatus.BLOCKED)
        self.assertGreaterEqual(learning.run_count, 3)
        self.assertGreaterEqual(len(learning.suggested_playbook_patches), 2)
        self.assertGreaterEqual(len(learning.knowledge_update_ids), 2)
        self.assertGreaterEqual(len(learning.suggested_knowledge_updates), 2)


if __name__ == "__main__":
    unittest.main()
