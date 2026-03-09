from __future__ import annotations

from collections import Counter
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


def _session_sort_key(session: Session) -> tuple[str, str]:
    return (session.created_at.isoformat(), session.id)


def _counts_by_status(values: list[Any], attribute: str = "status") -> dict[str, int]:
    counter = Counter(str(getattr(item, attribute).value if hasattr(getattr(item, attribute), "value") else getattr(item, attribute)) for item in values)
    return dict(counter)


def _goal_to_session_status(goal_status: GoalStatus) -> SessionStatus:
    if goal_status in {GoalStatus.LEARNED, GoalStatus.DONE, GoalStatus.ARCHIVED}:
        return SessionStatus.COMPLETED
    if goal_status == GoalStatus.BLOCKED:
        return SessionStatus.WAITING_HUMAN
    if goal_status in {GoalStatus.RUNNING, GoalStatus.REVIEW}:
        return SessionStatus.RUNNING
    return SessionStatus.PLANNED


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


def ensure_child_session(
    store: StoreProtocol,
    *,
    goal_id: str,
    parent_session_id: str,
    title: str,
    task_id: str | None = None,
    run_id: str | None = None,
    objective: str = "",
    input_context: dict[str, Any] | None = None,
    kind: SessionKind = SessionKind.WORKER,
) -> Session:
    existing = next(
        (
            session
            for session in store.sessions.list()
            if session.goal_id == goal_id
            and session.parent_session_id == parent_session_id
            and session.title == title
            and session.task_id == task_id
            and session.run_id == run_id
        ),
        None,
    )
    if existing is not None:
        if input_context:
            existing.input_context = {**existing.input_context, **input_context}
            existing.updated_at = utc_now()
            store.sessions.save(existing)
        return existing

    child = Session(
        goal_id=goal_id,
        task_id=task_id,
        run_id=run_id,
        parent_session_id=parent_session_id,
        title=title,
        kind=kind,
        status=SessionStatus.PLANNED,
        objective=objective,
        input_context=input_context or {},
    )
    store.sessions.save(child)
    append_event(
        store,
        entity_type="session",
        entity_id=child.id,
        event_type="session.child_spawned",
        payload={"goal_id": goal_id, "parent_session_id": parent_session_id, "task_id": task_id, "run_id": run_id, "title": title},
    )
    return child


def record_child_session(
    store: StoreProtocol,
    *,
    goal_id: str,
    parent_session_id: str,
    title: str,
    task_id: str | None = None,
    run_id: str | None = None,
    objective: str = "",
    input_context: dict[str, Any] | None = None,
    output_context: dict[str, Any] | None = None,
    summary: str = "",
    status: SessionStatus = SessionStatus.COMPLETED,
) -> Session:
    session = ensure_child_session(
        store,
        goal_id=goal_id,
        parent_session_id=parent_session_id,
        title=title,
        task_id=task_id,
        run_id=run_id,
        objective=objective,
        input_context=input_context,
    )
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
        event_type="session.child_updated",
        payload={"goal_id": goal_id, "parent_session_id": parent_session_id, "status": status.value, "run_id": run_id},
    )
    return session


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


def refresh_goal_supervisor_session(store: StoreProtocol, goal_id: str) -> Session:
    goal = store.goals.get(goal_id)
    supervisor = ensure_goal_supervisor_session(store, goal_id)
    tasks = [task for task in store.tasks.list() if task.goal_id == goal_id]
    task_ids = {task.id for task in tasks}
    runs = [run for run in store.runs.list() if run.task_id in task_ids]
    run_ids = {run.id for run in runs}
    sessions = sorted([session for session in store.sessions.list() if session.goal_id == goal_id], key=_session_sort_key)
    session_ids = {session.id for session in sessions}
    acceptances = [item for item in store.acceptances.list() if item.goal_id == goal_id]
    acceptance_ids = {item.id for item in acceptances}
    reflections = [item for item in store.reflections.list() if item.run_id in run_ids]
    reflection_ids = {item.id for item in reflections}
    knowledge_updates = [item for item in store.knowledge_updates.list() if item.goal_id == goal_id]
    knowledge_update_ids = {item.id for item in knowledge_updates}
    events = [
        item
        for item in store.events.list()
        if (item.entity_type == "goal" and item.entity_id == goal_id)
        or (item.entity_type == "task" and item.entity_id in task_ids)
        or (item.entity_type == "run" and item.entity_id in run_ids)
        or (item.entity_type == "session" and item.entity_id in session_ids)
        or (item.entity_type == "acceptance" and item.entity_id in acceptance_ids)
        or (item.entity_type == "reflection" and item.entity_id in reflection_ids)
        or (item.entity_type == "knowledge_update" and item.entity_id in knowledge_update_ids)
    ]

    aggregate = {
        "goal_status": goal.status.value,
        "tasks": _counts_by_status(tasks),
        "runs": _counts_by_status(runs),
        "acceptances": _counts_by_status(acceptances),
        "reflections": _counts_by_status(reflections, attribute="eval_status"),
        "knowledge_updates": _counts_by_status(knowledge_updates),
        "session_total": len(sessions),
        "child_session_total": len([session for session in sessions if session.parent_session_id]),
        "worker_session_total": len([session for session in sessions if session.kind == SessionKind.WORKER]),
        "event_count": len(events),
        "waiting_human_runs": len([run for run in runs if run.status == RunStatus.WAITING_HUMAN]),
        "review_tasks": len([task for task in tasks if task.status == TaskStatus.REVIEW]),
        "learned_tasks": len([task for task in tasks if task.status == TaskStatus.LEARNED]),
        "active_task_count": len([task for task in tasks if task.status not in {TaskStatus.DONE, TaskStatus.LEARNED}]),
        "latest_reflection_id": reflections[-1].id if reflections else None,
        "latest_knowledge_update_id": knowledge_updates[-1].id if knowledge_updates else None,
    }

    summary_parts = [
        f"{len([task for task in tasks if task.status in {TaskStatus.DONE, TaskStatus.LEARNED}])}/{len(tasks)} tasks closed" if tasks else "0 tasks",
        f"{aggregate['waiting_human_runs']} waiting human",
        f"{len(reflections)} reflections",
        f"{len(knowledge_updates)} knowledge updates",
    ]
    latest_events = [event.event_type for event in sorted(events, key=lambda item: (item.created_at.isoformat(), item.id))[-4:]]
    changed = (
        supervisor.status != _goal_to_session_status(goal.status)
        or supervisor.summary != " · ".join(summary_parts)
        or supervisor.output_context.get("aggregate") != aggregate
        or supervisor.output_context.get("latest_events") != latest_events
    )

    supervisor.status = _goal_to_session_status(goal.status)
    supervisor.summary = " · ".join(summary_parts)
    supervisor.output_context = {
        **supervisor.output_context,
        "aggregate": aggregate,
        "latest_events": latest_events,
        "goal_title": goal.title,
    }
    supervisor.updated_at = utc_now()
    store.sessions.save(supervisor)

    if changed:
        append_event(
            store,
            entity_type="session",
            entity_id=supervisor.id,
            event_type="session.supervisor_refreshed",
            payload={"goal_id": goal_id, "goal_status": goal.status.value, "summary": supervisor.summary},
        )
    return supervisor


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
    refresh_goal_supervisor_session(store, goal.id)

    return TaskAcceptanceResult(
        acceptance=acceptance,
        task_status=task.status,
        goal_status=goal.status,
        event_ids=event_ids,
    )
