from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from playbookos.api.store import StoreProtocol
from playbookos.domain.models import (
    Acceptance,
    AcceptanceStatus,
    Event,
    GoalStatus,
    RunStatus,
    Session,
    SessionKind,
    SessionStatus,
    TaskStatus,
    utc_now,
)


class AcceptanceError(ValueError):
    pass


@dataclass(slots=True)
class TaskAcceptanceResult:
    acceptance: Acceptance
    task_status: TaskStatus
    goal_status: GoalStatus
    event_ids: list[str] = field(default_factory=list)


def append_event(
    store: StoreProtocol,
    *,
    entity_type: str,
    entity_id: str,
    event_type: str,
    payload: dict[str, Any] | None = None,
    source: str = "system",
) -> Event:
    event = Event(
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        payload=payload or {},
        source=source,
    )
    store.events.save(event)
    return event


def ensure_goal_supervisor_session(store: StoreProtocol, goal_id: str) -> Session:
    goal = store.goals.get(goal_id)
    existing = next(
        (session for session in store.sessions.list() if session.goal_id == goal_id and session.kind == SessionKind.SUPERVISOR),
        None,
    )
    if existing is not None:
        return existing

    session = Session(
        goal_id=goal.id,
        title=f"Supervisor · {goal.title}",
        kind=SessionKind.SUPERVISOR,
        status=SessionStatus.RUNNING,
        objective=goal.objective,
        input_context={"constraints": goal.constraints, "definition_of_done": goal.definition_of_done},
    )
    store.sessions.save(session)
    append_event(
        store,
        entity_type="session",
        entity_id=session.id,
        event_type="session.supervisor_created",
        payload={"goal_id": goal.id},
    )
    return session


def ensure_worker_session_for_run(store: StoreProtocol, run_id: str) -> Session:
    run = store.runs.get(run_id)
    if run.session_id:
        return store.sessions.get(run.session_id)

    task = store.tasks.get(run.task_id)
    supervisor = ensure_goal_supervisor_session(store, task.goal_id)
    worker = Session(
        goal_id=task.goal_id,
        task_id=task.id,
        run_id=run.id,
        parent_session_id=supervisor.id,
        title=f"Worker · {task.name}",
        kind=SessionKind.WORKER,
        status=SessionStatus.PLANNED,
        objective=task.description,
        input_context={
            "task_name": task.name,
            "queue_name": task.queue_name,
            "approval_required": task.approval_required,
            "assigned_skill_id": task.assigned_skill_id,
        },
    )
    store.sessions.save(worker)
    run.session_id = worker.id
    store.runs.save(run)
    append_event(
        store,
        entity_type="session",
        entity_id=worker.id,
        event_type="session.worker_spawned",
        payload={"goal_id": task.goal_id, "task_id": task.id, "run_id": run.id, "parent_session_id": supervisor.id},
    )
    return worker


def update_session_for_run(
    store: StoreProtocol,
    run_id: str,
    *,
    status: SessionStatus,
    summary: str = "",
    output_context: dict[str, Any] | None = None,
) -> Session:
    run = store.runs.get(run_id)
    session = ensure_worker_session_for_run(store, run.id)
    session.status = status
    session.summary = summary or session.summary
    if output_context:
        session.output_context = {**session.output_context, **output_context}
    session.updated_at = utc_now()
    store.sessions.save(session)
    append_event(
        store,
        entity_type="session",
        entity_id=session.id,
        event_type="session.updated",
        payload={"run_id": run.id, "status": status.value},
    )
    return session


def list_goal_sessions(store: StoreProtocol, goal_id: str) -> list[Session]:
    return [session for session in store.sessions.list() if session.goal_id == goal_id]


def accept_task_in_store(
    store: StoreProtocol,
    task_id: str,
    *,
    criteria: list[str],
    reviewer_id: str | None = None,
    accepted: bool,
    notes: str = "",
    findings: list[str] | None = None,
) -> TaskAcceptanceResult:
    task = store.tasks.get(task_id)
    goal = store.goals.get(task.goal_id)
    related_runs = [run for run in store.runs.list() if run.task_id == task.id]
    latest_run = related_runs[-1] if related_runs else None
    artifact_ids = [artifact.id for artifact in store.artifacts.list() if latest_run is not None and artifact.run_id == latest_run.id]

    status = AcceptanceStatus.ACCEPTED if accepted else AcceptanceStatus.REJECTED
    acceptance = Acceptance(
        goal_id=task.goal_id,
        task_id=task.id,
        run_id=latest_run.id if latest_run is not None else None,
        criteria=criteria,
        status=status,
        artifact_ids=artifact_ids,
        reviewer_id=reviewer_id,
        notes=notes,
        findings=findings or [],
    )
    store.acceptances.save(acceptance)

    event_ids: list[str] = []
    acceptance_event = append_event(
        store,
        entity_type="acceptance",
        entity_id=acceptance.id,
        event_type="acceptance.recorded",
        payload={"task_id": task.id, "goal_id": goal.id, "status": status.value},
        source=reviewer_id or "human",
    )
    event_ids.append(acceptance_event.id)

    if accepted:
        task.status = TaskStatus.LEARNED
        if all(item.status in {TaskStatus.DONE, TaskStatus.LEARNED} for item in store.tasks.list() if item.goal_id == goal.id and item.id != task.id):
            goal.status = GoalStatus.LEARNED
        else:
            goal.status = GoalStatus.REVIEW
    else:
        task.status = TaskStatus.BLOCKED
        goal.status = GoalStatus.BLOCKED

    task.updated_at = utc_now()
    goal.updated_at = utc_now()
    store.tasks.save(task)
    store.goals.save(goal)

    if latest_run is not None:
        session_status = SessionStatus.COMPLETED if accepted else SessionStatus.FAILED
        update_session_for_run(
            store,
            latest_run.id,
            status=session_status,
            summary=notes or ("Accepted by reviewer" if accepted else "Rejected by reviewer"),
            output_context={"acceptance_id": acceptance.id, "acceptance_status": status.value},
        )

    task_event = append_event(
        store,
        entity_type="task",
        entity_id=task.id,
        event_type="task.accepted" if accepted else "task.rejected",
        payload={"acceptance_id": acceptance.id, "goal_id": goal.id},
        source=reviewer_id or "human",
    )
    event_ids.append(task_event.id)

    return TaskAcceptanceResult(
        acceptance=acceptance,
        task_status=task.status,
        goal_status=goal.status,
        event_ids=event_ids,
    )
