from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from playbookos.api.store import StoreProtocol
from playbookos.domain.models import Goal, GoalStatus, Playbook, Task, TaskStatus, utc_now


class PlanningError(ValueError):
    pass


@dataclass(slots=True)
class StepBlueprint:
    name: str
    description: str
    depends_on_refs: list[str | int] = field(default_factory=list)
    assigned_skill_id: str | None = None
    approval_required: bool = False
    queue_name: str = "default"
    priority: int = 0


@dataclass(slots=True)
class GoalPlanningResult:
    goal_id: str
    playbook_ids: list[str]
    created_tasks: list[Task]
    existing_task_count: int = 0

    @property
    def created_count(self) -> int:
        return len(self.created_tasks)


class PlaybookPlanner:
    def plan_goal(
        self,
        goal: Goal,
        playbooks: list[Playbook],
        *,
        existing_tasks: list[Task] | None = None,
    ) -> GoalPlanningResult:
        existing_tasks = existing_tasks or []
        if existing_tasks:
            return GoalPlanningResult(
                goal_id=goal.id,
                playbook_ids=[playbook.id for playbook in playbooks],
                created_tasks=[],
                existing_task_count=len(existing_tasks),
            )

        if not playbooks:
            raise PlanningError("Goal must be linked to at least one playbook before planning")

        created_tasks: list[Task] = []
        for playbook in sorted(playbooks, key=lambda item: item.created_at):
            blueprints = self._extract_steps(goal, playbook)
            created_tasks.extend(self._build_tasks_for_playbook(goal, playbook, blueprints))

        return GoalPlanningResult(
            goal_id=goal.id,
            playbook_ids=[playbook.id for playbook in playbooks],
            created_tasks=created_tasks,
            existing_task_count=0,
        )

    def _extract_steps(self, goal: Goal, playbook: Playbook) -> list[StepBlueprint]:
        raw_steps = playbook.compiled_spec.get("steps", [])
        if not raw_steps:
            return [
                StepBlueprint(
                    name=f"Execute {playbook.name}",
                    description=goal.objective,
                    priority=0,
                )
            ]

        steps: list[StepBlueprint] = []
        for index, raw_step in enumerate(raw_steps):
            steps.append(self._normalize_step(raw_step, goal, playbook, index))
        return steps

    def _normalize_step(
        self,
        raw_step: Any,
        goal: Goal,
        playbook: Playbook,
        index: int,
    ) -> StepBlueprint:
        if isinstance(raw_step, str):
            name = raw_step.strip() or f"{playbook.name} step {index + 1}"
            return StepBlueprint(
                name=name,
                description=goal.objective,
                priority=index,
            )

        if not isinstance(raw_step, dict):
            raise PlanningError(f"Unsupported playbook step type at index {index}: {type(raw_step).__name__}")

        name = str(raw_step.get("name") or raw_step.get("title") or f"{playbook.name} step {index + 1}").strip()
        description = str(raw_step.get("description") or raw_step.get("instruction") or goal.objective).strip()
        depends_on_refs = list(raw_step.get("depends_on", []))
        return StepBlueprint(
            name=name,
            description=description,
            depends_on_refs=depends_on_refs,
            assigned_skill_id=raw_step.get("assigned_skill_id") or raw_step.get("skill_id"),
            approval_required=bool(raw_step.get("approval_required") or raw_step.get("requires_approval", False)),
            queue_name=str(raw_step.get("queue_name", "default")),
            priority=int(raw_step.get("priority", index)),
        )

    def _build_tasks_for_playbook(
        self,
        goal: Goal,
        playbook: Playbook,
        blueprints: list[StepBlueprint],
    ) -> list[Task]:
        tasks: list[Task] = []
        step_name_to_task_id: dict[str, str] = {}

        for index, blueprint in enumerate(blueprints):
            depends_on = self._resolve_dependencies(blueprint, blueprints, tasks, step_name_to_task_id, index)
            task = Task(
                goal_id=goal.id,
                playbook_id=playbook.id,
                name=blueprint.name,
                description=blueprint.description,
                depends_on=depends_on,
                assigned_skill_id=blueprint.assigned_skill_id,
                approval_required=blueprint.approval_required,
                queue_name=blueprint.queue_name,
                priority=blueprint.priority,
                status=TaskStatus.READY if not depends_on else TaskStatus.INBOX,
            )
            tasks.append(task)
            step_name_to_task_id[blueprint.name] = task.id

        return tasks

    def _resolve_dependencies(
        self,
        blueprint: StepBlueprint,
        blueprints: list[StepBlueprint],
        tasks: list[Task],
        step_name_to_task_id: dict[str, str],
        index: int,
    ) -> list[str]:
        if not blueprint.depends_on_refs:
            if index == 0:
                return []
            return [tasks[index - 1].id]

        resolved: list[str] = []
        for dependency in blueprint.depends_on_refs:
            if isinstance(dependency, int):
                if dependency < 0 or dependency >= index:
                    raise PlanningError(
                        f"Step '{blueprint.name}' references invalid dependency index {dependency}"
                    )
                resolved.append(tasks[dependency].id)
                continue

            dependency_name = str(dependency).strip()
            if dependency_name not in step_name_to_task_id:
                raise PlanningError(
                    f"Step '{blueprint.name}' references unknown dependency '{dependency_name}'"
                )
            resolved.append(step_name_to_task_id[dependency_name])

        return resolved


def plan_goal_in_store(
    store: StoreProtocol,
    goal_id: str,
    *,
    planner: PlaybookPlanner | None = None,
) -> GoalPlanningResult:
    planner = planner or PlaybookPlanner()
    goal = store.goals.get(goal_id)
    playbooks = [playbook for playbook in store.playbooks.list() if playbook.goal_id == goal_id]
    existing_tasks = [task for task in store.tasks.list() if task.goal_id == goal_id]
    planning_result = planner.plan_goal(goal, playbooks, existing_tasks=existing_tasks)

    for task in planning_result.created_tasks:
        store.tasks.save(task)

    goal.status = GoalStatus.RUNNING
    goal.updated_at = utc_now()
    store.goals.save(goal)
    return planning_result
