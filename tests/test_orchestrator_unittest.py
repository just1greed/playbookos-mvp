import unittest

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Goal, GoalStatus, Playbook, RunStatus, TaskStatus
from playbookos.orchestrator.service import complete_task_in_store, dispatch_goal_in_store
from playbookos.planner.service import plan_goal_in_store


class OrchestratorTestCase(unittest.TestCase):
    def test_dispatch_creates_run_for_ready_task(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Dispatch goal", objective="Queue work"))
        store.playbooks.save(
            Playbook(
                name="Dispatch playbook",
                source_kind="markdown",
                source_uri="file:///tmp/dispatch.md",
                goal_id=goal.id,
                compiled_spec={"steps": ["Step 1", "Step 2"]},
            )
        )

        plan_goal_in_store(store, goal.id)
        dispatch_result = dispatch_goal_in_store(store, goal.id)

        self.assertEqual(len(dispatch_result.created_run_ids), 1)
        first_task = sorted(store.tasks.list(), key=lambda item: item.priority)[0]
        first_run = store.runs.get(dispatch_result.created_run_ids[0])
        self.assertEqual(first_task.status, TaskStatus.RUNNING)
        self.assertEqual(first_run.status, RunStatus.QUEUED)
        self.assertEqual(dispatch_result.goal_status, GoalStatus.RUNNING)

    def test_complete_task_promotes_and_dispatches_next_task(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Advance goal", objective="Unlock downstream work"))
        store.playbooks.save(
            Playbook(
                name="Advance playbook",
                source_kind="markdown",
                source_uri="file:///tmp/advance.md",
                goal_id=goal.id,
                compiled_spec={"steps": ["Collect", "Execute"]},
            )
        )

        plan_goal_in_store(store, goal.id)
        dispatch_goal_in_store(store, goal.id)
        first_task = sorted(store.tasks.list(), key=lambda item: item.priority)[0]

        completion = complete_task_in_store(store, first_task.id)
        second_task = sorted(store.tasks.list(), key=lambda item: item.priority)[1]

        self.assertEqual(second_task.status, TaskStatus.RUNNING)
        self.assertEqual(len(completion.created_run_ids), 1)
        self.assertEqual(completion.goal_status, GoalStatus.RUNNING)

    def test_waiting_human_and_review_transitions(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Review goal", objective="Require approval then finish"))
        store.playbooks.save(
            Playbook(
                name="Approval playbook",
                source_kind="markdown",
                source_uri="file:///tmp/approval.md",
                goal_id=goal.id,
                compiled_spec={
                    "steps": [
                        "Prepare",
                        {"name": "Approve", "depends_on": ["Prepare"], "requires_approval": True},
                    ]
                },
            )
        )

        plan_goal_in_store(store, goal.id)
        dispatch_goal_in_store(store, goal.id)
        first_task = sorted(store.tasks.list(), key=lambda item: item.priority)[0]
        complete_task_in_store(store, first_task.id)
        second_task = sorted(store.tasks.list(), key=lambda item: item.priority)[1]

        self.assertEqual(second_task.status, TaskStatus.WAITING_HUMAN)
        self.assertEqual(store.goals.get(goal.id).status, GoalStatus.BLOCKED)

        complete_task_in_store(store, second_task.id, auto_dispatch=False)
        self.assertEqual(store.goals.get(goal.id).status, GoalStatus.REVIEW)


if __name__ == "__main__":
    unittest.main()
