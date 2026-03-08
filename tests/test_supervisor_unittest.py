import unittest

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Goal, GoalStatus, Playbook, RunStatus, SessionKind, SessionStatus, TaskStatus
from playbookos.executor.service import DeterministicExecutorAdapter, execute_run_in_store
from playbookos.orchestrator.service import complete_task_in_store, dispatch_goal_in_store
from playbookos.planner.service import plan_goal_in_store
from playbookos.supervisor import accept_task_in_store


class SupervisorFlowTestCase(unittest.TestCase):
    def test_dispatch_creates_supervisor_worker_sessions_and_events(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Session goal", objective="Spawn visible child sessions"))
        store.playbooks.save(
            Playbook(
                name="Session playbook",
                source_kind="markdown",
                source_uri="file:///tmp/session.md",
                goal_id=goal.id,
                compiled_spec={"steps": ["Collect context"]},
            )
        )

        plan_goal_in_store(store, goal.id)
        dispatch = dispatch_goal_in_store(store, goal.id)

        self.assertEqual(len(dispatch.created_run_ids), 1)
        sessions = store.sessions.list()
        self.assertEqual(len([item for item in sessions if item.kind == SessionKind.SUPERVISOR]), 1)
        self.assertEqual(len([item for item in sessions if item.kind == SessionKind.WORKER]), 1)

        run = store.runs.get(dispatch.created_run_ids[0])
        worker = store.sessions.get(run.session_id)
        self.assertEqual(worker.run_id, run.id)
        self.assertEqual(worker.status, SessionStatus.PLANNED)

        event_types = {event.event_type for event in store.events.list()}
        self.assertIn("session.supervisor_created", event_types)
        self.assertIn("session.worker_spawned", event_types)
        self.assertIn("goal.dispatch_started", event_types)
        self.assertIn("run.created", event_types)

    def test_execute_and_accept_task_updates_session_and_goal_learning(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Acceptance goal", objective="Accept completed work"))
        store.playbooks.save(
            Playbook(
                name="Acceptance playbook",
                source_kind="markdown",
                source_uri="file:///tmp/acceptance.md",
                goal_id=goal.id,
                compiled_spec={"steps": ["Deliver output"]},
            )
        )

        plan_goal_in_store(store, goal.id)
        dispatch = dispatch_goal_in_store(store, goal.id)
        run_id = dispatch.created_run_ids[0]
        result = execute_run_in_store(store, run_id, adapter=DeterministicExecutorAdapter())
        completion = complete_task_in_store(store, store.runs.get(run_id).task_id, auto_dispatch=False)
        acceptance_result = accept_task_in_store(
            store,
            completion.task_id,
            criteria=["Output is complete", "Artifacts are attached"],
            reviewer_id="reviewer-1",
            accepted=True,
            notes="Looks good.",
        )

        run = store.runs.get(run_id)
        worker = store.sessions.get(run.session_id)
        self.assertEqual(result.status, RunStatus.SUCCEEDED)
        self.assertEqual(worker.status, SessionStatus.COMPLETED)
        self.assertEqual(worker.output_context["run_status"], RunStatus.SUCCEEDED.value)
        self.assertEqual(worker.output_context["acceptance_id"], acceptance_result.acceptance.id)
        self.assertEqual(store.tasks.get(completion.task_id).status, TaskStatus.LEARNED)
        self.assertEqual(store.goals.get(goal.id).status, GoalStatus.LEARNED)
        self.assertEqual(acceptance_result.acceptance.status.value, "accepted")

        event_types = [event.event_type for event in store.events.list()]
        self.assertIn("run.execution_started", event_types)
        self.assertIn("run.execution_finished", event_types)
        self.assertIn("acceptance.recorded", event_types)
        self.assertIn("task.accepted", event_types)


if __name__ == "__main__":
    unittest.main()
