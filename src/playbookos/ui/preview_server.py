from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from playbookos.api.store import InMemoryStore, StoreProtocol
from playbookos.domain.models import Goal, KnowledgeBase, Playbook, PlaybookStatus, ReflectionStatus, Skill, Task
from playbookos.executor.service import DeterministicExecutorAdapter, autopilot_goal_in_store
from playbookos.observability import get_error_log_path, list_recorded_errors, record_error
from playbookos.persistence import create_store_from_env
from playbookos.planner.service import plan_goal_in_store
from playbookos.reflection.service import approve_reflection_in_store, evaluate_reflection_in_store, publish_reflection_in_store
from playbookos.supervisor import accept_task_in_store
from playbookos.ui import build_dashboard_html


class PreviewRequestHandler(BaseHTTPRequestHandler):
    server_version = "PlaybookOSPreview/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path == "/":
                self._write_html(build_dashboard_html(self.server.store.board_snapshot(), api_base="/api"))
                return
            if path == "/healthz":
                self._write_json({"status": "ok"})
                return
            if path == "/api/board":
                self._write_json(self.server.store.board_snapshot())
                return
            if path == "/api/goals":
                self._write_json(_serialize_items(self.server.store.goals.list()))
                return
            if path == "/api/playbooks":
                self._write_json(_serialize_items(self.server.store.playbooks.list()))
                return
            if path == "/api/skills":
                self._write_json(_serialize_items(self.server.store.skills.list()))
                return
            if path == "/api/knowledge-bases":
                self._write_json(_serialize_items(self.server.store.knowledge_bases.list()))
                return
            if path == "/api/tasks":
                self._write_json(_serialize_items(self.server.store.tasks.list()))
                return
            if path == "/api/sessions":
                self._write_json(_serialize_items(self.server.store.sessions.list()))
                return
            if path == "/api/runs":
                self._write_json(_serialize_items(self.server.store.runs.list()))
                return
            if path == "/api/acceptances":
                self._write_json(_serialize_items(self.server.store.acceptances.list()))
                return
            if path == "/api/artifacts":
                self._write_json(_serialize_items(self.server.store.artifacts.list()))
                return
            if path == "/api/reflections":
                self._write_json(_serialize_items(self.server.store.reflections.list()))
                return
            if path == "/api/events":
                self._write_json(_serialize_items(self.server.store.events.list()))
                return
            if path == "/api/errors":
                self._write_json(list_recorded_errors(path=self.server.error_log_path))
                return

            record_error("Route not found", component="preview_server", operation="do_GET", metadata={"path": path, "status_code": 404}, path=self.server.error_log_path)
            self._write_json({"detail": "Not found"}, status=HTTPStatus.NOT_FOUND)
        except Exception as exc:
            record_error(exc, component="preview_server", operation="do_GET", metadata={"path": path}, path=self.server.error_log_path)
            self._write_json({"detail": "Internal server error"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            payload = self._read_json_body()
            if path == "/api/goals":
                goal = Goal(
                    title=payload["title"],
                    objective=payload["objective"],
                    constraints=list(payload.get("constraints", [])),
                    definition_of_done=list(payload.get("definition_of_done", [])),
                )
                self.server.store.goals.save(goal)
                self._write_json(_to_jsonable(goal), status=HTTPStatus.CREATED)
                return
            if path == "/api/playbooks/import":
                goal_id = payload.get("goal_id") or None
                if goal_id is not None:
                    self.server.store.goals.get(goal_id)
                playbook = Playbook(
                    name=payload["name"],
                    source_kind=payload.get("source_kind", "markdown"),
                    source_uri=payload["source_uri"],
                    goal_id=goal_id,
                    compiled_spec=dict(payload.get("compiled_spec", {})),
                )
                if playbook.compiled_spec.get("steps"):
                    playbook.status = PlaybookStatus.COMPILED
                self.server.store.playbooks.save(playbook)
                self._write_json(_to_jsonable(playbook), status=HTTPStatus.CREATED)
                return
            if path == "/api/skills":
                skill = Skill(
                    name=payload["name"],
                    description=payload["description"],
                    input_schema=dict(payload.get("input_schema", {})),
                    output_schema=dict(payload.get("output_schema", {})),
                    required_mcp_servers=list(payload.get("required_mcp_servers", [])),
                    approval_policy=dict(payload.get("approval_policy", {})),
                    evaluation_policy=dict(payload.get("evaluation_policy", {})),
                )
                self.server.store.skills.save(skill)
                self._write_json(_to_jsonable(skill), status=HTTPStatus.CREATED)
                return
            if path == "/api/knowledge-bases":
                goal_id = payload.get("goal_id") or None
                if goal_id is not None:
                    self.server.store.goals.get(goal_id)
                item = KnowledgeBase(
                    name=payload["name"],
                    description=payload.get("description", ""),
                    content=payload["content"],
                    tags=list(payload.get("tags", [])),
                    source_uri=payload.get("source_uri") or None,
                    goal_id=goal_id,
                )
                self.server.store.knowledge_bases.save(item)
                self._write_json(_to_jsonable(item), status=HTTPStatus.CREATED)
                return
            if path == "/api/tasks":
                self.server.store.goals.get(payload["goal_id"])
                self.server.store.playbooks.get(payload["playbook_id"])
                assigned_skill_id = payload.get("assigned_skill_id") or None
                if assigned_skill_id is not None:
                    self.server.store.skills.get(assigned_skill_id)
                task = Task(
                    goal_id=payload["goal_id"],
                    playbook_id=payload["playbook_id"],
                    name=payload["name"],
                    description=payload["description"],
                    depends_on=list(payload.get("depends_on", [])),
                    assigned_skill_id=assigned_skill_id,
                    approval_required=bool(payload.get("approval_required", False)),
                    queue_name=payload.get("queue_name", "default"),
                    priority=int(payload.get("priority", 0)),
                    parent_task_id=payload.get("parent_task_id") or None,
                )
                self.server.store.tasks.save(task)
                self._write_json(_to_jsonable(task), status=HTTPStatus.CREATED)
                return

            record_error("Route not found", component="preview_server", operation="do_POST", metadata={"path": path, "status_code": 404}, path=self.server.error_log_path)
            self._write_json({"detail": "Not found"}, status=HTTPStatus.NOT_FOUND)
        except KeyError as exc:
            record_error(exc, component="preview_server", operation="do_POST", metadata={"path": path}, path=self.server.error_log_path)
            self._write_json({"detail": f"Missing field: {exc.args[0]}"}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            record_error(exc, component="preview_server", operation="do_POST", metadata={"path": path}, path=self.server.error_log_path)
            self._write_json({"detail": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length > 0 else b"{}"
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _write_html(self, payload: str, *, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _write_json(self, payload: Any, *, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class PreviewHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address: tuple[str, int], store: StoreProtocol, *, error_log_path: str | Path | None = None) -> None:
        super().__init__(server_address, PreviewRequestHandler)
        self.store = store
        self.error_log_path = get_error_log_path(error_log_path)


def build_demo_store() -> StoreProtocol:
    store = InMemoryStore()

    goal = store.goals.save(
        Goal(
            title="Launch PlaybookOS control plane",
            objective="Show a realistic dashboard with execution, artifacts, and learning signals.",
            constraints=["No external SaaS calls in preview mode", "Keep humans in approval loop"],
            definition_of_done=["Dashboard visible", "Artifacts visible", "Reflection published safely"],
        )
    )
    launch_skill = store.skills.save(
        Skill(name="Launch operator", description="Coordinate rollout tasks", input_schema={}, output_schema={}, required_mcp_servers=["plane", "github", "slack"])
    )
    store.knowledge_bases.save(
        KnowledgeBase(
            name="Launch context pack",
            description="Reusable operational notes for product launch.",
            content="Stakeholder list, launch risks, escalation path, and release checklist.",
            tags=["launch", "ops", "sop"],
            goal_id=goal.id,
            source_uri="file:///demo/launch-context.md",
        )
    )
    store.playbooks.save(
        Playbook(
            name="Ops launch playbook",
            source_kind="markdown",
            source_uri="file:///demo/launch-playbook.md",
            goal_id=goal.id,
            compiled_spec={
                "steps": [
                    "Collect context",
                    "Execute rollout",
                    {"name": "Human approval", "depends_on": ["Execute rollout"], "requires_approval": True},
                ],
                "mcp_servers": ["plane", "github", "slack"],
            },
        )
    )

    second_goal = store.goals.save(
        Goal(
            title="Evaluate SOP patches",
            objective="Generate a reflection proposal and publish a safer playbook version.",
        )
    )
    reflection_skill = store.skills.save(
        Skill(name="Reflection analyst", description="Review traces and improve SOPs", input_schema={}, output_schema={}, required_mcp_servers=["plane"])
    )
    store.knowledge_bases.save(
        KnowledgeBase(
            name="Reflection evidence base",
            description="Lessons learned used for postmortem synthesis.",
            content="Previous incidents, patch notes, acceptance criteria, and replay evidence.",
            tags=["reflection", "knowledge", "postmortem"],
            goal_id=second_goal.id,
            source_uri="file:///demo/reflection-evidence.md",
        )
    )
    store.playbooks.save(
        Playbook(
            name="Reflection loop playbook",
            source_kind="markdown",
            source_uri="file:///demo/reflection-playbook.md",
            goal_id=second_goal.id,
            compiled_spec={
                "steps": ["Gather traces", "Update SOP guidance"],
                "mcp_servers": ["plane"],
            },
        )
    )

    plan_goal_in_store(store, goal.id)
    for task in [item for item in store.tasks.list() if item.goal_id == goal.id]:
        task.assigned_skill_id = launch_skill.id
        store.tasks.save(task)
    autopilot_goal_in_store(store, goal.id, adapter=DeterministicExecutorAdapter())

    plan_goal_in_store(store, second_goal.id)
    for task in [item for item in store.tasks.list() if item.goal_id == second_goal.id]:
        task.assigned_skill_id = reflection_skill.id
        store.tasks.save(task)
    result = autopilot_goal_in_store(store, second_goal.id, adapter=DeterministicExecutorAdapter())
    succeeded_tasks = [task for task in store.tasks.list() if task.goal_id == second_goal.id and task.status.name in {"REVIEW", "DONE"}]
    for task in succeeded_tasks:
        accept_task_in_store(store, task.id, criteria=["Patch proposal is clear", "Evidence is attached"], reviewer_id="preview-reviewer", accepted=True, notes="Preview acceptance passed")

    if result.reflection_ids:
        reflection_id = result.reflection_ids[0]
        evaluation = evaluate_reflection_in_store(store, reflection_id)
        if evaluation.passed and evaluation.reflection.eval_status == ReflectionStatus.APPROVED:
            approve_reflection_in_store(store, reflection_id, approved_by="preview-reviewer")
            publish_reflection_in_store(store, reflection_id)

    return store


def build_runtime_store(*, demo: bool, db_path: str | None = None) -> StoreProtocol:
    if demo:
        return build_demo_store()
    if db_path:
        from playbookos.persistence.sqlite_store import SQLiteStore

        return SQLiteStore(Path(db_path))
    return create_store_from_env()


def _serialize_items(items: list[Any]) -> list[Any]:
    return [_to_jsonable(item) for item in items]


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PlaybookOS preview dashboard without FastAPI dependencies.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--demo", action="store_true", help="Serve demo data instead of the configured runtime store.")
    parser.add_argument("--error-log-path", default=None)
    args = parser.parse_args()

    try:
        store = build_runtime_store(demo=args.demo, db_path=args.db_path)
        server = PreviewHTTPServer((args.host, args.port), store, error_log_path=args.error_log_path)
    except Exception as exc:
        record_error(exc, component="preview_server", operation="startup", metadata={"host": args.host, "port": args.port}, path=args.error_log_path)
        raise
    print(f"PlaybookOS preview running on http://{args.host}:{args.port} (demo={args.demo})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
