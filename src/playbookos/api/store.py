from __future__ import annotations

from collections import Counter
from threading import RLock
from typing import Generic, Protocol, TypeVar

from playbookos.domain.models import Acceptance, Artifact, DelegationProfile, Event, Goal, KnowledgeBase, KnowledgeUpdate, MCPServer, Playbook, Reflection, Run, Session, Skill, Task

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
    mcp_servers: RepositoryProtocol[MCPServer]
    knowledge_bases: RepositoryProtocol[KnowledgeBase]
    knowledge_updates: RepositoryProtocol[KnowledgeUpdate]
    tasks: RepositoryProtocol[Task]
    sessions: RepositoryProtocol[Session]
    runs: RepositoryProtocol[Run]
    artifacts: RepositoryProtocol[Artifact]
    acceptances: RepositoryProtocol[Acceptance]
    reflections: RepositoryProtocol[Reflection]
    events: RepositoryProtocol[Event]
    delegation_profiles: RepositoryProtocol[DelegationProfile]

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
        self.mcp_servers = InMemoryRepository[MCPServer]()
        self.knowledge_bases = InMemoryRepository[KnowledgeBase]()
        self.knowledge_updates = InMemoryRepository[KnowledgeUpdate]()
        self.tasks = InMemoryRepository[Task]()
        self.sessions = InMemoryRepository[Session]()
        self.runs = InMemoryRepository[Run]()
        self.artifacts = InMemoryRepository[Artifact]()
        self.acceptances = InMemoryRepository[Acceptance]()
        self.reflections = InMemoryRepository[Reflection]()
        self.events = InMemoryRepository[Event]()
        self.delegation_profiles = InMemoryRepository[DelegationProfile]()

    def board_snapshot(self) -> dict[str, dict[str, int]]:
        goal_counts = Counter(goal.status.value for goal in self.goals.list())
        playbook_counts = Counter(playbook.status.value for playbook in self.playbooks.list())
        skill_counts = Counter(skill.status.value for skill in self.skills.list())
        mcp_server_counts = Counter(item.status.value for item in self.mcp_servers.list())
        knowledge_counts = Counter(item.status.value for item in self.knowledge_bases.list())
        knowledge_update_counts = Counter(item.status.value for item in self.knowledge_updates.list())
        task_counts = Counter(task.status.value for task in self.tasks.list())
        session_counts = Counter(session.status.value for session in self.sessions.list())
        run_counts = Counter(run.status.value for run in self.runs.list())
        artifact_counts = Counter(artifact.kind for artifact in self.artifacts.list())
        acceptance_counts = Counter(acceptance.status.value for acceptance in self.acceptances.list())
        reflection_counts = Counter(reflection.eval_status.value for reflection in self.reflections.list())
        event_counts = Counter(event.entity_type for event in self.events.list())
        return {
            "goals": dict(goal_counts),
            "playbooks": dict(playbook_counts),
            "skills": dict(skill_counts),
            "mcp_servers": dict(mcp_server_counts),
            "knowledge_bases": dict(knowledge_counts),
            "knowledge_updates": dict(knowledge_update_counts),
            "tasks": dict(task_counts),
            "sessions": dict(session_counts),
            "runs": dict(run_counts),
            "artifacts": dict(artifact_counts),
            "acceptances": dict(acceptance_counts),
            "reflections": dict(reflection_counts),
            "events": dict(event_counts),
        }
