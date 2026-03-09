from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any


def utc_now() -> datetime:
    return datetime.now(UTC)


from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, Response

from playbookos.api.schemas import (
    AcceptanceRead,
    ArtifactCreate,
    ArtifactRead,
    BoardSnapshot,
    EnumCatalog,
    EventRead,
    GoalAutopilotRead,
    GoalCreate,
    GoalDispatchRead,
    GoalLearningRead,
    GoalPlanRead,
    GoalRead,
    KnowledgeBaseCreate,
    KnowledgeBaseRead,
    KnowledgeUpdateRead,
    MCPServerCreate,
    MCPServerRead,
    PlaybookIngest,
    PlaybookIngestRead,
    StoredObjectRead,
    PlaybookImport,
    PlaybookMCPDraftCreate,
    PlaybookMCPDraftRead,
    PlaybookSkillDraftCreate,
    PlaybookSkillDraftRead,
    PlaybookRead,
    ReflectionCreate,
    SessionRead,
    SessionUpdate,
    SkillAuthoringApplyRead,
    SkillAuthoringPackRead,
    SkillCreate,
    SkillRead,
    SkillSuggestionRead,
    ToolingGuidanceRead,
    TaskAcceptanceCreate,
    TaskAcceptanceRead,
    ReflectionEvaluationRead,
    ReflectionPublish,
    ReflectionPublishRead,
    ReflectionRead,
    RunCreate,
    RunExecutionRead,
    RunRead,
    RunReflectionRead,
    TaskCompletionRead,
    TaskCreate,
    TaskRead,
    TemporalWorkflowSpecRead,
)
from playbookos.api.store import NotFoundError, RepositoryProtocol, StoreProtocol
from playbookos.domain.models import (
    Artifact,
    Goal,
    MCPServer,
    GoalStatus,
    KnowledgeBase,
    KnowledgeStatus,
    KnowledgeUpdateStatus,
    MCPServerStatus,
    Playbook,
    PlaybookStatus,
    Reflection,
    ReflectionStatus,
    RiskLevel,
    Skill,
    Run,
    RunStatus,
    SessionStatus,
    SkillStatus,
    Task,
    TaskStatus,
)
from playbookos.authoring import apply_skill_authoring_pack_in_store, build_skill_authoring_pack_in_store
from playbookos.executor import ExecutionError, OpenAIAgentsSDKAdapter, autopilot_goal_in_store, execute_run_in_store
from playbookos.ingestion import SOPIngestionError, ingest_sop_in_store, materialize_required_mcp_in_store, materialize_suggested_skill_in_store
from playbookos.object_store import attach_source_object_to_playbook, create_object_store_from_env
from playbookos.observability import record_error
from playbookos.knowledge import KnowledgeUpdateError, apply_knowledge_update_in_store, reject_knowledge_update_in_store
from playbookos.skills_service import SkillLifecycleError, activate_skill_in_store, create_next_skill_version_in_store, deprecate_skill_in_store, rollback_skill_in_store
from playbookos.orchestrator import OrchestrationError, complete_task_in_store, dispatch_goal_in_store
from playbookos.persistence import create_store_from_env
from playbookos.planner import PlanningError, plan_goal_in_store
from playbookos.reflection import (
    ReflectionError,
    analyze_goal_learning,
    approve_reflection_in_store,
    evaluate_reflection_in_store,
    publish_reflection_in_store,
    reflect_run_in_store,
    reject_reflection_in_store,
)
from playbookos.supervisor import AcceptanceError, accept_task_in_store
from playbookos.runtime_settings import create_runtime_settings_store_from_env
from playbookos.ui import build_dashboard_html


def create_app(store: StoreProtocol | None = None) -> FastAPI:
    api = FastAPI(
        title="PlaybookOS API",
        version="0.1.0",
        description="MVP control plane API for PlaybookOS.",
    )
    api.state.store = store or create_store_from_env()
    api.state.runtime_settings = create_runtime_settings_store_from_env()

    def get_store() -> StoreProtocol:
        return api.state.store

    def get_runtime_settings():
        return api.state.runtime_settings

    store_dep = Annotated[StoreProtocol, Depends(get_store)]

    @api.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @api.get("/", response_class=HTMLResponse)
    def dashboard(store: store_dep) -> HTMLResponse:
        return HTMLResponse(build_dashboard_html(store.board_snapshot(), api_base="/api"))

    @api.get("/api/errors", response_model=list[dict[str, Any]])
    def list_errors() -> list[dict[str, Any]]:
        from playbookos.observability import list_recorded_errors

        return list_recorded_errors()

    @api.get("/api/meta/enums", response_model=EnumCatalog)
    def list_enums() -> EnumCatalog:
        return EnumCatalog(
            goal_statuses=list(GoalStatus),
            playbook_statuses=list(PlaybookStatus),
            skill_statuses=list(SkillStatus),
            knowledge_statuses=list(KnowledgeStatus),
            knowledge_update_statuses=list(KnowledgeUpdateStatus),
            mcp_server_statuses=list(MCPServerStatus),
            task_statuses=list(TaskStatus),
            run_statuses=list(RunStatus),
            reflection_statuses=list(ReflectionStatus),
            risk_levels=list(RiskLevel),
        )

    @api.get("/api/board", response_model=BoardSnapshot)
    def get_board(store: store_dep) -> BoardSnapshot:
        return BoardSnapshot.model_validate(store.board_snapshot())

    @api.get("/api/runtime-settings", response_model=dict[str, Any])
    def get_runtime_settings_payload() -> dict[str, Any]:
        return api.state.runtime_settings.get_settings()

    @api.put("/api/runtime-settings", response_model=dict[str, Any])
    def update_runtime_settings(payload: dict[str, Any]) -> dict[str, Any]:
        return api.state.runtime_settings.update_settings(payload)

    @api.post("/api/goals", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
    def create_goal(payload: GoalCreate, store: store_dep) -> GoalRead:
        goal = Goal(**payload.model_dump())
        store.goals.save(goal)
        return GoalRead.model_validate(goal)

    @api.get("/api/goals", response_model=list[GoalRead])
    def list_goals(store: store_dep) -> list[GoalRead]:
        return [GoalRead.model_validate(goal) for goal in store.goals.list()]

    @api.get("/api/goals/{goal_id}", response_model=GoalRead)
    def get_goal(goal_id: str, store: store_dep) -> GoalRead:
        return GoalRead.model_validate(_fetch(store.goals, goal_id, "Goal", operation="get_goal", metadata={"goal_id": goal_id}))

    @api.put("/api/goals/{goal_id}", response_model=GoalRead)
    def update_goal(goal_id: str, payload: GoalCreate, store: store_dep) -> GoalRead:
        goal = _fetch(store.goals, goal_id, "Goal", operation="update_goal", metadata={"goal_id": goal_id})
        for field_name, value in payload.model_dump().items():
            setattr(goal, field_name, value)
        goal.updated_at = utc_now()
        store.goals.save(goal)
        return GoalRead.model_validate(goal)

    @api.post("/api/goals/{goal_id}/plan", response_model=GoalPlanRead)
    def plan_goal(goal_id: str, store: store_dep) -> GoalPlanRead:
        try:
            planning_result = plan_goal_in_store(store, goal_id)
        except PlanningError as exc:
            raise _conflict_http_exception(exc, operation="plan_goal", metadata={"goal_id": goal_id}) from exc
        return GoalPlanRead(
            goal_id=planning_result.goal_id,
            playbook_ids=planning_result.playbook_ids,
            task_ids=[task.id for task in planning_result.created_tasks],
            created_count=planning_result.created_count,
            existing_task_count=planning_result.existing_task_count,
        )

    @api.post("/api/goals/{goal_id}/dispatch", response_model=GoalDispatchRead)
    def dispatch_goal(goal_id: str, store: store_dep) -> GoalDispatchRead:
        try:
            dispatch_result = dispatch_goal_in_store(store, goal_id)
        except OrchestrationError as exc:
            raise _conflict_http_exception(exc, operation="dispatch_goal", metadata={"goal_id": goal_id}) from exc
        return _dispatch_read(dispatch_result)

    @api.post("/api/goals/{goal_id}/autopilot", response_model=GoalAutopilotRead)
    def autopilot_goal(goal_id: str, store: store_dep) -> GoalAutopilotRead:
        try:
            plan_goal_in_store(store, goal_id)
            result = autopilot_goal_in_store(store, goal_id, adapter=OpenAIAgentsSDKAdapter(config=api.state.runtime_settings.openai_config()))
        except (PlanningError, OrchestrationError, ExecutionError, ReflectionError) as exc:
            raise _conflict_http_exception(exc, operation="autopilot_goal", metadata={"goal_id": goal_id}) from exc
        return GoalAutopilotRead.model_validate(result)

    @api.get("/api/goals/{goal_id}/learning", response_model=GoalLearningRead)
    def get_goal_learning(goal_id: str, store: store_dep) -> GoalLearningRead:
        _fetch(store.goals, goal_id, "Goal", operation="get_goal_learning", metadata={"goal_id": goal_id})
        return GoalLearningRead.model_validate(analyze_goal_learning(store, goal_id))

    @api.post("/api/goals/{goal_id}/start", response_model=GoalRead)
    def start_goal(goal_id: str, store: store_dep) -> GoalRead:
        try:
            plan_goal_in_store(store, goal_id)
            dispatch_goal_in_store(store, goal_id)
        except (PlanningError, OrchestrationError) as exc:
            raise _conflict_http_exception(exc, operation="start_goal", metadata={"goal_id": goal_id}) from exc
        goal = _fetch(store.goals, goal_id, "Goal", operation="goal_lookup", metadata={"goal_id": goal_id})
        return GoalRead.model_validate(goal)

    @api.post("/api/goals/{goal_id}/complete-review", response_model=GoalRead)
    def complete_goal_review(goal_id: str, store: store_dep) -> GoalRead:
        goal = _fetch(store.goals, goal_id, "Goal", operation="goal_lookup", metadata={"goal_id": goal_id})
        goal.status = GoalStatus.DONE
        goal.updated_at = utc_now()
        store.goals.save(goal)
        return GoalRead.model_validate(goal)

    @api.post("/api/playbooks/import", response_model=PlaybookRead, status_code=status.HTTP_201_CREATED)
    def import_playbook(payload: PlaybookImport, store: store_dep) -> PlaybookRead:
        if payload.goal_id is not None:
            _fetch(store.goals, payload.goal_id, "Goal", operation="import_playbook", metadata={"goal_id": payload.goal_id})
        playbook = Playbook(**payload.model_dump())
        if playbook.compiled_spec.get("steps"):
            playbook.status = PlaybookStatus.COMPILED
        store.playbooks.save(playbook)
        return PlaybookRead.model_validate(playbook)

    @api.post("/api/playbooks/ingest", response_model=PlaybookIngestRead, status_code=status.HTTP_201_CREATED)
    def ingest_playbook(payload: PlaybookIngest, store: store_dep) -> PlaybookIngestRead:
        try:
            result = ingest_sop_in_store(
                store,
                name=payload.name,
                source_text=payload.source_text,
                source_kind=payload.source_kind,
                source_uri=payload.source_uri,
                goal_id=payload.goal_id,
            )
            source_object = attach_source_object_to_playbook(
                result.playbook,
                source_text=payload.source_text,
                source_kind=payload.source_kind,
                source_uri=payload.source_uri,
                object_store=create_object_store_from_env(),
            )
            store.playbooks.save(result.playbook)
        except SOPIngestionError as exc:
            raise _conflict_http_exception(exc, operation="ingest_playbook", metadata={"goal_id": payload.goal_id}) from exc
        return PlaybookIngestRead(
            playbook=PlaybookRead.model_validate(result.playbook),
            step_count=result.step_count,
            detected_mcp_servers=result.detected_mcp_servers,
            suggested_skills=[SkillSuggestionRead.model_validate(item) for item in result.suggested_skills],
            parsing_notes=result.parsing_notes,
            tooling_guidance=ToolingGuidanceRead.model_validate(result.tooling_guidance) if result.tooling_guidance else None,
            source_object=StoredObjectRead.model_validate(source_object),
        )

    @api.post("/api/playbooks/{playbook_id}/skill-drafts", response_model=PlaybookSkillDraftRead, status_code=status.HTTP_201_CREATED)
    def create_playbook_skill_draft(playbook_id: str, payload: PlaybookSkillDraftCreate, store: store_dep) -> PlaybookSkillDraftRead:
        try:
            result = materialize_suggested_skill_in_store(
                store,
                playbook_id,
                suggestion_index=payload.suggestion_index,
                bind_to_unassigned_steps=payload.bind_to_unassigned_steps,
            )
        except SOPIngestionError as exc:
            raise _conflict_http_exception(exc, operation="create_playbook_skill_draft", metadata={"playbook_id": playbook_id}) from exc
        return PlaybookSkillDraftRead(
            playbook_id=result.playbook.id,
            suggestion_index=result.suggestion_index,
            bound_step_count=result.bound_step_count,
            skill=SkillRead.model_validate(result.skill),
        )

    @api.post("/api/playbooks/{playbook_id}/mcp-drafts", response_model=PlaybookMCPDraftRead, status_code=status.HTTP_201_CREATED)
    def create_playbook_mcp_draft(playbook_id: str, payload: PlaybookMCPDraftCreate, store: store_dep) -> PlaybookMCPDraftRead:
        try:
            result = materialize_required_mcp_in_store(store, playbook_id, server_name=payload.server_name)
        except SOPIngestionError as exc:
            raise _conflict_http_exception(exc, operation="create_playbook_mcp_draft", metadata={"playbook_id": playbook_id, "server_name": payload.server_name}) from exc
        return PlaybookMCPDraftRead(
            playbook_id=result.playbook.id,
            tool_name=result.tool_name,
            created=result.created,
            mcp_server=MCPServerRead.model_validate(result.mcp_server),
        )

    @api.get("/api/playbooks", response_model=list[PlaybookRead])
    def list_playbooks(store: store_dep) -> list[PlaybookRead]:
        return [PlaybookRead.model_validate(playbook) for playbook in store.playbooks.list()]

    @api.get("/api/playbooks/{playbook_id}", response_model=PlaybookRead)
    def get_playbook(playbook_id: str, store: store_dep) -> PlaybookRead:
        return PlaybookRead.model_validate(_fetch(store.playbooks, playbook_id, "Playbook", operation="get_playbook", metadata={"playbook_id": playbook_id}))

    @api.put("/api/playbooks/{playbook_id}", response_model=PlaybookRead)
    def update_playbook(playbook_id: str, payload: PlaybookImport, store: store_dep) -> PlaybookRead:
        playbook = _fetch(store.playbooks, playbook_id, "Playbook", operation="update_playbook", metadata={"playbook_id": playbook_id})
        if payload.goal_id is not None:
            _fetch(store.goals, payload.goal_id, "Goal", operation="update_playbook", metadata={"goal_id": payload.goal_id})
        playbook.name = payload.name
        playbook.source_kind = payload.source_kind
        playbook.source_uri = payload.source_uri
        playbook.goal_id = payload.goal_id
        playbook.compiled_spec = dict(payload.compiled_spec)
        if playbook.status == PlaybookStatus.DRAFT and playbook.compiled_spec.get("steps"):
            playbook.status = PlaybookStatus.COMPILED
        playbook.updated_at = utc_now()
        store.playbooks.save(playbook)
        return PlaybookRead.model_validate(playbook)

    @api.post("/api/playbooks/{playbook_id}/compile", response_model=PlaybookRead)
    def compile_playbook(playbook_id: str, store: store_dep) -> PlaybookRead:
        playbook = _fetch(store.playbooks, playbook_id, "Playbook", operation="compile_playbook", metadata={"playbook_id": playbook_id})
        playbook.status = PlaybookStatus.COMPILED
        playbook.compiled_spec = {
            "playbook_id": playbook.id,
            "compiled_at": utc_now().isoformat(),
            "steps": playbook.compiled_spec.get("steps", []),
            "mcp_servers": playbook.compiled_spec.get("mcp_servers", []),
        }
        playbook.updated_at = utc_now()
        store.playbooks.save(playbook)
        return PlaybookRead.model_validate(playbook)

    @api.post("/api/skills", response_model=SkillRead, status_code=status.HTTP_201_CREATED)
    def create_skill(payload: SkillCreate, store: store_dep) -> SkillRead:
        skill = Skill(**payload.model_dump())
        store.skills.save(skill)
        return SkillRead.model_validate(skill)

    @api.get("/api/skills/{skill_id}/authoring-pack", response_model=SkillAuthoringPackRead)
    def get_skill_authoring_pack(skill_id: str, store: store_dep) -> SkillAuthoringPackRead:
        pack = build_skill_authoring_pack_in_store(store, skill_id)
        return SkillAuthoringPackRead.model_validate(pack)

    @api.post("/api/skills/{skill_id}/apply-authoring-pack", response_model=SkillAuthoringApplyRead)
    def apply_skill_authoring_pack(skill_id: str, store: store_dep) -> SkillAuthoringApplyRead:
        result = apply_skill_authoring_pack_in_store(store, skill_id)
        return SkillAuthoringApplyRead(
            skill=SkillRead.model_validate(result.skill),
            authoring_pack=SkillAuthoringPackRead.model_validate(result.authoring_pack),
            applied_fields=result.applied_fields,
        )

    @api.get("/api/skills", response_model=list[SkillRead])
    def list_skills(store: store_dep) -> list[SkillRead]:
        return [SkillRead.model_validate(skill) for skill in store.skills.list()]

    @api.get("/api/skills/{skill_id}", response_model=SkillRead)
    def get_skill(skill_id: str, store: store_dep) -> SkillRead:
        return SkillRead.model_validate(_fetch(store.skills, skill_id, "Skill", operation="get_skill", metadata={"skill_id": skill_id}))

    @api.put("/api/skills/{skill_id}", response_model=SkillRead)
    def update_skill(skill_id: str, payload: SkillCreate, store: store_dep) -> SkillRead:
        skill = _fetch(store.skills, skill_id, "Skill", operation="update_skill", metadata={"skill_id": skill_id})
        for field_name, value in payload.model_dump().items():
            setattr(skill, field_name, value)
        skill.updated_at = utc_now()
        store.skills.save(skill)
        return SkillRead.model_validate(skill)


    @api.post("/api/skills/{skill_id}/create-version", response_model=SkillRead)
    def create_skill_version(skill_id: str, store: store_dep) -> SkillRead:
        try:
            result = create_next_skill_version_in_store(store, skill_id)
        except SkillLifecycleError as exc:
            raise _conflict_http_exception(exc, operation="create_skill_version", metadata={"skill_id": skill_id}) from exc
        return SkillRead.model_validate(result.skill)

    @api.post("/api/skills/{skill_id}/activate", response_model=SkillRead)
    def activate_skill(skill_id: str, store: store_dep) -> SkillRead:
        try:
            result = activate_skill_in_store(store, skill_id)
        except SkillLifecycleError as exc:
            raise _conflict_http_exception(exc, operation="activate_skill", metadata={"skill_id": skill_id}) from exc
        return SkillRead.model_validate(result.skill)

    @api.post("/api/skills/{skill_id}/deprecate", response_model=SkillRead)
    def deprecate_skill(skill_id: str, store: store_dep) -> SkillRead:
        try:
            result = deprecate_skill_in_store(store, skill_id)
        except SkillLifecycleError as exc:
            raise _conflict_http_exception(exc, operation="deprecate_skill", metadata={"skill_id": skill_id}) from exc
        return SkillRead.model_validate(result.skill)

    @api.post("/api/skills/{skill_id}/rollback", response_model=SkillRead)
    def rollback_skill(skill_id: str, store: store_dep) -> SkillRead:
        try:
            result = rollback_skill_in_store(store, skill_id)
        except SkillLifecycleError as exc:
            raise _conflict_http_exception(exc, operation="rollback_skill", metadata={"skill_id": skill_id}) from exc
        return SkillRead.model_validate(result.active_skill)

    @api.post("/api/mcp-servers", response_model=MCPServerRead, status_code=status.HTTP_201_CREATED)
    def create_mcp_server(payload: MCPServerCreate, store: store_dep) -> MCPServerRead:
        item = MCPServer(**payload.model_dump())
        store.mcp_servers.save(item)
        return MCPServerRead.model_validate(item)

    @api.get("/api/mcp-servers", response_model=list[MCPServerRead])
    def list_mcp_servers(store: store_dep) -> list[MCPServerRead]:
        return [MCPServerRead.model_validate(item) for item in store.mcp_servers.list()]

    @api.get("/api/mcp-servers/{mcp_server_id}", response_model=MCPServerRead)
    def get_mcp_server(mcp_server_id: str, store: store_dep) -> MCPServerRead:
        return MCPServerRead.model_validate(_fetch(store.mcp_servers, mcp_server_id, "MCPServer", operation="get_mcp_server", metadata={"mcp_server_id": mcp_server_id}))

    @api.put("/api/mcp-servers/{mcp_server_id}", response_model=MCPServerRead)
    def update_mcp_server(mcp_server_id: str, payload: MCPServerCreate, store: store_dep) -> MCPServerRead:
        item = _fetch(store.mcp_servers, mcp_server_id, "MCPServer", operation="update_mcp_server", metadata={"mcp_server_id": mcp_server_id})
        for field_name, value in payload.model_dump().items():
            setattr(item, field_name, value)
        item.updated_at = utc_now()
        store.mcp_servers.save(item)
        return MCPServerRead.model_validate(item)

    @api.post("/api/knowledge-bases", response_model=KnowledgeBaseRead, status_code=status.HTTP_201_CREATED)
    def create_knowledge_base(payload: KnowledgeBaseCreate, store: store_dep) -> KnowledgeBaseRead:
        if payload.goal_id is not None:
            _fetch(store.goals, payload.goal_id, "Goal", operation="create_knowledge_base", metadata={"goal_id": payload.goal_id})
        item = KnowledgeBase(**payload.model_dump())
        store.knowledge_bases.save(item)
        return KnowledgeBaseRead.model_validate(item)

    @api.get("/api/knowledge-bases", response_model=list[KnowledgeBaseRead])
    def list_knowledge_bases(store: store_dep) -> list[KnowledgeBaseRead]:
        return [KnowledgeBaseRead.model_validate(item) for item in store.knowledge_bases.list()]

    @api.get("/api/knowledge-bases/{knowledge_id}", response_model=KnowledgeBaseRead)
    def get_knowledge_base(knowledge_id: str, store: store_dep) -> KnowledgeBaseRead:
        return KnowledgeBaseRead.model_validate(_fetch(store.knowledge_bases, knowledge_id, "KnowledgeBase", operation="get_knowledge_base", metadata={"knowledge_id": knowledge_id}))

    @api.get("/api/knowledge-updates", response_model=list[KnowledgeUpdateRead])
    def list_knowledge_updates(store: store_dep) -> list[KnowledgeUpdateRead]:
        return [KnowledgeUpdateRead.model_validate(item) for item in store.knowledge_updates.list()]

    @api.get("/api/knowledge-updates/{knowledge_update_id}", response_model=KnowledgeUpdateRead)
    def get_knowledge_update(knowledge_update_id: str, store: store_dep) -> KnowledgeUpdateRead:
        return KnowledgeUpdateRead.model_validate(_fetch(store.knowledge_updates, knowledge_update_id, "KnowledgeUpdate", operation="get_knowledge_update", metadata={"knowledge_update_id": knowledge_update_id}))

    @api.post("/api/knowledge-updates/{knowledge_update_id}/apply", response_model=KnowledgeUpdateRead)
    def apply_knowledge_update(knowledge_update_id: str, store: store_dep) -> KnowledgeUpdateRead:
        try:
            result = apply_knowledge_update_in_store(store, knowledge_update_id, applied_by="human")
        except KnowledgeUpdateError as exc:
            raise _conflict_http_exception(exc, operation="apply_knowledge_update", metadata={"knowledge_update_id": knowledge_update_id}) from exc
        return KnowledgeUpdateRead.model_validate(result.knowledge_update)

    @api.post("/api/knowledge-updates/{knowledge_update_id}/reject", response_model=KnowledgeUpdateRead)
    def reject_knowledge_update(knowledge_update_id: str, store: store_dep) -> KnowledgeUpdateRead:
        try:
            item = reject_knowledge_update_in_store(store, knowledge_update_id, rejected_by="human")
        except KnowledgeUpdateError as exc:
            raise _conflict_http_exception(exc, operation="reject_knowledge_update", metadata={"knowledge_update_id": knowledge_update_id}) from exc
        return KnowledgeUpdateRead.model_validate(item)

    @api.put("/api/knowledge-bases/{knowledge_id}", response_model=KnowledgeBaseRead)
    def update_knowledge_base(knowledge_id: str, payload: KnowledgeBaseCreate, store: store_dep) -> KnowledgeBaseRead:
        item = _fetch(store.knowledge_bases, knowledge_id, "KnowledgeBase", operation="update_knowledge_base", metadata={"knowledge_id": knowledge_id})
        if payload.goal_id is not None:
            _fetch(store.goals, payload.goal_id, "Goal", operation="update_knowledge_base", metadata={"goal_id": payload.goal_id})
        for field_name, value in payload.model_dump().items():
            setattr(item, field_name, value)
        item.updated_at = utc_now()
        store.knowledge_bases.save(item)
        return KnowledgeBaseRead.model_validate(item)

    @api.get("/api/sessions", response_model=list[SessionRead])
    def list_sessions(store: store_dep) -> list[SessionRead]:
        return [SessionRead.model_validate(session) for session in store.sessions.list()]

    @api.get("/api/sessions/{session_id}", response_model=SessionRead)
    def get_session(session_id: str, store: store_dep) -> SessionRead:
        return SessionRead.model_validate(_fetch(store.sessions, session_id, "Session", operation="get_session", metadata={"session_id": session_id}))

    @api.put("/api/sessions/{session_id}", response_model=SessionRead)
    def update_session(session_id: str, payload: SessionUpdate, store: store_dep) -> SessionRead:
        session = _fetch(store.sessions, session_id, "Session", operation="update_session", metadata={"session_id": session_id})
        data = payload.model_dump(exclude_none=True)
        if "title" in data:
            session.title = data["title"]
        if "status" in data:
            session.status = SessionStatus(data["status"])
        if "objective" in data:
            session.objective = data["objective"]
        if "summary" in data:
            session.summary = data["summary"]
        if "input_context" in data:
            session.input_context = dict(data["input_context"] or {})
        if "output_context" in data:
            session.output_context = dict(data["output_context"] or {})
        session.updated_at = utc_now()
        store.sessions.save(session)
        return SessionRead.model_validate(session)

    @api.get("/api/acceptances", response_model=list[AcceptanceRead])
    def list_acceptances(store: store_dep) -> list[AcceptanceRead]:
        return [AcceptanceRead.model_validate(item) for item in store.acceptances.list()]

    @api.get("/api/acceptances/{acceptance_id}", response_model=AcceptanceRead)
    def get_acceptance(acceptance_id: str, store: store_dep) -> AcceptanceRead:
        return AcceptanceRead.model_validate(_fetch(store.acceptances, acceptance_id, "Acceptance", operation="get_acceptance", metadata={"acceptance_id": acceptance_id}))

    @api.get("/api/events", response_model=list[EventRead])
    def list_events(store: store_dep) -> list[EventRead]:
        return [EventRead.model_validate(item) for item in store.events.list()]

    @api.post("/api/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
    def create_task(payload: TaskCreate, store: store_dep) -> TaskRead:
        _fetch(store.goals, payload.goal_id, "Goal", operation="create_task", metadata={"goal_id": payload.goal_id})
        _fetch(store.playbooks, payload.playbook_id, "Playbook", operation="create_task", metadata={"playbook_id": payload.playbook_id})
        if payload.assigned_skill_id is not None:
            _fetch(store.skills, payload.assigned_skill_id, "Skill", operation="create_task", metadata={"assigned_skill_id": payload.assigned_skill_id})
        for knowledge_id in payload.knowledge_base_ids:
            _fetch(store.knowledge_bases, knowledge_id, "KnowledgeBase", operation="create_task", metadata={"knowledge_id": knowledge_id})
        task = Task(**payload.model_dump())
        store.tasks.save(task)
        return TaskRead.model_validate(task)

    @api.get("/api/tasks", response_model=list[TaskRead])
    def list_tasks(store: store_dep) -> list[TaskRead]:
        return [TaskRead.model_validate(task) for task in store.tasks.list()]

    @api.get("/api/tasks/{task_id}", response_model=TaskRead)
    def get_task(task_id: str, store: store_dep) -> TaskRead:
        return TaskRead.model_validate(_fetch(store.tasks, task_id, "Task", operation="get_task", metadata={"task_id": task_id}))

    @api.put("/api/tasks/{task_id}", response_model=TaskRead)
    def update_task(task_id: str, payload: TaskCreate, store: store_dep) -> TaskRead:
        task = _fetch(store.tasks, task_id, "Task", operation="update_task", metadata={"task_id": task_id})
        _fetch(store.goals, payload.goal_id, "Goal", operation="update_task", metadata={"goal_id": payload.goal_id})
        _fetch(store.playbooks, payload.playbook_id, "Playbook", operation="update_task", metadata={"playbook_id": payload.playbook_id})
        if payload.assigned_skill_id is not None:
            _fetch(store.skills, payload.assigned_skill_id, "Skill", operation="update_task", metadata={"assigned_skill_id": payload.assigned_skill_id})
        for knowledge_id in payload.knowledge_base_ids:
            _fetch(store.knowledge_bases, knowledge_id, "KnowledgeBase", operation="update_task", metadata={"knowledge_id": knowledge_id})
        for field_name, value in payload.model_dump().items():
            setattr(task, field_name, value)
        task.updated_at = utc_now()
        store.tasks.save(task)
        return TaskRead.model_validate(task)

    @api.post("/api/tasks/{task_id}/accept", response_model=TaskAcceptanceRead)
    def accept_task(task_id: str, payload: TaskAcceptanceCreate, store: store_dep) -> TaskAcceptanceRead:
        try:
            result = accept_task_in_store(
                store,
                task_id,
                criteria=payload.criteria,
                reviewer_id=payload.reviewer_id,
                accepted=payload.accepted,
                notes=payload.notes,
                findings=payload.findings,
            )
        except AcceptanceError as exc:
            raise _conflict_http_exception(exc, operation="accept_task", metadata={"task_id": task_id}) from exc
        return TaskAcceptanceRead(
            acceptance=AcceptanceRead.model_validate(result.acceptance),
            task_status=result.task_status,
            goal_status=result.goal_status,
            event_ids=result.event_ids,
        )

    @api.post("/api/tasks/{task_id}/complete", response_model=TaskCompletionRead)
    def complete_task(task_id: str, store: store_dep) -> TaskCompletionRead:
        try:
            result = complete_task_in_store(store, task_id)
        except OrchestrationError as exc:
            raise _conflict_http_exception(exc, operation="complete_task", metadata={"task_id": task_id}) from exc
        return TaskCompletionRead.model_validate(result)

    @api.post("/api/runs", response_model=RunRead, status_code=status.HTTP_201_CREATED)
    def create_run(payload: RunCreate, store: store_dep) -> RunRead:
        _fetch(store.tasks, payload.task_id, "Task", operation="create_run", metadata={"task_id": payload.task_id})
        run = Run(**payload.model_dump())
        store.runs.save(run)
        return RunRead.model_validate(run)

    @api.get("/api/runs", response_model=list[RunRead])
    def list_runs(store: store_dep) -> list[RunRead]:
        return [RunRead.model_validate(run) for run in store.runs.list()]

    @api.get("/api/runs/{run_id}", response_model=RunRead)
    def get_run(run_id: str, store: store_dep) -> RunRead:
        return RunRead.model_validate(_fetch(store.runs, run_id, "Run", operation="get_run", metadata={"run_id": run_id}))

    @api.post("/api/runs/{run_id}/execute", response_model=RunExecutionRead)
    def execute_run(run_id: str, store: store_dep) -> RunExecutionRead:
        try:
            result = execute_run_in_store(store, run_id, adapter=OpenAIAgentsSDKAdapter(config=api.state.runtime_settings.openai_config()))
            if result.status == RunStatus.SUCCEEDED:
                run = _fetch(store.runs, run_id, "Run", operation="execute_run_lookup", metadata={"run_id": run_id})
                complete_task_in_store(store, run.task_id)
        except (ExecutionError, OrchestrationError) as exc:
            raise _conflict_http_exception(exc, operation="execute_run", metadata={"run_id": run_id}) from exc
        return RunExecutionRead.model_validate(result)

    @api.post("/api/artifacts", response_model=ArtifactRead, status_code=status.HTTP_201_CREATED)
    def create_artifact(payload: ArtifactCreate, store: store_dep) -> ArtifactRead:
        _fetch(store.runs, payload.run_id, "Run", operation="create_artifact", metadata={"run_id": payload.run_id})
        artifact = Artifact(**payload.model_dump())
        store.artifacts.save(artifact)
        return ArtifactRead.model_validate(artifact)

    @api.get("/api/artifacts", response_model=list[ArtifactRead])
    def list_artifacts(store: store_dep) -> list[ArtifactRead]:
        return [ArtifactRead.model_validate(artifact) for artifact in store.artifacts.list()]

    @api.get("/api/artifacts/{artifact_id}", response_model=ArtifactRead)
    def get_artifact(artifact_id: str, store: store_dep) -> ArtifactRead:
        return ArtifactRead.model_validate(_fetch(store.artifacts, artifact_id, "Artifact", operation="get_artifact", metadata={"artifact_id": artifact_id}))

    @api.get("/api/objects", response_model=list[StoredObjectRead])
    def list_objects() -> list[StoredObjectRead]:
        return [StoredObjectRead.model_validate(item) for item in create_object_store_from_env().list_objects()]

    @api.get("/api/objects/{object_id}", response_model=StoredObjectRead)
    def get_object(object_id: str) -> StoredObjectRead:
        try:
            stored = create_object_store_from_env().get_meta(object_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found") from exc
        return StoredObjectRead.model_validate(stored)

    @api.get("/api/objects/{object_id}/content", response_class=Response)
    def get_object_content(object_id: str) -> Response:
        try:
            object_store = create_object_store_from_env()
            stored = object_store.get_meta(object_id)
            body = object_store.get_bytes(object_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Object not found") from exc
        return Response(content=body, media_type=stored.mime_type)

    @api.post("/api/runs/{run_id}/reflect", response_model=RunReflectionRead)
    def reflect_run(run_id: str, store: store_dep) -> RunReflectionRead:
        try:
            result = reflect_run_in_store(store, run_id)
        except ReflectionError as exc:
            raise _conflict_http_exception(exc, operation="reflect_run", metadata={"run_id": run_id}) from exc
        reflection = result.reflection
        return RunReflectionRead(
            reflection_id=reflection.id,
            run_id=reflection.run_id,
            failure_category=reflection.failure_category,
            summary=reflection.summary,
            proposal_type=result.proposal_type,
            target=result.target,
            eval_status=reflection.eval_status,
        )

    @api.post("/api/runs/{run_id}/approve", response_model=RunRead)
    def approve_run(run_id: str, store: store_dep) -> RunRead:
        run = _fetch(store.runs, run_id, "Run", operation="approve_run", metadata={"run_id": run_id})
        task = _fetch(store.tasks, run.task_id, "Task")
        run.status = RunStatus.QUEUED
        run.started_at = run.started_at or utc_now()
        task.status = TaskStatus.RUNNING
        task.updated_at = utc_now()
        store.runs.save(run)
        store.tasks.save(task)
        return RunRead.model_validate(run)

    @api.post("/api/runs/{run_id}/reject", response_model=RunRead)
    def reject_run(run_id: str, store: store_dep) -> RunRead:
        run = _fetch(store.runs, run_id, "Run")
        task = _fetch(store.tasks, run.task_id, "Task")
        run.status = RunStatus.FAILED
        run.finished_at = utc_now()
        run.error_class = "human_rejected"
        run.error_message = "Run rejected by human review"
        task.status = TaskStatus.FAILED
        task.updated_at = utc_now()
        store.runs.save(run)
        store.tasks.save(task)
        goal = _fetch(store.goals, task.goal_id, "Goal")
        goal.status = GoalStatus.BLOCKED
        goal.updated_at = utc_now()
        store.goals.save(goal)
        return RunRead.model_validate(run)

    @api.post("/api/reflections", response_model=ReflectionRead, status_code=status.HTTP_201_CREATED)
    def create_reflection(payload: ReflectionCreate, store: store_dep) -> ReflectionRead:
        _fetch(store.runs, payload.run_id, "Run", operation="create_reflection", metadata={"run_id": payload.run_id})
        reflection = Reflection(**payload.model_dump())
        store.reflections.save(reflection)
        return ReflectionRead.model_validate(reflection)

    @api.get("/api/reflections", response_model=list[ReflectionRead])
    def list_reflections(store: store_dep) -> list[ReflectionRead]:
        return [ReflectionRead.model_validate(item) for item in store.reflections.list()]

    @api.post("/api/reflections/{reflection_id}/evaluate", response_model=ReflectionEvaluationRead)
    def evaluate_reflection(reflection_id: str, store: store_dep) -> ReflectionEvaluationRead:
        try:
            result = evaluate_reflection_in_store(store, reflection_id)
        except ReflectionError as exc:
            raise _conflict_http_exception(exc, operation="evaluate_reflection", metadata={"reflection_id": reflection_id}) from exc
        return ReflectionEvaluationRead(
            reflection_id=result.reflection.id,
            passed=result.passed,
            score=result.score,
            replay_run_ids=result.replay_run_ids,
            eval_status=result.reflection.eval_status,
        )

    @api.post("/api/reflections/{reflection_id}/approve", response_model=ReflectionRead)
    def approve_reflection(reflection_id: str, store: store_dep) -> ReflectionRead:
        try:
            reflection = approve_reflection_in_store(store, reflection_id, approved_by="human")
        except ReflectionError as exc:
            raise _conflict_http_exception(exc, operation="approve_reflection", metadata={"reflection_id": reflection_id}) from exc
        return ReflectionRead.model_validate(reflection)

    @api.post("/api/reflections/{reflection_id}/reject", response_model=ReflectionRead)
    def reject_reflection(reflection_id: str, store: store_dep) -> ReflectionRead:
        reflection = reject_reflection_in_store(store, reflection_id, approved_by="human")
        return ReflectionRead.model_validate(reflection)

    @api.post("/api/reflections/{reflection_id}/publish", response_model=ReflectionPublishRead)
    def publish_reflection(reflection_id: str, payload: ReflectionPublish, store: store_dep) -> ReflectionPublishRead:
        del payload
        try:
            result = publish_reflection_in_store(store, reflection_id)
        except ReflectionError as exc:
            raise _conflict_http_exception(exc, operation="publish_reflection", metadata={"reflection_id": reflection_id}) from exc
        return ReflectionPublishRead(
            reflection_id=result.reflection.id,
            playbook_id=result.playbook.id,
            playbook_version=result.playbook.version,
            eval_status=result.reflection.eval_status,
            approval_status=result.reflection.approval_status,
            published_target_version=result.reflection.published_target_version,
        )

    return api


app = create_app()


def _fetch(repository: RepositoryProtocol, item_id: str, entity_name: str, *, operation: str | None = None, metadata: dict[str, Any] | None = None):
    try:
        return repository.get(item_id)
    except NotFoundError as exc:
        record_error(exc, component="api", operation=operation or f"fetch_{entity_name.lower()}", metadata={"entity_name": entity_name, "item_id": item_id, **(metadata or {})})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_name} not found") from exc



def _conflict_http_exception(exc: Exception, *, operation: str, metadata: dict[str, Any] | None = None) -> HTTPException:
    record_error(exc, component="api", operation=operation, metadata=metadata or {})
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


def _dispatch_read(dispatch_result) -> GoalDispatchRead:
    temporal_spec = dispatch_result.temporal_spec
    return GoalDispatchRead(
        goal_id=dispatch_result.goal_id,
        promoted_task_ids=dispatch_result.promoted_task_ids,
        dispatched_task_ids=dispatch_result.dispatched_task_ids,
        created_run_ids=dispatch_result.created_run_ids,
        waiting_human_task_ids=dispatch_result.waiting_human_task_ids,
        goal_status=dispatch_result.goal_status,
        temporal_spec=TemporalWorkflowSpecRead(
            goal_id=temporal_spec.goal_id,
            task_ids=temporal_spec.task_ids,
            runnable_task_ids=temporal_spec.runnable_task_ids,
            waiting_human_task_ids=temporal_spec.waiting_human_task_ids,
            queue_names=temporal_spec.queue_names,
        ),
    )



def main() -> None:
    import uvicorn

    uvicorn.run("playbookos.api.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
