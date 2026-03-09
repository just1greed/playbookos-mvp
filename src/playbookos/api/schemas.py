from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from playbookos.domain.models import (
    GoalStatus,
    MCPServerStatus,
    PlaybookStatus,
    AcceptanceStatus,
    KnowledgeStatus,
    KnowledgeUpdateStatus,
    ReflectionStatus,
    RiskLevel,
    RunStatus,
    SessionKind,
    SessionStatus,
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
    knowledge_update_ids: list[str] = Field(default_factory=list)
    failure_categories: dict[str, int]
    suggested_playbook_patches: list[dict[str, Any]]
    suggested_knowledge_updates: list[dict[str, Any]] = Field(default_factory=list)




class SessionRead(APIModel):
    id: str
    goal_id: str
    task_id: str | None = None
    run_id: str | None = None
    parent_session_id: str | None = None
    title: str
    kind: SessionKind
    status: SessionStatus
    objective: str
    input_context: dict[str, Any] = Field(default_factory=dict)
    output_context: dict[str, Any] = Field(default_factory=dict)
    summary: str
    created_at: datetime
    updated_at: datetime


class SessionUpdate(APIModel):
    title: str | None = None
    status: SessionStatus | None = None
    objective: str | None = None
    summary: str | None = None
    input_context: dict[str, Any] | None = None
    output_context: dict[str, Any] | None = None


class TaskAcceptanceCreate(APIModel):
    criteria: list[str] = Field(default_factory=list)
    reviewer_id: str | None = None
    accepted: bool = True
    notes: str = ""
    findings: list[str] = Field(default_factory=list)


class AcceptanceRead(APIModel):
    id: str
    goal_id: str
    task_id: str
    run_id: str | None = None
    criteria: list[str] = Field(default_factory=list)
    status: AcceptanceStatus
    artifact_ids: list[str] = Field(default_factory=list)
    reviewer_id: str | None = None
    notes: str = ""
    findings: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class TaskAcceptanceRead(APIModel):
    acceptance: AcceptanceRead
    task_status: TaskStatus
    goal_status: GoalStatus
    event_ids: list[str] = Field(default_factory=list)


class EventRead(APIModel):
    id: str
    entity_type: str
    entity_id: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    source: str
    created_at: datetime

class RunExecutionRead(APIModel):
    status: RunStatus
    output_text: str
    trace_id: str
    metrics: dict[str, Any]
    error_class: str | None = None
    error_message: str | None = None
    tool_calls: list[dict[str, Any]]
    artifact_ids: list[str] = Field(default_factory=list)


class StoredObjectRead(APIModel):
    id: str
    kind: str
    title: str
    mime_type: str
    uri: str
    size_bytes: int
    checksum: str
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


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


class SkillSuggestionRead(APIModel):
    name: str
    description: str
    required_mcp_servers: list[str] = Field(default_factory=list)
    rationale: str = ""
    sample_task_names: list[str] = Field(default_factory=list)
    approval_hint: str = ""


class ToolRequirementRead(APIModel):
    tool_name: str
    purpose: str
    rationale: str = ""
    related_steps: list[str] = Field(default_factory=list)
    suggested_skill_name: str = ""
    suggested_mcp_server: str = ""


class PromptBlockRead(APIModel):
    key: str
    title: str
    objective: str
    prompt: str


class ToolingGuidanceRead(APIModel):
    summary: str = ""
    required_mcp_servers: list[str] = Field(default_factory=list)
    suggested_skill_names: list[str] = Field(default_factory=list)
    existing_skill_candidates: list[str] = Field(default_factory=list)
    existing_mcp_candidates: list[str] = Field(default_factory=list)
    missing_mcp_servers: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    tool_requirements: list[ToolRequirementRead] = Field(default_factory=list)
    prompt_blocks: list[PromptBlockRead] = Field(default_factory=list)


class PlaybookIngest(APIModel):
    name: str
    source_text: str
    source_kind: str = "markdown"
    source_uri: str | None = None
    goal_id: str | None = None


class PlaybookImport(APIModel):
    name: str
    source_kind: str
    source_uri: str
    goal_id: str | None = None
    compiled_spec: dict[str, Any] = Field(default_factory=dict)


class PlaybookRead(PlaybookImport):
    id: str
    compiled_spec: dict[str, Any]
    version: str
    status: PlaybookStatus
    created_at: datetime
    updated_at: datetime


class PlaybookIngestRead(APIModel):
    playbook: PlaybookRead
    step_count: int
    detected_mcp_servers: list[str] = Field(default_factory=list)
    suggested_skills: list[SkillSuggestionRead] = Field(default_factory=list)
    parsing_notes: list[str] = Field(default_factory=list)
    tooling_guidance: ToolingGuidanceRead | None = None
    source_object: "StoredObjectRead | None" = None


class PlaybookSkillDraftCreate(APIModel):
    suggestion_index: int = 0
    bind_to_unassigned_steps: bool = False


class PlaybookSkillDraftRead(APIModel):
    playbook_id: str
    suggestion_index: int
    bound_step_count: int = 0
    skill: "SkillRead"


class MCPServerCreate(APIModel):
    name: str
    transport: str
    endpoint: str
    scopes: list[str] = Field(default_factory=list)
    auth_config: dict[str, Any] = Field(default_factory=dict)
    status: MCPServerStatus = MCPServerStatus.INACTIVE


class MCPServerRead(MCPServerCreate):
    id: str
    created_at: datetime
    updated_at: datetime


class PlaybookMCPDraftCreate(APIModel):
    server_name: str


class PlaybookMCPDraftRead(APIModel):
    playbook_id: str
    tool_name: str
    created: bool = True
    mcp_server: MCPServerRead


class SkillAuthoringPackRead(APIModel):
    skill_id: str
    skill_name: str
    playbook_id: str | None = None
    playbook_name: str | None = None
    recommended_input_schema: dict[str, Any] = Field(default_factory=dict)
    recommended_output_schema: dict[str, Any] = Field(default_factory=dict)
    recommended_approval_policy: dict[str, Any] = Field(default_factory=dict)
    recommended_evaluation_policy: dict[str, Any] = Field(default_factory=dict)
    checklist: list[str] = Field(default_factory=list)
    risk_signals: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    linked_step_names: list[str] = Field(default_factory=list)


class SkillAuthoringApplyRead(APIModel):
    skill: "SkillRead"
    authoring_pack: SkillAuthoringPackRead
    applied_fields: list[str] = Field(default_factory=list)




class SkillCreate(APIModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    required_mcp_servers: list[str] = Field(default_factory=list)
    approval_policy: dict[str, Any] = Field(default_factory=dict)
    evaluation_policy: dict[str, Any] = Field(default_factory=dict)
    rollback_version: str | None = None
    version: str = "0.1.0"
    status: SkillStatus = SkillStatus.DRAFT


class SkillRead(SkillCreate):
    id: str
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseCreate(APIModel):
    name: str
    content: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    source_uri: str | None = None
    goal_id: str | None = None
    status: KnowledgeStatus = KnowledgeStatus.DRAFT


class KnowledgeBaseRead(KnowledgeBaseCreate):
    id: str
    created_at: datetime
    updated_at: datetime


class KnowledgeUpdateRead(APIModel):
    id: str
    goal_id: str
    task_id: str
    run_id: str
    title: str
    summary: str
    proposed_content: str
    rationale: str = ""
    knowledge_base_id: str | None = None
    source_reflection_id: str | None = None
    status: KnowledgeUpdateStatus
    applied_by: str | None = None
    created_at: datetime
    updated_at: datetime


class TaskCreate(APIModel):
    goal_id: str
    playbook_id: str
    name: str
    description: str
    depends_on: list[str] = Field(default_factory=list)
    knowledge_base_ids: list[str] = Field(default_factory=list)
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
    playbooks: dict[str, int] = Field(default_factory=dict)
    skills: dict[str, int] = Field(default_factory=dict)
    mcp_servers: dict[str, int] = Field(default_factory=dict)
    knowledge_bases: dict[str, int] = Field(default_factory=dict)
    knowledge_updates: dict[str, int] = Field(default_factory=dict)
    tasks: dict[str, int] = Field(default_factory=dict)
    sessions: dict[str, int] = Field(default_factory=dict)
    runs: dict[str, int] = Field(default_factory=dict)
    artifacts: dict[str, int] = Field(default_factory=dict)
    acceptances: dict[str, int] = Field(default_factory=dict)
    reflections: dict[str, int] = Field(default_factory=dict)
    events: dict[str, int] = Field(default_factory=dict)


class EnumCatalog(APIModel):
    goal_statuses: list[GoalStatus]
    playbook_statuses: list[PlaybookStatus]
    skill_statuses: list[SkillStatus]
    knowledge_statuses: list[KnowledgeStatus]
    knowledge_update_statuses: list[KnowledgeUpdateStatus]
    mcp_server_statuses: list[MCPServerStatus]
    task_statuses: list[TaskStatus]
    run_statuses: list[RunStatus]
    reflection_statuses: list[ReflectionStatus]
    risk_levels: list[RiskLevel]
