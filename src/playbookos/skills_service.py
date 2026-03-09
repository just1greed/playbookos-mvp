from __future__ import annotations

from dataclasses import dataclass

from playbookos.api.store import StoreProtocol
from playbookos.domain.models import Skill, SkillStatus, utc_now
from playbookos.supervisor import append_event


class SkillLifecycleError(ValueError):
    pass


@dataclass(slots=True)
class SkillVersionResult:
    skill: Skill
    related_skill_ids: list[str]


@dataclass(slots=True)
class SkillRollbackResult:
    active_skill: Skill
    deprecated_skill: Skill
    target_version: str


def _parse_version(value: str) -> tuple[int, ...]:
    parts = []
    for item in str(value or "0").split("."):
        try:
            parts.append(int(item))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _format_version(parts: tuple[int, ...]) -> str:
    return ".".join(str(part) for part in parts)


def _increment_patch(value: str) -> str:
    parts = list(_parse_version(value))
    while len(parts) < 3:
        parts.append(0)
    parts[2] += 1
    return _format_version(tuple(parts[:3]))


def _skills_with_same_name(store: StoreProtocol, name: str) -> list[Skill]:
    return [item for item in store.skills.list() if item.name == name]


def create_next_skill_version_in_store(store: StoreProtocol, skill_id: str) -> SkillVersionResult:
    skill = store.skills.get(skill_id)
    family = _skills_with_same_name(store, skill.name)
    latest_version = max((item.version for item in family), key=_parse_version, default=skill.version)
    next_version = _increment_patch(latest_version)
    new_skill = Skill(
        name=skill.name,
        description=skill.description,
        input_schema=dict(skill.input_schema),
        output_schema=dict(skill.output_schema),
        required_mcp_servers=list(skill.required_mcp_servers),
        approval_policy=dict(skill.approval_policy),
        evaluation_policy=dict(skill.evaluation_policy),
        rollback_version=skill.version,
        version=next_version,
        status=SkillStatus.DRAFT,
    )
    store.skills.save(new_skill)
    append_event(
        store,
        entity_type="skill",
        entity_id=new_skill.id,
        event_type="skill.version_created",
        payload={"source_skill_id": skill.id, "source_version": skill.version, "version": new_skill.version},
        source="system",
    )
    return SkillVersionResult(skill=new_skill, related_skill_ids=[item.id for item in family] + [new_skill.id])


def activate_skill_in_store(store: StoreProtocol, skill_id: str) -> SkillVersionResult:
    skill = store.skills.get(skill_id)
    family = _skills_with_same_name(store, skill.name)
    previous_active = next((item for item in family if item.status == SkillStatus.ACTIVE and item.id != skill.id), None)
    related_ids: list[str] = []
    for item in family:
        if item.id == skill.id:
            continue
        if item.status == SkillStatus.ACTIVE:
            item.status = SkillStatus.DEPRECATED
            item.updated_at = utc_now()
            store.skills.save(item)
            related_ids.append(item.id)
    skill.status = SkillStatus.ACTIVE
    if previous_active is not None:
        skill.rollback_version = previous_active.version
    skill.updated_at = utc_now()
    store.skills.save(skill)
    append_event(
        store,
        entity_type="skill",
        entity_id=skill.id,
        event_type="skill.activated",
        payload={"version": skill.version, "rollback_version": skill.rollback_version},
        source="human",
    )
    return SkillVersionResult(skill=skill, related_skill_ids=related_ids + [skill.id])


def deprecate_skill_in_store(store: StoreProtocol, skill_id: str) -> SkillVersionResult:
    skill = store.skills.get(skill_id)
    skill.status = SkillStatus.DEPRECATED
    skill.updated_at = utc_now()
    store.skills.save(skill)
    append_event(
        store,
        entity_type="skill",
        entity_id=skill.id,
        event_type="skill.deprecated",
        payload={"version": skill.version},
        source="human",
    )
    return SkillVersionResult(skill=skill, related_skill_ids=[skill.id])


def rollback_skill_in_store(store: StoreProtocol, skill_id: str) -> SkillRollbackResult:
    skill = store.skills.get(skill_id)
    family = sorted(_skills_with_same_name(store, skill.name), key=lambda item: _parse_version(item.version))
    target = None
    if skill.rollback_version:
        target = next((item for item in family if item.version == skill.rollback_version), None)
    if target is None:
        previous_versions = [item for item in family if _parse_version(item.version) < _parse_version(skill.version)]
        if previous_versions:
            target = previous_versions[-1]
    if target is None:
        raise SkillLifecycleError("No rollback target version available for this skill")

    skill.status = SkillStatus.DEPRECATED
    skill.updated_at = utc_now()
    store.skills.save(skill)

    target.status = SkillStatus.ACTIVE
    target.rollback_version = skill.version
    target.updated_at = utc_now()
    store.skills.save(target)

    append_event(
        store,
        entity_type="skill",
        entity_id=target.id,
        event_type="skill.rolled_back",
        payload={"from_skill_id": skill.id, "from_version": skill.version, "to_version": target.version},
        source="human",
    )
    return SkillRollbackResult(active_skill=target, deprecated_skill=skill, target_version=target.version)
