from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib import error, request
from uuid import uuid4

from playbookos.api.store import StoreProtocol
from playbookos.domain.models import Artifact, GoalStatus, RunStatus, SessionStatus, TaskStatus, utc_now
from playbookos.orchestrator.service import complete_task_in_store, dispatch_goal_in_store
from playbookos.reflection.service import reflect_run_in_store
from playbookos.supervisor import (
    append_event,
    ensure_worker_session_for_run,
    record_child_session,
    refresh_goal_supervisor_session,
    update_session_for_run,
)


class ExecutionError(ValueError):
    pass


@dataclass(slots=True)
class ExecutionContext:
    goal_id: str
    goal_title: str
    objective: str
    task_id: str
    task_name: str
    task_description: str
    playbook_id: str
    playbook_name: str
    playbook_version: str
    compiled_steps: list[dict[str, Any] | str]
    mcp_servers: list[str] = field(default_factory=list)
    knowledge_items: list[dict[str, Any]] = field(default_factory=list)
    skill_id: str | None = None
    approval_required: bool = False


@dataclass(slots=True)
class ExecutionResult:
    status: RunStatus
    output_text: str
    trace_id: str
    metrics: dict[str, Any] = field(default_factory=dict)
    error_class: str | None = None
    error_message: str | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    artifact_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GoalAutopilotResult:
    goal_id: str
    goal_status: GoalStatus
    executed_run_ids: list[str] = field(default_factory=list)
    completed_task_ids: list[str] = field(default_factory=list)
    waiting_human_run_ids: list[str] = field(default_factory=list)
    failed_run_ids: list[str] = field(default_factory=list)
    reflection_ids: list[str] = field(default_factory=list)
    iteration_count: int = 0


@dataclass(slots=True)
class OpenAIExecutionConfig:
    api_key: str | None
    base_url: str
    model: str
    api_format: str = "responses"
    timeout_seconds: float = 90.0
    temperature: float | None = 0.2
    max_output_tokens: int | None = 1600
    organization: str | None = None
    project: str | None = None

    @classmethod
    def from_env(cls) -> OpenAIExecutionConfig:
        base_url = (
            os.getenv("PLAYBOOKOS_OPENAI_BASE_URL")
            or os.getenv("OPENAI_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        model = (
            os.getenv("PLAYBOOKOS_OPENAI_MODEL")
            or os.getenv("OPENAI_MODEL")
            or "gpt-4.1"
        )
        api_format = (os.getenv("PLAYBOOKOS_OPENAI_API_FORMAT") or "responses").strip().lower()
        if api_format not in {"responses", "chat.completions"}:
            api_format = "responses"
        timeout_value = os.getenv("PLAYBOOKOS_OPENAI_TIMEOUT") or "90"
        max_output_tokens_raw = os.getenv("PLAYBOOKOS_OPENAI_MAX_OUTPUT_TOKENS")
        temperature_raw = os.getenv("PLAYBOOKOS_OPENAI_TEMPERATURE")
        return cls(
            api_key=os.getenv("PLAYBOOKOS_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=base_url,
            model=model,
            api_format=api_format,
            timeout_seconds=float(timeout_value),
            temperature=float(temperature_raw) if temperature_raw not in {None, ""} else 0.2,
            max_output_tokens=int(max_output_tokens_raw) if max_output_tokens_raw not in {None, ""} else 1600,
            organization=os.getenv("OPENAI_ORG_ID") or os.getenv("PLAYBOOKOS_OPENAI_ORG_ID"),
            project=os.getenv("OPENAI_PROJECT") or os.getenv("PLAYBOOKOS_OPENAI_PROJECT"),
        )

    def request_url(self) -> str:
        suffix = "/responses" if self.api_format == "responses" else "/chat/completions"
        return f"{self.base_url}{suffix}"

    def headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        if self.project:
            headers["OpenAI-Project"] = self.project
        return headers

    def summary(self) -> dict[str, Any]:
        return {
            "base_url": self.base_url,
            "model": self.model,
            "api_format": self.api_format,
            "timeout_seconds": self.timeout_seconds,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "has_api_key": bool(self.api_key),
            "organization": self.organization,
            "project": self.project,
        }


class ExecutorAdapter(Protocol):
    def execute(self, context: ExecutionContext) -> ExecutionResult: ...


class OpenAITransport(Protocol):
    def post_json(self, url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]: ...


class UrllibOpenAITransport:
    def post_json(self, url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
        req = request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ExecutionError(f"OpenAI HTTP {exc.code}: {body}") from exc
        except error.URLError as exc:
            raise ExecutionError(f"OpenAI request failed: {exc.reason}") from exc


class DeterministicExecutorAdapter:
    def execute(self, context: ExecutionContext) -> ExecutionResult:
        if context.approval_required:
            return ExecutionResult(
                status=RunStatus.WAITING_HUMAN,
                output_text=f"Task '{context.task_name}' requires human approval before execution.",
                trace_id=f"trace-{uuid4()}",
                metrics={"approval_required": True},
                tool_calls=[],
            )

        return ExecutionResult(
            status=RunStatus.SUCCEEDED,
            output_text=(
                f"Executed '{context.task_name}' for goal '{context.goal_title}'. "
                f"Playbook '{context.playbook_name}' supplied {len(context.compiled_steps)} step(s). "
                f"Knowledge items: {len(context.knowledge_items)}."
            ),
            trace_id=f"trace-{uuid4()}",
            metrics={
                "mcp_server_count": len(context.mcp_servers),
                "compiled_step_count": len(context.compiled_steps),
                "knowledge_item_count": len(context.knowledge_items),
                "adapter": "deterministic",
            },
            tool_calls=[
                {
                    "tool": "compiled_playbook",
                    "action": "simulate_execution",
                    "task": context.task_name,
                    "mcp_servers": context.mcp_servers,
                    "knowledge_item_count": len(context.knowledge_items),
                }
            ],
        )


class OpenAIAgentsSDKAdapter:
    def __init__(
        self,
        *,
        config: OpenAIExecutionConfig | None = None,
        transport: OpenAITransport | None = None,
    ) -> None:
        self.config = config or OpenAIExecutionConfig.from_env()
        self.transport = transport or UrllibOpenAITransport()

    def execute(self, context: ExecutionContext) -> ExecutionResult:
        trace_id = f"agents-trace-{uuid4()}"
        payload = self._build_request_payload(context)
        config_summary = self.config.summary()
        request_url = self.config.request_url()
        prepared_call = {
            "tool": "openai_api",
            "action": "request_prepared",
            "request_format": self.config.api_format,
            "request_url": request_url,
            "config": config_summary,
            "payload": payload,
        }

        if context.approval_required:
            return ExecutionResult(
                status=RunStatus.WAITING_HUMAN,
                output_text=f"Task '{context.task_name}' requires human approval before execution.",
                trace_id=trace_id,
                metrics={
                    "adapter": "openai-agents-sdk",
                    "openai_mode": "approval_required",
                    "openai_config": config_summary,
                    "openai_request_format": self.config.api_format,
                    "openai_request_url": request_url,
                },
                tool_calls=[prepared_call],
            )

        if not self.config.api_key:
            return ExecutionResult(
                status=RunStatus.SUCCEEDED,
                output_text="Prepared OpenAI execution payload using current configuration, but no API key is configured in the environment.",
                trace_id=trace_id,
                metrics={
                    "adapter": "openai-agents-sdk",
                    "openai_mode": "prepared_only",
                    "openai_config": config_summary,
                    "openai_request_format": self.config.api_format,
                    "openai_request_url": request_url,
                    "instruction_bytes": len(json.dumps(payload, ensure_ascii=False)),
                },
                tool_calls=[prepared_call],
            )

        try:
            response_payload = self.transport.post_json(
                request_url,
                self.config.headers(),
                payload,
                self.config.timeout_seconds,
            )
        except ExecutionError as exc:
            return ExecutionResult(
                status=RunStatus.FAILED,
                output_text="OpenAI execution request failed.",
                trace_id=trace_id,
                metrics={
                    "adapter": "openai-agents-sdk",
                    "openai_mode": "online_error",
                    "openai_config": config_summary,
                    "openai_request_format": self.config.api_format,
                    "openai_request_url": request_url,
                },
                error_class=exc.__class__.__name__,
                error_message=str(exc),
                tool_calls=[prepared_call],
            )

        output_text = self._extract_output_text(response_payload)
        response_call = {
            "tool": "openai_api",
            "action": "response_received",
            "request_format": self.config.api_format,
            "response_id": response_payload.get("id"),
            "response_model": response_payload.get("model", self.config.model),
            "usage": response_payload.get("usage", {}),
            "output_preview": output_text[:400],
        }
        return ExecutionResult(
            status=RunStatus.SUCCEEDED,
            output_text=output_text or "OpenAI API call completed without text output.",
            trace_id=response_payload.get("id") or trace_id,
            metrics={
                "adapter": "openai-agents-sdk",
                "openai_mode": "online",
                "openai_config": config_summary,
                "openai_request_format": self.config.api_format,
                "openai_request_url": request_url,
                "openai_response_id": response_payload.get("id"),
                "openai_usage": response_payload.get("usage", {}),
                "instruction_bytes": len(json.dumps(payload, ensure_ascii=False)),
            },
            tool_calls=[prepared_call, response_call],
        )

    def _build_request_payload(self, context: ExecutionContext) -> dict[str, Any]:
        task_packet = {
            "goal": {
                "id": context.goal_id,
                "title": context.goal_title,
                "objective": context.objective,
            },
            "task": {
                "id": context.task_id,
                "name": context.task_name,
                "description": context.task_description,
                "approval_required": context.approval_required,
            },
            "playbook": {
                "id": context.playbook_id,
                "name": context.playbook_name,
                "version": context.playbook_version,
                "steps": context.compiled_steps,
            },
            "skill_id": context.skill_id,
            "mcp_servers": context.mcp_servers,
            "knowledge_items": context.knowledge_items,
        }
        metadata = {
            "goal_id": context.goal_id,
            "task_id": context.task_id,
            "playbook_id": context.playbook_id,
            "skill_id": context.skill_id,
            "mcp_server_count": len(context.mcp_servers),
            "knowledge_item_count": len(context.knowledge_items),
        }
        system_prompt = self._system_prompt(context)
        user_prompt = json.dumps(task_packet, ensure_ascii=False, indent=2)
        if self.config.api_format == "chat.completions":
            payload: dict[str, Any] = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "metadata": metadata,
            }
            if self.config.temperature is not None:
                payload["temperature"] = self.config.temperature
            if self.config.max_output_tokens is not None:
                payload["max_tokens"] = self.config.max_output_tokens
            return payload

        payload = {
            "model": self.config.model,
            "instructions": system_prompt,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": user_prompt,
                        }
                    ],
                }
            ],
            "metadata": metadata,
        }
        if self.config.temperature is not None:
            payload["temperature"] = self.config.temperature
        if self.config.max_output_tokens is not None:
            payload["max_output_tokens"] = self.config.max_output_tokens
        return payload

    def _system_prompt(self, context: ExecutionContext) -> str:
        step_count = len(context.compiled_steps)
        return (
            "You are the PlaybookOS execution worker. "
            "Follow the supplied SOP strictly, use the declared skill and MCP scope only, "
            "produce a concise execution summary, and call out blockers explicitly. "
            f"The task includes {step_count} SOP step(s), {len(context.mcp_servers)} MCP server reference(s), "
            f"and {len(context.knowledge_items)} knowledge item(s)."
        )

    def _extract_output_text(self, response_payload: dict[str, Any]) -> str:
        if isinstance(response_payload.get("output_text"), str):
            return response_payload["output_text"]
        choices = response_payload.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts: list[str] = []
                for item in content:
                    if isinstance(item, dict):
                        text = item.get("text") or item.get("content")
                        if isinstance(text, str):
                            parts.append(text)
                if parts:
                    return "\n".join(parts)
        output = response_payload.get("output")
        if isinstance(output, list):
            parts: list[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                content = item.get("content")
                if isinstance(content, list):
                    for content_item in content:
                        if isinstance(content_item, dict):
                            text = content_item.get("text")
                            if isinstance(text, str):
                                parts.append(text)
                elif isinstance(content, str):
                    parts.append(content)
            if parts:
                return "\n".join(parts)
        return ""


def _session_status_for_result(status: RunStatus) -> SessionStatus:
    if status == RunStatus.SUCCEEDED:
        return SessionStatus.COMPLETED
    if status == RunStatus.WAITING_HUMAN:
        return SessionStatus.WAITING_HUMAN
    return SessionStatus.FAILED


class RunExecutor:
    def __init__(self, adapter: ExecutorAdapter | None = None) -> None:
        self.adapter = adapter or DeterministicExecutorAdapter()

    def execute_run(self, store: StoreProtocol, run_id: str) -> ExecutionResult:
        run = store.runs.get(run_id)
        task = store.tasks.get(run.task_id)
        playbook = store.playbooks.get(task.playbook_id)
        goal = store.goals.get(task.goal_id)

        if run.status == RunStatus.WAITING_HUMAN:
            raise ExecutionError("Run is waiting for human approval")
        if run.status not in {RunStatus.QUEUED, RunStatus.RUNNING}:
            raise ExecutionError(f"Run is not executable from status '{run.status.value}'")

        worker_session = ensure_worker_session_for_run(store, run.id)
        update_session_for_run(store, run.id, status=SessionStatus.RUNNING, summary=f"Started run for {task.name}")
        append_event(store, entity_type="run", entity_id=run.id, event_type="run.execution_started", payload={"session_id": worker_session.id, "task_id": task.id})
        run.status = RunStatus.RUNNING
        run.started_at = run.started_at or utc_now()
        task.status = TaskStatus.RUNNING
        task.updated_at = utc_now()
        store.runs.save(run)
        store.tasks.save(task)

        linked_knowledge_items = [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "content": item.content,
                "tags": item.tags,
            }
            for item in [store.knowledge_bases.get(knowledge_id) for knowledge_id in task.knowledge_base_ids if knowledge_id]
        ]

        context = ExecutionContext(
            goal_id=goal.id,
            goal_title=goal.title,
            objective=goal.objective,
            task_id=task.id,
            task_name=task.name,
            task_description=task.description,
            playbook_id=playbook.id,
            playbook_name=playbook.name,
            playbook_version=playbook.version,
            compiled_steps=playbook.compiled_spec.get("steps", []),
            mcp_servers=list(playbook.compiled_spec.get("mcp_servers", [])),
            knowledge_items=linked_knowledge_items,
            skill_id=task.assigned_skill_id,
            approval_required=task.approval_required,
        )
        record_child_session(
            store,
            goal_id=goal.id,
            parent_session_id=worker_session.id,
            title="Subsession · Context synthesis",
            task_id=task.id,
            run_id=run.id,
            objective="Assemble SOP, skill, knowledge, and task context for execution",
            input_context={
                "compiled_step_count": len(context.compiled_steps),
                "mcp_servers": context.mcp_servers,
                "knowledge_item_ids": [item["id"] for item in linked_knowledge_items],
                "skill_id": context.skill_id,
            },
            output_context={
                "task_name": task.name,
                "playbook_name": playbook.name,
                "approval_required": task.approval_required,
            },
            summary=f"Prepared {len(context.compiled_steps)} steps, {len(context.mcp_servers)} MCP servers, and {len(linked_knowledge_items)} knowledge items.",
            status=SessionStatus.COMPLETED,
        )

        result = self.adapter.execute(context)
        record_child_session(
            store,
            goal_id=goal.id,
            parent_session_id=worker_session.id,
            title="Subsession · AI execution",
            task_id=task.id,
            run_id=run.id,
            objective="Run the assigned skill against the compiled SOP",
            input_context={"task_id": task.id, "run_id": run.id, "playbook_id": playbook.id},
            output_context={
                "trace_id": result.trace_id,
                "tool_calls": result.tool_calls,
                "metrics": result.metrics,
                "run_status": result.status.value,
            },
            summary=result.output_text,
            status=_session_status_for_result(result.status),
        )

        run.status = result.status
        run.trace_id = result.trace_id
        run.metrics = {
            **result.metrics,
            "output_text": result.output_text,
            "tool_calls": result.tool_calls,
        }
        run.error_class = result.error_class
        run.error_message = result.error_message
        if result.status in {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.CANCELLED, RunStatus.TIMED_OUT}:
            run.finished_at = utc_now()

        artifact = Artifact(
            run_id=run.id,
            kind="run_report",
            title=f"Run report for {task.name}",
            uri=f"playbookos://runs/{run.id}/attempts/{run.attempt}/report.json",
            mime_type="application/json",
            version=str(run.attempt),
            metadata={
                "goal_id": goal.id,
                "task_id": task.id,
                "playbook_id": playbook.id,
                "knowledge_base_ids": task.knowledge_base_ids,
                "knowledge_item_count": len(linked_knowledge_items),
                "run_status": result.status.value,
                "trace_id": result.trace_id,
                "output_text": result.output_text,
                "tool_calls": result.tool_calls,
                "metrics": result.metrics,
                "error_class": result.error_class,
                "error_message": result.error_message,
            },
        )
        store.artifacts.save(artifact)
        result.artifact_ids.append(artifact.id)

        record_child_session(
            store,
            goal_id=goal.id,
            parent_session_id=worker_session.id,
            title="Subsession · Supervisor verification",
            task_id=task.id,
            run_id=run.id,
            objective="Collect artifacts and expose verifiable execution outputs",
            input_context={"artifact_kind": artifact.kind, "artifact_id": artifact.id},
            output_context={"trace_id": result.trace_id, "artifact_ids": result.artifact_ids, "run_status": result.status.value},
            summary="Captured run artifact, trace, and execution metrics for the supervisor.",
            status=_session_status_for_result(result.status),
        )

        session_status = _session_status_for_result(result.status)
        update_session_for_run(
            store,
            run.id,
            status=session_status,
            summary=result.output_text,
            output_context={
                "trace_id": result.trace_id,
                "artifact_ids": result.artifact_ids,
                "run_status": result.status.value,
                "knowledge_base_ids": task.knowledge_base_ids,
            },
        )
        append_event(store, entity_type="run", entity_id=run.id, event_type="run.execution_finished", payload={"status": result.status.value, "task_id": task.id, "goal_id": goal.id})

        if result.status == RunStatus.SUCCEEDED:
            task.status = TaskStatus.REVIEW
            goal.status = GoalStatus.RUNNING
        elif result.status == RunStatus.WAITING_HUMAN:
            task.status = TaskStatus.WAITING_HUMAN
            goal.status = GoalStatus.BLOCKED
        else:
            task.status = TaskStatus.FAILED
            goal.status = GoalStatus.BLOCKED

        task.updated_at = utc_now()
        goal.updated_at = utc_now()
        store.runs.save(run)
        store.tasks.save(task)
        store.goals.save(goal)
        refresh_goal_supervisor_session(store, goal.id)
        return result


class GoalAutopilot:
    def __init__(self, adapter: ExecutorAdapter | None = None) -> None:
        self.adapter = adapter or DeterministicExecutorAdapter()

    def run(self, store: StoreProtocol, goal_id: str, *, max_iterations: int = 100) -> GoalAutopilotResult:
        executed_run_ids: list[str] = []
        completed_task_ids: list[str] = []
        waiting_human_run_ids: list[str] = []
        failed_run_ids: list[str] = []
        reflection_ids: list[str] = []
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            dispatch_goal_in_store(store, goal_id)
            refresh_goal_supervisor_session(store, goal_id)
            tasks = [task for task in store.tasks.list() if task.goal_id == goal_id]
            task_ids = {task.id for task in tasks}
            executable_runs = [
                run for run in store.runs.list() if run.task_id in task_ids and run.status == RunStatus.QUEUED
            ]

            if not executable_runs:
                goal = store.goals.get(goal_id)
                refresh_goal_supervisor_session(store, goal_id)
                return GoalAutopilotResult(
                    goal_id=goal_id,
                    goal_status=goal.status,
                    executed_run_ids=executed_run_ids,
                    completed_task_ids=completed_task_ids,
                    waiting_human_run_ids=waiting_human_run_ids,
                    failed_run_ids=failed_run_ids,
                    reflection_ids=reflection_ids,
                    iteration_count=iterations,
                )

            progress_made = False
            for run in executable_runs:
                result = execute_run_in_store(store, run.id, adapter=self.adapter)
                executed_run_ids.append(run.id)
                progress_made = True

                if result.status == RunStatus.SUCCEEDED:
                    completion = complete_task_in_store(store, run.task_id)
                    completed_task_ids.append(completion.task_id)
                    reflection = reflect_run_in_store(store, run.id)
                    reflection_ids.append(reflection.reflection.id)
                    refresh_goal_supervisor_session(store, goal_id)
                    continue

                if result.status == RunStatus.WAITING_HUMAN:
                    waiting_human_run_ids.append(run.id)
                    reflection = reflect_run_in_store(store, run.id)
                    reflection_ids.append(reflection.reflection.id)
                    refresh_goal_supervisor_session(store, goal_id)
                    continue

                failed_run_ids.append(run.id)
                reflection = reflect_run_in_store(store, run.id)
                reflection_ids.append(reflection.reflection.id)
                refresh_goal_supervisor_session(store, goal_id)

            if not progress_made:
                break

        goal = store.goals.get(goal_id)
        refresh_goal_supervisor_session(store, goal_id)
        return GoalAutopilotResult(
            goal_id=goal_id,
            goal_status=goal.status,
            executed_run_ids=executed_run_ids,
            completed_task_ids=completed_task_ids,
            waiting_human_run_ids=waiting_human_run_ids,
            failed_run_ids=failed_run_ids,
            reflection_ids=reflection_ids,
            iteration_count=iterations,
        )



def execute_run_in_store(
    store: StoreProtocol,
    run_id: str,
    *,
    adapter: ExecutorAdapter | None = None,
) -> ExecutionResult:
    return RunExecutor(adapter=adapter).execute_run(store, run_id)



def autopilot_goal_in_store(
    store: StoreProtocol,
    goal_id: str,
    *,
    adapter: ExecutorAdapter | None = None,
    max_iterations: int = 100,
) -> GoalAutopilotResult:
    return GoalAutopilot(adapter=adapter).run(store, goal_id, max_iterations=max_iterations)
