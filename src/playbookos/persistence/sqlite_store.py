from __future__ import annotations

import json
import os
import sqlite3
from collections import Counter
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Generic, TypeVar
from urllib.parse import urlparse

from playbookos.api.store import NotFoundError
from playbookos.domain.models import (
    Acceptance,
    AcceptanceStatus,
    Artifact,
    Event,
    Goal,
    GoalStatus,
    KnowledgeBase,
    KnowledgeStatus,
    Skill,
    SkillStatus,
    Playbook,
    PlaybookStatus,
    Reflection,
    ReflectionStatus,
    Session,
    SessionKind,
    SessionStatus,
    RiskLevel,
    Run,
    RunStatus,
    Task,
    TaskStatus,
)

EntityT = TypeVar("EntityT")

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    objective TEXT NOT NULL,
    constraints_json TEXT NOT NULL,
    definition_of_done_json TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    budget_amount TEXT,
    budget_currency TEXT NOT NULL,
    due_at TEXT,
    owner_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);

CREATE TABLE IF NOT EXISTS playbooks (
    id TEXT PRIMARY KEY,
    goal_id TEXT,
    name TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    source_uri TEXT NOT NULL,
    compiled_spec_json TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goal_id) REFERENCES goals(id)
);
CREATE INDEX IF NOT EXISTS idx_playbooks_status ON playbooks(status);
CREATE INDEX IF NOT EXISTS idx_playbooks_goal_id ON playbooks(goal_id);

CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    input_schema_json TEXT NOT NULL,
    output_schema_json TEXT NOT NULL,
    required_mcp_servers_json TEXT NOT NULL,
    approval_policy_json TEXT NOT NULL,
    evaluation_policy_json TEXT NOT NULL,
    rollback_version TEXT,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_skills_status ON skills(status);

CREATE TABLE IF NOT EXISTS knowledge_bases (
    id TEXT PRIMARY KEY,
    goal_id TEXT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    content TEXT NOT NULL,
    tags_json TEXT NOT NULL,
    source_uri TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goal_id) REFERENCES goals(id)
);
CREATE INDEX IF NOT EXISTS idx_knowledge_bases_goal_id ON knowledge_bases(goal_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_bases_status ON knowledge_bases(status);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    playbook_id TEXT NOT NULL,
    parent_task_id TEXT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    priority INTEGER NOT NULL,
    depends_on_json TEXT NOT NULL,
    assigned_skill_id TEXT,
    approval_required INTEGER NOT NULL,
    queue_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goal_id) REFERENCES goals(id),
    FOREIGN KEY(playbook_id) REFERENCES playbooks(id),
    FOREIGN KEY(parent_task_id) REFERENCES tasks(id)
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_goal_id ON tasks(goal_id);
CREATE INDEX IF NOT EXISTS idx_tasks_playbook_id ON tasks(playbook_id);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    task_id TEXT,
    run_id TEXT,
    parent_session_id TEXT,
    title TEXT NOT NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    objective TEXT NOT NULL,
    input_context_json TEXT NOT NULL,
    output_context_json TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goal_id) REFERENCES goals(id),
    FOREIGN KEY(task_id) REFERENCES tasks(id),
    FOREIGN KEY(run_id) REFERENCES runs(id),
    FOREIGN KEY(parent_session_id) REFERENCES sessions(id)
);
CREATE INDEX IF NOT EXISTS idx_sessions_goal_id ON sessions(goal_id);
CREATE INDEX IF NOT EXISTS idx_sessions_task_id ON sessions(task_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);

CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    status TEXT NOT NULL,
    worker_type TEXT NOT NULL,
    trace_id TEXT,
    session_id TEXT,
    started_at TEXT,
    finished_at TEXT,
    error_class TEXT,
    error_message TEXT,
    metrics_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_task_id ON runs(task_id);

CREATE TABLE IF NOT EXISTS reflections (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    failure_category TEXT NOT NULL,
    summary TEXT NOT NULL,
    proposal_json TEXT NOT NULL,
    eval_status TEXT NOT NULL,
    approval_status TEXT NOT NULL,
    approved_by TEXT,
    published_target_version TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);
CREATE INDEX IF NOT EXISTS idx_reflections_eval_status ON reflections(eval_status);
CREATE INDEX IF NOT EXISTS idx_reflections_run_id ON reflections(run_id);

CREATE TABLE IF NOT EXISTS acceptances (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    run_id TEXT,
    criteria_json TEXT NOT NULL,
    status TEXT NOT NULL,
    artifact_ids_json TEXT NOT NULL,
    reviewer_id TEXT,
    notes TEXT NOT NULL,
    findings_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goal_id) REFERENCES goals(id),
    FOREIGN KEY(task_id) REFERENCES tasks(id),
    FOREIGN KEY(run_id) REFERENCES runs(id)
);
CREATE INDEX IF NOT EXISTS idx_acceptances_goal_id ON acceptances(goal_id);
CREATE INDEX IF NOT EXISTS idx_acceptances_task_id ON acceptances(task_id);
CREATE INDEX IF NOT EXISTS idx_acceptances_status ON acceptances(status);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_entity_type ON events(entity_type);
CREATE INDEX IF NOT EXISTS idx_events_entity_id ON events(entity_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    uri TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    checksum TEXT,
    version TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);
CREATE INDEX IF NOT EXISTS idx_artifacts_run_id ON artifacts(run_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_kind ON artifacts(kind);
"""


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _json_default(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_json_default(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_default(item) for key, item in value.items()}
    return value


def _dump_json(value: Any) -> str:
    return json.dumps(value, default=_json_default, ensure_ascii=False, sort_keys=True)


def _load_json(value: str | None, fallback: Any) -> Any:
    if value is None:
        return fallback
    return json.loads(value)


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value)


class SQLiteRepository(Generic[EntityT]):
    def __init__(
        self,
        *,
        db_path: Path,
        table_name: str,
        to_record: Callable[[EntityT], dict[str, Any]],
        from_row: Callable[[sqlite3.Row], EntityT],
    ) -> None:
        self._db_path = db_path
        self._table_name = table_name
        self._to_record = to_record
        self._from_row = from_row
        self._lock = RLock()

    def list(self) -> list[EntityT]:
        query = f"SELECT * FROM {self._table_name} ORDER BY created_at ASC"
        with self._connect() as connection:
            rows = connection.execute(query).fetchall()
        return [self._from_row(row) for row in rows]

    def get(self, item_id: str) -> EntityT:
        query = f"SELECT * FROM {self._table_name} WHERE id = ?"
        with self._connect() as connection:
            row = connection.execute(query, (item_id,)).fetchone()
        if row is None:
            raise NotFoundError(item_id)
        return self._from_row(row)

    def save(self, item: EntityT) -> EntityT:
        record = self._to_record(item)
        columns = list(record.keys())
        placeholders = ", ".join("?" for _ in columns)
        assignments = ", ".join(f"{column} = excluded.{column}" for column in columns if column != "id")
        query = (
            f"INSERT INTO {self._table_name} ({', '.join(columns)}) VALUES ({placeholders}) "
            f"ON CONFLICT(id) DO UPDATE SET {assignments}"
        )
        values = tuple(record[column] for column in columns)
        with self._lock, self._connect() as connection:
            connection.execute(query, values)
            connection.commit()
        return item

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection


class SQLiteStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()
        self.goals = SQLiteRepository[Goal](
            db_path=self.db_path,
            table_name="goals",
            to_record=_goal_to_record,
            from_row=_goal_from_row,
        )
        self.playbooks = SQLiteRepository[Playbook](
            db_path=self.db_path,
            table_name="playbooks",
            to_record=_playbook_to_record,
            from_row=_playbook_from_row,
        )
        self.skills = SQLiteRepository[Skill](
            db_path=self.db_path,
            table_name="skills",
            to_record=_skill_to_record,
            from_row=_skill_from_row,
        )
        self.knowledge_bases = SQLiteRepository[KnowledgeBase](
            db_path=self.db_path,
            table_name="knowledge_bases",
            to_record=_knowledge_base_to_record,
            from_row=_knowledge_base_from_row,
        )
        self.tasks = SQLiteRepository[Task](
            db_path=self.db_path,
            table_name="tasks",
            to_record=_task_to_record,
            from_row=_task_from_row,
        )
        self.sessions = SQLiteRepository[Session](
            db_path=self.db_path,
            table_name="sessions",
            to_record=_session_to_record,
            from_row=_session_from_row,
        )
        self.runs = SQLiteRepository[Run](
            db_path=self.db_path,
            table_name="runs",
            to_record=_run_to_record,
            from_row=_run_from_row,
        )
        self.artifacts = SQLiteRepository[Artifact](
            db_path=self.db_path,
            table_name="artifacts",
            to_record=_artifact_to_record,
            from_row=_artifact_from_row,
        )
        self.acceptances = SQLiteRepository[Acceptance](
            db_path=self.db_path,
            table_name="acceptances",
            to_record=_acceptance_to_record,
            from_row=_acceptance_from_row,
        )
        self.reflections = SQLiteRepository[Reflection](
            db_path=self.db_path,
            table_name="reflections",
            to_record=_reflection_to_record,
            from_row=_reflection_from_row,
        )
        self.events = SQLiteRepository[Event](
            db_path=self.db_path,
            table_name="events",
            to_record=_event_to_record,
            from_row=_event_from_row,
        )

    def board_snapshot(self) -> dict[str, dict[str, int]]:
        return {
            "goals": self._status_counts("goals", "status"),
            "playbooks": self._status_counts("playbooks", "status"),
            "skills": self._status_counts("skills", "status"),
            "knowledge_bases": self._status_counts("knowledge_bases", "status"),
            "tasks": self._status_counts("tasks", "status"),
            "sessions": self._status_counts("sessions", "status"),
            "runs": self._status_counts("runs", "status"),
            "artifacts": self._status_counts("artifacts", "kind"),
            "acceptances": self._status_counts("acceptances", "status"),
            "reflections": self._status_counts("reflections", "eval_status"),
            "events": self._status_counts("events", "entity_type"),
        }

    def _initialize_schema(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(SQLITE_SCHEMA)
            self._ensure_reflection_columns(connection)
            connection.commit()

    def _ensure_reflection_columns(self, connection: sqlite3.Connection) -> None:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(reflections)").fetchall()}
        if "published_target_version" not in columns:
            connection.execute("ALTER TABLE reflections ADD COLUMN published_target_version TEXT")

    def _status_counts(self, table_name: str, status_column: str) -> dict[str, int]:
        query = f"SELECT {status_column} AS status, COUNT(*) AS count FROM {table_name} GROUP BY {status_column}"
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(query).fetchall()
        return dict(Counter({row[0]: row[1] for row in rows}))



def create_store_from_env() -> SQLiteStore:
    store_backend = os.getenv("PLAYBOOKOS_STORE", "sqlite").strip().lower()
    database_url = os.getenv("DATABASE_URL", "").strip()
    db_path = os.getenv("PLAYBOOKOS_DB_PATH", "data/playbookos.db").strip()

    if store_backend == "memory":
        raise RuntimeError("PLAYBOOKOS_STORE=memory is deprecated for API runtime; pass an explicit store object in tests")

    if database_url:
        parsed = urlparse(database_url)
        if parsed.scheme == "sqlite":
            return SQLiteStore(_sqlite_path_from_url(database_url))
        if parsed.scheme in {"postgres", "postgresql"}:
            raise RuntimeError(
                "PostgreSQL runtime adapter is not wired yet in code; use the provided PostgreSQL schema files and keep local runtime on sqlite for now"
            )
        raise RuntimeError(f"Unsupported DATABASE_URL scheme: {parsed.scheme}")

    return SQLiteStore(db_path)



def _sqlite_path_from_url(database_url: str) -> str:
    parsed = urlparse(database_url)
    if parsed.netloc and parsed.netloc != "":
        return f"/{parsed.netloc}{parsed.path}"
    return parsed.path or ":memory:"



def _goal_to_record(goal: Goal) -> dict[str, Any]:
    return {
        "id": goal.id,
        "title": goal.title,
        "objective": goal.objective,
        "constraints_json": _dump_json(goal.constraints),
        "definition_of_done_json": _dump_json(goal.definition_of_done),
        "risk_level": goal.risk_level.value,
        "budget_amount": str(goal.budget_amount) if goal.budget_amount is not None else None,
        "budget_currency": goal.budget_currency,
        "due_at": goal.due_at.isoformat() if goal.due_at else None,
        "owner_id": goal.owner_id,
        "status": goal.status.value,
        "created_at": goal.created_at.isoformat(),
        "updated_at": goal.updated_at.isoformat(),
    }



def _goal_from_row(row: sqlite3.Row) -> Goal:
    return Goal(
        id=row["id"],
        title=row["title"],
        objective=row["objective"],
        constraints=_load_json(row["constraints_json"], []),
        definition_of_done=_load_json(row["definition_of_done_json"], []),
        risk_level=RiskLevel(row["risk_level"]),
        budget_amount=Decimal(row["budget_amount"]) if row["budget_amount"] is not None else None,
        budget_currency=row["budget_currency"],
        due_at=_parse_datetime(row["due_at"]),
        owner_id=row["owner_id"],
        status=GoalStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )



def _playbook_to_record(playbook: Playbook) -> dict[str, Any]:
    return {
        "id": playbook.id,
        "goal_id": playbook.goal_id,
        "name": playbook.name,
        "source_kind": playbook.source_kind,
        "source_uri": playbook.source_uri,
        "compiled_spec_json": _dump_json(playbook.compiled_spec),
        "version": playbook.version,
        "status": playbook.status.value,
        "created_at": playbook.created_at.isoformat(),
        "updated_at": playbook.updated_at.isoformat(),
    }



def _playbook_from_row(row: sqlite3.Row) -> Playbook:
    return Playbook(
        id=row["id"],
        goal_id=row["goal_id"],
        name=row["name"],
        source_kind=row["source_kind"],
        source_uri=row["source_uri"],
        compiled_spec=_load_json(row["compiled_spec_json"], {}),
        version=row["version"],
        status=PlaybookStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )




def _skill_to_record(skill: Skill) -> dict[str, Any]:
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "input_schema_json": _dump_json(skill.input_schema),
        "output_schema_json": _dump_json(skill.output_schema),
        "required_mcp_servers_json": _dump_json(skill.required_mcp_servers),
        "approval_policy_json": _dump_json(skill.approval_policy),
        "evaluation_policy_json": _dump_json(skill.evaluation_policy),
        "rollback_version": skill.rollback_version,
        "version": skill.version,
        "status": skill.status.value,
        "created_at": skill.created_at.isoformat(),
        "updated_at": skill.updated_at.isoformat(),
    }


def _skill_from_row(row: sqlite3.Row) -> Skill:
    return Skill(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        input_schema=_load_json(row["input_schema_json"], {}),
        output_schema=_load_json(row["output_schema_json"], {}),
        required_mcp_servers=_load_json(row["required_mcp_servers_json"], []),
        approval_policy=_load_json(row["approval_policy_json"], {}),
        evaluation_policy=_load_json(row["evaluation_policy_json"], {}),
        rollback_version=row["rollback_version"],
        version=row["version"],
        status=SkillStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )

def _knowledge_base_to_record(item: KnowledgeBase) -> dict[str, Any]:
    return {
        "id": item.id,
        "goal_id": item.goal_id,
        "name": item.name,
        "description": item.description,
        "content": item.content,
        "tags_json": _dump_json(item.tags),
        "source_uri": item.source_uri,
        "status": item.status.value,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


def _knowledge_base_from_row(row: sqlite3.Row) -> KnowledgeBase:
    return KnowledgeBase(
        id=row["id"],
        goal_id=row["goal_id"],
        name=row["name"],
        description=row["description"],
        content=row["content"],
        tags=_load_json(row["tags_json"], []),
        source_uri=row["source_uri"],
        status=KnowledgeStatus(row["status"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )

def _task_to_record(task: Task) -> dict[str, Any]:
    return {
        "id": task.id,
        "goal_id": task.goal_id,
        "playbook_id": task.playbook_id,
        "parent_task_id": task.parent_task_id,
        "name": task.name,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority,
        "depends_on_json": _dump_json(task.depends_on),
        "assigned_skill_id": task.assigned_skill_id,
        "approval_required": int(task.approval_required),
        "queue_name": task.queue_name,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }



def _task_from_row(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        goal_id=row["goal_id"],
        playbook_id=row["playbook_id"],
        parent_task_id=row["parent_task_id"],
        name=row["name"],
        description=row["description"],
        status=TaskStatus(row["status"]),
        priority=row["priority"],
        depends_on=_load_json(row["depends_on_json"], []),
        assigned_skill_id=row["assigned_skill_id"],
        approval_required=bool(row["approval_required"]),
        queue_name=row["queue_name"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )




def _session_to_record(session: Session) -> dict[str, Any]:
    return {
        "id": session.id,
        "goal_id": session.goal_id,
        "task_id": session.task_id,
        "run_id": session.run_id,
        "parent_session_id": session.parent_session_id,
        "title": session.title,
        "kind": session.kind.value,
        "status": session.status.value,
        "objective": session.objective,
        "input_context_json": _dump_json(session.input_context),
        "output_context_json": _dump_json(session.output_context),
        "summary": session.summary,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
    }


def _session_from_row(row: sqlite3.Row) -> Session:
    return Session(
        id=row["id"],
        goal_id=row["goal_id"],
        task_id=row["task_id"],
        run_id=row["run_id"],
        parent_session_id=row["parent_session_id"],
        title=row["title"],
        kind=SessionKind(row["kind"]),
        status=SessionStatus(row["status"]),
        objective=row["objective"],
        input_context=_load_json(row["input_context_json"], {}),
        output_context=_load_json(row["output_context_json"], {}),
        summary=row["summary"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )

def _run_to_record(run: Run) -> dict[str, Any]:
    return {
        "id": run.id,
        "task_id": run.task_id,
        "attempt": run.attempt,
        "status": run.status.value,
        "worker_type": run.worker_type,
        "trace_id": run.trace_id,
        "session_id": run.session_id,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "error_class": run.error_class,
        "error_message": run.error_message,
        "metrics_json": _dump_json(run.metrics),
        "created_at": run.created_at.isoformat(),
    }



def _run_from_row(row: sqlite3.Row) -> Run:
    return Run(
        id=row["id"],
        task_id=row["task_id"],
        attempt=row["attempt"],
        status=RunStatus(row["status"]),
        worker_type=row["worker_type"],
        trace_id=row["trace_id"],
        session_id=row["session_id"],
        started_at=_parse_datetime(row["started_at"]),
        finished_at=_parse_datetime(row["finished_at"]),
        error_class=row["error_class"],
        error_message=row["error_message"],
        metrics=_load_json(row["metrics_json"], {}),
        created_at=datetime.fromisoformat(row["created_at"]),
    )



def _reflection_to_record(reflection: Reflection) -> dict[str, Any]:
    return {
        "id": reflection.id,
        "run_id": reflection.run_id,
        "failure_category": reflection.failure_category,
        "summary": reflection.summary,
        "proposal_json": _dump_json(reflection.proposal),
        "eval_status": reflection.eval_status.value,
        "approval_status": reflection.approval_status,
        "approved_by": reflection.approved_by,
        "published_target_version": reflection.published_target_version,
        "created_at": reflection.created_at.isoformat(),
        "updated_at": reflection.updated_at.isoformat(),
    }



def _reflection_from_row(row: sqlite3.Row) -> Reflection:
    row_keys = set(row.keys())
    published_target_version = row["published_target_version"] if "published_target_version" in row_keys else None
    if published_target_version is None and "published_skill_version" in row_keys:
        published_target_version = row["published_skill_version"]

    return Reflection(
        id=row["id"],
        run_id=row["run_id"],
        failure_category=row["failure_category"],
        summary=row["summary"],
        proposal=_load_json(row["proposal_json"], {}),
        eval_status=ReflectionStatus(row["eval_status"]),
        approval_status=row["approval_status"],
        approved_by=row["approved_by"],
        published_target_version=published_target_version,
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )




def _acceptance_to_record(acceptance: Acceptance) -> dict[str, Any]:
    return {
        "id": acceptance.id,
        "goal_id": acceptance.goal_id,
        "task_id": acceptance.task_id,
        "run_id": acceptance.run_id,
        "criteria_json": _dump_json(acceptance.criteria),
        "status": acceptance.status.value,
        "artifact_ids_json": _dump_json(acceptance.artifact_ids),
        "reviewer_id": acceptance.reviewer_id,
        "notes": acceptance.notes,
        "findings_json": _dump_json(acceptance.findings),
        "created_at": acceptance.created_at.isoformat(),
        "updated_at": acceptance.updated_at.isoformat(),
    }


def _acceptance_from_row(row: sqlite3.Row) -> Acceptance:
    return Acceptance(
        id=row["id"],
        goal_id=row["goal_id"],
        task_id=row["task_id"],
        run_id=row["run_id"],
        criteria=_load_json(row["criteria_json"], []),
        status=AcceptanceStatus(row["status"]),
        artifact_ids=_load_json(row["artifact_ids_json"], []),
        reviewer_id=row["reviewer_id"],
        notes=row["notes"],
        findings=_load_json(row["findings_json"], []),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _event_to_record(event: Event) -> dict[str, Any]:
    return {
        "id": event.id,
        "entity_type": event.entity_type,
        "entity_id": event.entity_id,
        "event_type": event.event_type,
        "payload_json": _dump_json(event.payload),
        "source": event.source,
        "created_at": event.created_at.isoformat(),
    }


def _event_from_row(row: sqlite3.Row) -> Event:
    return Event(
        id=row["id"],
        entity_type=row["entity_type"],
        entity_id=row["entity_id"],
        event_type=row["event_type"],
        payload=_load_json(row["payload_json"], {}),
        source=row["source"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )

def _artifact_to_record(artifact: Artifact) -> dict[str, Any]:
    return {
        "id": artifact.id,
        "run_id": artifact.run_id,
        "kind": artifact.kind,
        "title": artifact.title,
        "uri": artifact.uri,
        "mime_type": artifact.mime_type,
        "checksum": artifact.checksum,
        "version": artifact.version,
        "metadata_json": _dump_json(artifact.metadata),
        "created_at": artifact.created_at.isoformat(),
    }



def _artifact_from_row(row: sqlite3.Row) -> Artifact:
    return Artifact(
        id=row["id"],
        run_id=row["run_id"],
        kind=row["kind"],
        title=row["title"],
        uri=row["uri"],
        mime_type=row["mime_type"],
        checksum=row["checksum"],
        version=row["version"],
        metadata=_load_json(row["metadata_json"], {}),
        created_at=datetime.fromisoformat(row["created_at"]),
    )
