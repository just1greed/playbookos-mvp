from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from playbookos.domain.models import (
    GoalStatus,
    MCPServerStatus,
    PlaybookStatus,
    ReflectionStatus,
    RiskLevel,
    RunStatus,
    SkillStatus,
    TaskStatus,
)


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class GoalCreate(APIModel):
    title: str
    objective: str
    constraints: list[str] = Field(default_factory=list)
    definition_of_done: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    budget_amount: Decimal | None = None
    budget_currency: str = "USD"
    due_at: datetime | None = None
    owner_id: str | None = None


class GoalRead(GoalCreate):
    id: str
    status: GoalStatus
    created_at: datetime
    updated_at: datetime


class GoalPlanRead(APIModel):
    goal_id: str
    playbook_ids: list[str]
    task_ids: list[str]
    created_count: int
    existing_task_count: int


class TemporalWorkflowSpecRead(APIModel):
    goal_id: str
    task_ids: list[str]
    runnable_task_ids: list[str]
    waiting_human_task_ids: list[str]
    queue_names: dict[str, str]


class GoalDispatchRead(APIModel):
    goal_id: str
    promoted_task_ids: list[str]
    dispatched_task_ids: list[str]
    created_run_ids: list[str]
    waiting_human_task_ids: list[str]
    goal_status: GoalStatus
    temporal_spec: TemporalWorkflowSpecRead


class TaskCompletionRead(APIModel):
    task_id: str
    goal_id: str
    goal_status: GoalStatus
    promoted_task_ids: list[str]
    dispatched_task_ids: list[str]
    created_run_ids: list[str]


class GoalAutopilotRead(APIModel):
    goal_id: str
    goal_status: GoalStatus
    executed_run_ids: list[str]
    completed_task_ids: list[str]
    waiting_human_run_ids: list[str]
    failed_run_ids: list[str]
    reflection_ids: list[str]
    iteration_count: int


class GoalLearningRead(APIModel):
    goal_id: str
    run_count: int
    failed_run_count: int
    reflection_ids: list[str]
    failure_categories: dict[str, int]
    suggested_playbook_patches: list[dict[str, Any]]


class RunExecutionRead(APIModel):
    status: RunStatus
    output_text: str
    trace_id: str
    metrics: dict[str, Any]
    error_class: str | None = None
    error_message: str | None = None
    tool_calls: list[dict[str, Any]]
    artifact_ids: list[str] = Field(default_factory=list)


class ArtifactCreate(APIModel):
    run_id: str
    kind: str
    title: str
    uri: str
    mime_type: str
    checksum: str | None = None
    version: str = "1"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactRead(ArtifactCreate):
    id: str
    created_at: datetime


class RunReflectionRead(APIModel):
    reflection_id: str
    run_id: str
    failure_category: str
    summary: str
    proposal_type: str
    target: str
    eval_status: ReflectionStatus


class ReflectionEvaluationRead(APIModel):
    reflection_id: str
    passed: bool
    score: float
    replay_run_ids: list[str]
    eval_status: ReflectionStatus


class ReflectionPublishRead(APIModel):
    reflection_id: str
    playbook_id: str
    playbook_version: str
    eval_status: ReflectionStatus
    approval_status: str
    published_target_version: str | None = None


class PlaybookImport(APIModel):
    name: str
    source_kind: str
    source_uri: str
    goal_id: str | None = None


class PlaybookRead(PlaybookImport):
    id: str
    compiled_spec: dict[str, Any]
    version: str
    status: PlaybookStatus
    created_at: datetime
    updated_at: datetime


class TaskCreate(APIModel):
    goal_id: str
    playbook_id: str
    name: str
    description: str
    depends_on: list[str] = Field(default_factory=list)
    assigned_skill_id: str | None = None
    approval_required: bool = False
    queue_name: str = "default"
    priority: int = 0
    parent_task_id: str | None = None


class TaskRead(TaskCreate):
    id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class RunCreate(APIModel):
    task_id: str
    worker_type: str
    attempt: int = 1
    status: RunStatus = RunStatus.QUEUED
    trace_id: str | None = None
    session_id: str | None = None


class RunRead(RunCreate):
    id: str
    error_class: str | None = None
    error_message: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime


class ReflectionCreate(APIModel):
    run_id: str
    failure_category: str
    summary: str
    proposal: dict[str, Any]


class ReflectionRead(ReflectionCreate):
    id: str
    eval_status: ReflectionStatus
    approval_status: str
    approved_by: str | None = None
    published_target_version: str | None = None
    created_at: datetime
    updated_at: datetime


class ReflectionPublish(APIModel):
    skill_version: str = ""


class BoardSnapshot(APIModel):
    goals: dict[str, int] = Field(default_factory=dict)
    tasks: dict[str, int] = Field(default_factory=dict)
    runs: dict[str, int] = Field(default_factory=dict)
    artifacts: dict[str, int] = Field(default_factory=dict)
    reflections: dict[str, int] = Field(default_factory=dict)


class EnumCatalog(APIModel):
    goal_statuses: list[GoalStatus]
    playbook_statuses: list[PlaybookStatus]
    skill_statuses: list[SkillStatus]
    mcp_server_statuses: list[MCPServerStatus]
    task_statuses: list[TaskStatus]
    run_statuses: list[RunStatus]
    reflection_statuses: list[ReflectionStatus]
    risk_levels: list[RiskLevel]
