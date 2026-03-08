from __future__ import annotations

from dataclasses import dataclass, field

from playbookos.api.store import NotFoundError, StoreProtocol
from playbookos.domain.models import GoalStatus, Run, RunStatus, Task, TaskStatus, utc_now

ACTIVE_RUN_STATUSES = {RunStatus.QUEUED, RunStatus.RUNNING, RunStatus.WAITING_HUMAN}
TERMINAL_TASK_STATUSES = {TaskStatus.DONE, TaskStatus.LEARNED}


class OrchestrationError(ValueError):
    pass


@dataclass(slots=True)
class TemporalWorkflowSpec:
    goal_id: str
    task_ids: list[str]
    runnable_task_ids: list[str]
    waiting_human_task_ids: list[str]
    queue_names: dict[str, str]


@dataclass(slots=True)
class GoalDispatchResult:
    goal_id: str
    promoted_task_ids: list[str] = field(default_factory=list)
    dispatched_task_ids: list[str] = field(default_factory=list)
    created_run_ids: list[str] = field(default_factory=list)
    waiting_human_task_ids: list[str] = field(default_factory=list)
    goal_status: GoalStatus = GoalStatus.RUNNING
    temporal_spec: TemporalWorkflowSpec | None = None


@dataclass(slots=True)
class TaskCompletionResult:
    task_id: str
    goal_id: str
    goal_status: GoalStatus
    promoted_task_ids: list[str] = field(default_factory=list)
    dispatched_task_ids: list[str] = field(default_factory=list)
    created_run_ids: list[str] = field(default_factory=list)


class GoalOrchestrator:
    def dispatch_goal(self, store: StoreProtocol, goal_id: str) -> GoalDispatchResult:
        goal = store.goals.get(goal_id)
        tasks = self._goal_tasks(store, goal_id)
        if not tasks:
            raise OrchestrationError("Goal has no tasks to orchestrate")

        task_map = {task.id: task for task in tasks}
        active_runs_by_task = self._active_runs_by_task(store, tasks)

        promoted_task_ids: list[str] = []
        dispatched_task_ids: list[str] = []
        created_run_ids: list[str] = []
        waiting_human_task_ids: list[str] = []

        for task in sorted(tasks, key=lambda item: (item.priority, item.created_at)):
            if task.status == TaskStatus.INBOX and self._dependencies_satisfied(task, task_map):
                task.status = TaskStatus.READY
                task.updated_at = utc_now()
                store.tasks.save(task)
                promoted_task_ids.append(task.id)

        tasks = self._goal_tasks(store, goal_id)
        task_map = {task.id: task for task in tasks}
        active_runs_by_task = self._active_runs_by_task(store, tasks)

        for task in sorted(tasks, key=lambda item: (item.priority, item.created_at)):
            if task.status != TaskStatus.READY:
                continue
            if task.id in active_runs_by_task:
                continue

            run_status = RunStatus.WAITING_HUMAN if task.approval_required else RunStatus.QUEUED
            run = Run(task_id=task.id, worker_type="temporal-worker", status=run_status)
            store.runs.save(run)

            task.status = TaskStatus.WAITING_HUMAN if task.approval_required else TaskStatus.RUNNING
            task.updated_at = utc_now()
            store.tasks.save(task)

            dispatched_task_ids.append(task.id)
            created_run_ids.append(run.id)
            if task.approval_required:
                waiting_human_task_ids.append(task.id)

        goal_status = self._recalculate_goal_status(store, goal_id)
        goal.status = goal_status
        goal.updated_at = utc_now()
        store.goals.save(goal)

        tasks = self._goal_tasks(store, goal_id)
        temporal_spec = self._build_temporal_spec(goal_id, tasks)
        return GoalDispatchResult(
            goal_id=goal_id,
            promoted_task_ids=promoted_task_ids,
            dispatched_task_ids=dispatched_task_ids,
            created_run_ids=created_run_ids,
            waiting_human_task_ids=waiting_human_task_ids,
            goal_status=goal_status,
            temporal_spec=temporal_spec,
        )

    def complete_task(self, store: StoreProtocol, task_id: str, *, auto_dispatch: bool = True) -> TaskCompletionResult:
        task = store.tasks.get(task_id)
        task.status = TaskStatus.DONE
        task.updated_at = utc_now()
        store.tasks.save(task)

        self._finalize_active_runs(store, task.id)

        dispatch_result = GoalDispatchResult(goal_id=task.goal_id, goal_status=GoalStatus.RUNNING)
        if auto_dispatch:
            dispatch_result = self.dispatch_goal(store, task.goal_id)
        else:
            goal_status = self._recalculate_goal_status(store, task.goal_id)
            goal = store.goals.get(task.goal_id)
            goal.status = goal_status
            goal.updated_at = utc_now()
            store.goals.save(goal)
            dispatch_result.goal_status = goal_status

        return TaskCompletionResult(
            task_id=task.id,
            goal_id=task.goal_id,
            goal_status=dispatch_result.goal_status,
            promoted_task_ids=dispatch_result.promoted_task_ids,
            dispatched_task_ids=dispatch_result.dispatched_task_ids,
            created_run_ids=dispatch_result.created_run_ids,
        )

    def _goal_tasks(self, store: StoreProtocol, goal_id: str) -> list[Task]:
        return [task for task in store.tasks.list() if task.goal_id == goal_id]

    def _dependencies_satisfied(self, task: Task, task_map: dict[str, Task]) -> bool:
        return all(task_map[dependency_id].status in TERMINAL_TASK_STATUSES for dependency_id in task.depends_on)

    def _active_runs_by_task(self, store: StoreProtocol, tasks: list[Task]) -> dict[str, Run]:
        task_ids = {task.id for task in tasks}
        active_runs: dict[str, Run] = {}
        for run in store.runs.list():
            if run.task_id not in task_ids:
                continue
            if run.status not in ACTIVE_RUN_STATUSES:
                continue
            active_runs[run.task_id] = run
        return active_runs

    def _finalize_active_runs(self, store: StoreProtocol, task_id: str) -> None:
        for run in store.runs.list():
            if run.task_id != task_id:
                continue
            if run.status not in ACTIVE_RUN_STATUSES:
                continue
            run.status = RunStatus.SUCCEEDED
            run.finished_at = utc_now()
            store.runs.save(run)

    def _recalculate_goal_status(self, store: StoreProtocol, goal_id: str) -> GoalStatus:
        tasks = self._goal_tasks(store, goal_id)
        if not tasks:
            return GoalStatus.READY

        statuses = {task.status for task in tasks}
        if statuses.issubset(TERMINAL_TASK_STATUSES):
            return GoalStatus.REVIEW
        if TaskStatus.WAITING_HUMAN in statuses:
            return GoalStatus.BLOCKED
        if TaskStatus.FAILED in statuses or TaskStatus.BLOCKED in statuses:
            return GoalStatus.BLOCKED
        if TaskStatus.RUNNING in statuses:
            return GoalStatus.RUNNING
        if TaskStatus.READY in statuses or TaskStatus.INBOX in statuses:
            return GoalStatus.RUNNING
        return GoalStatus.READY

    def _build_temporal_spec(self, goal_id: str, tasks: list[Task]) -> TemporalWorkflowSpec:
        return TemporalWorkflowSpec(
            goal_id=goal_id,
            task_ids=[task.id for task in tasks],
            runnable_task_ids=[task.id for task in tasks if task.status in {TaskStatus.READY, TaskStatus.RUNNING}],
            waiting_human_task_ids=[task.id for task in tasks if task.status == TaskStatus.WAITING_HUMAN],
            queue_names={task.id: task.queue_name for task in tasks},
        )


def dispatch_goal_in_store(
    store: StoreProtocol,
    goal_id: str,
    *,
    orchestrator: GoalOrchestrator | None = None,
) -> GoalDispatchResult:
    orchestrator = orchestrator or GoalOrchestrator()
    return orchestrator.dispatch_goal(store, goal_id)



def complete_task_in_store(
    store: StoreProtocol,
    task_id: str,
    *,
    auto_dispatch: bool = True,
    orchestrator: GoalOrchestrator | None = None,
) -> TaskCompletionResult:
    orchestrator = orchestrator or GoalOrchestrator()
    try:
        return orchestrator.complete_task(store, task_id, auto_dispatch=auto_dispatch)
    except NotFoundError as exc:
        raise OrchestrationError(f"Task not found: {task_id}") from exc
