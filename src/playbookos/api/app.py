from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any


def utc_now() -> datetime:
    return datetime.now(UTC)


from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse

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
    SkillCreate,
    SkillRead,
    PlaybookImport,
    PlaybookRead,
    ReflectionCreate,
    SessionRead,
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
    GoalStatus,
    KnowledgeBase,
    KnowledgeStatus,
    MCPServerStatus,
    Playbook,
    PlaybookStatus,
    Reflection,
    ReflectionStatus,
    RiskLevel,
    Skill,
    Run,
    RunStatus,
    SkillStatus,
    Task,
    TaskStatus,
)
from playbookos.executor import ExecutionError, OpenAIAgentsSDKAdapter, autopilot_goal_in_store, execute_run_in_store
from playbookos.observability import record_error
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
from playbookos.ui import build_dashboard_html


def create_app(store: StoreProtocol | None = None) -> FastAPI:
    api = FastAPI(
        title="PlaybookOS API",
        version="0.1.0",
        description="MVP control plane API for PlaybookOS.",
    )
    api.state.store = store or create_store_from_env()

    def get_store() -> StoreProtocol:
        return api.state.store

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
            mcp_server_statuses=list(MCPServerStatus),
            task_statuses=list(TaskStatus),
            run_statuses=list(RunStatus),
            reflection_statuses=list(ReflectionStatus),
            risk_levels=list(RiskLevel),
        )

    @api.get("/api/board", response_model=BoardSnapshot)
    def get_board(store: store_dep) -> BoardSnapshot:
        return BoardSnapshot.model_validate(store.board_snapshot())

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
            result = autopilot_goal_in_store(store, goal_id, adapter=OpenAIAgentsSDKAdapter())
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

    @api.get("/api/playbooks", response_model=list[PlaybookRead])
    def list_playbooks(store: store_dep) -> list[PlaybookRead]:
        return [PlaybookRead.model_validate(playbook) for playbook in store.playbooks.list()]

    @api.get("/api/playbooks/{playbook_id}", response_model=PlaybookRead)
    def get_playbook(playbook_id: str, store: store_dep) -> PlaybookRead:
        return PlaybookRead.model_validate(_fetch(store.playbooks, playbook_id, "Playbook", operation="get_playbook", metadata={"playbook_id": playbook_id}))

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

    @api.get("/api/skills", response_model=list[SkillRead])
    def list_skills(store: store_dep) -> list[SkillRead]:
        return [SkillRead.model_validate(skill) for skill in store.skills.list()]

    @api.get("/api/skills/{skill_id}", response_model=SkillRead)
    def get_skill(skill_id: str, store: store_dep) -> SkillRead:
        return SkillRead.model_validate(_fetch(store.skills, skill_id, "Skill", operation="get_skill", metadata={"skill_id": skill_id}))

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

    @api.get("/api/sessions", response_model=list[SessionRead])
    def list_sessions(store: store_dep) -> list[SessionRead]:
        return [SessionRead.model_validate(session) for session in store.sessions.list()]

    @api.get("/api/sessions/{session_id}", response_model=SessionRead)
    def get_session(session_id: str, store: store_dep) -> SessionRead:
        return SessionRead.model_validate(_fetch(store.sessions, session_id, "Session", operation="get_session", metadata={"session_id": session_id}))

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
        task = Task(**payload.model_dump())
        store.tasks.save(task)
        return TaskRead.model_validate(task)

    @api.get("/api/tasks", response_model=list[TaskRead])
    def list_tasks(store: store_dep) -> list[TaskRead]:
        return [TaskRead.model_validate(task) for task in store.tasks.list()]

    @api.get("/api/tasks/{task_id}", response_model=TaskRead)
    def get_task(task_id: str, store: store_dep) -> TaskRead:
        return TaskRead.model_validate(_fetch(store.tasks, task_id, "Task", operation="get_task", metadata={"task_id": task_id}))

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
            result = execute_run_in_store(store, run_id, adapter=OpenAIAgentsSDKAdapter())
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
