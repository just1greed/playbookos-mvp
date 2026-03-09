from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(UTC)


class GoalStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    REVIEW = "review"
    DONE = "done"
    LEARNED = "learned"
    ARCHIVED = "archived"


class PlaybookStatus(StrEnum):
    DRAFT = "draft"
    COMPILED = "compiled"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class SkillStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class MCPServerStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class KnowledgeStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class TaskStatus(StrEnum):
    INBOX = "inbox"
    READY = "ready"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_human"
    BLOCKED = "blocked"
    REVIEW = "review"
    DONE = "done"
    LEARNED = "learned"
    FAILED = "failed"


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_human"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class ReflectionStatus(StrEnum):
    PROPOSED = "proposed"
    EVALUATING = "evaluating"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class Goal:
    title: str
    objective: str
    constraints: list[str] = field(default_factory=list)
    definition_of_done: list[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    budget_amount: Decimal | None = None
    budget_currency: str = "USD"
    due_at: datetime | None = None
    owner_id: str | None = None
    status: GoalStatus = GoalStatus.DRAFT
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Goal.title is required")
        if not self.objective.strip():
            raise ValueError("Goal.objective is required")
        if self.budget_amount is not None and self.budget_amount < 0:
            raise ValueError("Goal.budget_amount must be >= 0")


@dataclass(slots=True)
class Playbook:
    name: str
    source_kind: str
    source_uri: str
    compiled_spec: dict[str, Any] = field(default_factory=dict)
    version: str = "0.1.0"
    status: PlaybookStatus = PlaybookStatus.DRAFT
    goal_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Playbook.name is required")
        if not self.source_kind.strip():
            raise ValueError("Playbook.source_kind is required")
        if not self.source_uri.strip():
            raise ValueError("Playbook.source_uri is required")


@dataclass(slots=True)
class Skill:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    required_mcp_servers: list[str] = field(default_factory=list)
    approval_policy: dict[str, Any] = field(default_factory=dict)
    evaluation_policy: dict[str, Any] = field(default_factory=dict)
    rollback_version: str | None = None
    version: str = "0.1.0"
    status: SkillStatus = SkillStatus.DRAFT
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Skill.name is required")
        if not self.description.strip():
            raise ValueError("Skill.description is required")


@dataclass(slots=True)
class KnowledgeBase:
    name: str
    content: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    source_uri: str | None = None
    goal_id: str | None = None
    status: KnowledgeStatus = KnowledgeStatus.DRAFT
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("KnowledgeBase.name is required")
        if not self.content.strip():
            raise ValueError("KnowledgeBase.content is required")


@dataclass(slots=True)
class MCPServer:
    name: str
    transport: str
    endpoint: str
    scopes: list[str] = field(default_factory=list)
    auth_config: dict[str, Any] = field(default_factory=dict)
    status: MCPServerStatus = MCPServerStatus.ACTIVE
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("MCPServer.name is required")
        if not self.transport.strip():
            raise ValueError("MCPServer.transport is required")
        if not self.endpoint.strip():
            raise ValueError("MCPServer.endpoint is required")


@dataclass(slots=True)
class Task:
    goal_id: str
    playbook_id: str
    name: str
    description: str
    depends_on: list[str] = field(default_factory=list)
    assigned_skill_id: str | None = None
    approval_required: bool = False
    queue_name: str = "default"
    status: TaskStatus = TaskStatus.INBOX
    parent_task_id: str | None = None
    priority: int = 0
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.goal_id.strip():
            raise ValueError("Task.goal_id is required")
        if not self.playbook_id.strip():
            raise ValueError("Task.playbook_id is required")
        if not self.name.strip():
            raise ValueError("Task.name is required")
        if not self.description.strip():
            raise ValueError("Task.description is required")


@dataclass(slots=True)
class Run:
    task_id: str
    worker_type: str
    status: RunStatus = RunStatus.QUEUED
    attempt: int = 1
    trace_id: str | None = None
    session_id: str | None = None
    error_class: str | None = None
    error_message: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("Run.task_id is required")
        if not self.worker_type.strip():
            raise ValueError("Run.worker_type is required")
        if self.attempt < 1:
            raise ValueError("Run.attempt must be >= 1")


@dataclass(slots=True)
class Artifact:
    run_id: str
    kind: str
    title: str
    uri: str
    mime_type: str
    checksum: str | None = None
    version: str = "1"
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.run_id.strip():
            raise ValueError("Artifact.run_id is required")
        if not self.kind.strip():
            raise ValueError("Artifact.kind is required")
        if not self.title.strip():
            raise ValueError("Artifact.title is required")
        if not self.uri.strip():
            raise ValueError("Artifact.uri is required")
        if not self.mime_type.strip():
            raise ValueError("Artifact.mime_type is required")


@dataclass(slots=True)
class Reflection:
    run_id: str
    failure_category: str
    summary: str
    proposal: dict[str, Any]
    eval_status: ReflectionStatus = ReflectionStatus.PROPOSED
    approval_status: str = "pending"
    approved_by: str | None = None
    published_target_version: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.run_id.strip():
            raise ValueError("Reflection.run_id is required")
        if not self.failure_category.strip():
            raise ValueError("Reflection.failure_category is required")
        if not self.summary.strip():
            raise ValueError("Reflection.summary is required")


class SessionKind(StrEnum):
    SUPERVISOR = "supervisor"
    WORKER = "worker"


class SessionStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    FAILED = "failed"


class AcceptanceStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(slots=True)
class Session:
    goal_id: str
    title: str
    kind: SessionKind
    status: SessionStatus = SessionStatus.PLANNED
    task_id: str | None = None
    run_id: str | None = None
    parent_session_id: str | None = None
    objective: str = ""
    input_context: dict[str, Any] = field(default_factory=dict)
    output_context: dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.goal_id.strip():
            raise ValueError("Session.goal_id is required")
        if not self.title.strip():
            raise ValueError("Session.title is required")


@dataclass(slots=True)
class Acceptance:
    goal_id: str
    task_id: str
    criteria: list[str] = field(default_factory=list)
    status: AcceptanceStatus = AcceptanceStatus.PENDING
    artifact_ids: list[str] = field(default_factory=list)
    reviewer_id: str | None = None
    run_id: str | None = None
    notes: str = ""
    findings: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.goal_id.strip():
            raise ValueError("Acceptance.goal_id is required")
        if not self.task_id.strip():
            raise ValueError("Acceptance.task_id is required")


@dataclass(slots=True)
class Event:
    entity_type: str
    entity_id: str
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = "system"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.entity_type.strip():
            raise ValueError("Event.entity_type is required")
        if not self.entity_id.strip():
            raise ValueError("Event.entity_id is required")
        if not self.event_type.strip():
            raise ValueError("Event.event_type is required")
