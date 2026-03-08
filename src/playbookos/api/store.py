from __future__ import annotations

from collections import Counter
from threading import RLock
from typing import Generic, Protocol, TypeVar

from playbookos.domain.models import Artifact, Goal, Playbook, Reflection, Run, Skill, Task

EntityT = TypeVar("EntityT")


class NotFoundError(KeyError):
    pass


class RepositoryProtocol(Protocol[EntityT]):
    def list(self) -> list[EntityT]: ...

    def get(self, item_id: str) -> EntityT: ...

    def save(self, item: EntityT) -> EntityT: ...


class StoreProtocol(Protocol):
    goals: RepositoryProtocol[Goal]
    playbooks: RepositoryProtocol[Playbook]
    skills: RepositoryProtocol[Skill]
    tasks: RepositoryProtocol[Task]
    runs: RepositoryProtocol[Run]
    artifacts: RepositoryProtocol[Artifact]
    reflections: RepositoryProtocol[Reflection]

    def board_snapshot(self) -> dict[str, dict[str, int]]: ...


class InMemoryRepository(Generic[EntityT]):
    def __init__(self) -> None:
        self._items: dict[str, EntityT] = {}
        self._lock = RLock()

    def list(self) -> list[EntityT]:
        with self._lock:
            return list(self._items.values())

    def get(self, item_id: str) -> EntityT:
        with self._lock:
            try:
                return self._items[item_id]
            except KeyError as exc:
                raise NotFoundError(item_id) from exc

    def save(self, item: EntityT) -> EntityT:
        with self._lock:
            item_id = getattr(item, "id")
            self._items[item_id] = item
            return item


class InMemoryStore:
    def __init__(self) -> None:
        self.goals = InMemoryRepository[Goal]()
        self.playbooks = InMemoryRepository[Playbook]()
        self.skills = InMemoryRepository[Skill]()
        self.tasks = InMemoryRepository[Task]()
        self.runs = InMemoryRepository[Run]()
        self.artifacts = InMemoryRepository[Artifact]()
        self.reflections = InMemoryRepository[Reflection]()

    def board_snapshot(self) -> dict[str, dict[str, int]]:
        goal_counts = Counter(goal.status.value for goal in self.goals.list())
        skill_counts = Counter(skill.status.value for skill in self.skills.list())
        task_counts = Counter(task.status.value for task in self.tasks.list())
        run_counts = Counter(run.status.value for run in self.runs.list())
        artifact_counts = Counter(artifact.kind for artifact in self.artifacts.list())
        reflection_counts = Counter(reflection.eval_status.value for reflection in self.reflections.list())
        return {
            "goals": dict(goal_counts),
            "skills": dict(skill_counts),
            "tasks": dict(task_counts),
            "runs": dict(run_counts),
            "artifacts": dict(artifact_counts),
            "reflections": dict(reflection_counts),
        }
