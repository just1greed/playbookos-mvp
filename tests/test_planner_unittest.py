import unittest

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Goal, GoalStatus, Playbook, TaskStatus
from playbookos.planner.service import PlanningError, PlaybookPlanner, plan_goal_in_store


class PlannerTestCase(unittest.TestCase):
    def test_planner_builds_task_dag_from_compiled_steps(self) -> None:
        goal = Goal(title="Ship planner", objective="Generate a task DAG")
        playbook = Playbook(
            name="Planner demo",
            source_kind="markdown",
            source_uri="file:///tmp/planner.md",
            goal_id=goal.id,
            compiled_spec={
                "steps": [
                    {"name": "Collect context", "description": "Read SOP"},
                    {"name": "Draft plan", "description": "Write DAG", "depends_on": ["Collect context"]},
                    {"name": "Review", "description": "Human review", "depends_on": [1], "requires_approval": True},
                ]
            },
        )

        planner = PlaybookPlanner()
        result = planner.plan_goal(goal, [playbook])

        self.assertEqual(result.created_count, 3)
        self.assertEqual(result.created_tasks[0].status, TaskStatus.READY)
        self.assertEqual(result.created_tasks[1].depends_on, [result.created_tasks[0].id])
        self.assertEqual(result.created_tasks[2].depends_on, [result.created_tasks[1].id])
        self.assertTrue(result.created_tasks[2].approval_required)

    def test_plan_goal_in_store_is_idempotent(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Start goal", objective="Plan tasks once"))
        store.playbooks.save(
            Playbook(
                name="Execution",
                source_kind="markdown",
                source_uri="file:///tmp/execution.md",
                goal_id=goal.id,
                compiled_spec={"steps": ["Step 1", "Step 2"]},
            )
        )

        first_result = plan_goal_in_store(store, goal.id)
        second_result = plan_goal_in_store(store, goal.id)

        self.assertEqual(first_result.created_count, 2)
        self.assertEqual(second_result.created_count, 0)
        self.assertEqual(second_result.existing_task_count, 2)
        self.assertEqual(len([task for task in store.tasks.list() if task.goal_id == goal.id]), 2)
        self.assertEqual(store.goals.get(goal.id).status, GoalStatus.RUNNING)

    def test_planner_raises_for_unknown_dependency(self) -> None:
        goal = Goal(title="Broken planner", objective="Fail clearly")
        playbook = Playbook(
            name="Broken spec",
            source_kind="markdown",
            source_uri="file:///tmp/broken.md",
            goal_id=goal.id,
            compiled_spec={"steps": [{"name": "Second", "depends_on": ["Missing"]}]},
        )

        with self.assertRaises(PlanningError):
            PlaybookPlanner().plan_goal(goal, [playbook])


if __name__ == "__main__":
    unittest.main()
