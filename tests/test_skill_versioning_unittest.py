import unittest

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Skill, SkillStatus
from playbookos.skills_service import (
    activate_skill_in_store,
    create_next_skill_version_in_store,
    rollback_skill_in_store,
)


class SkillVersioningTestCase(unittest.TestCase):
    def test_create_next_version_clones_skill_and_increments_patch(self) -> None:
        store = InMemoryStore()
        skill = store.skills.save(
            Skill(
                name="Research skill",
                description="Collect inputs",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                version="0.1.0",
            )
        )

        result = create_next_skill_version_in_store(store, skill.id)

        self.assertEqual(result.skill.version, "0.1.1")
        self.assertEqual(result.skill.rollback_version, "0.1.0")
        self.assertEqual(result.skill.status, SkillStatus.DRAFT)
        self.assertEqual(result.skill.name, skill.name)

    def test_activate_skill_deprecates_previous_active_and_sets_rollback(self) -> None:
        store = InMemoryStore()
        first = store.skills.save(Skill(name="Ops skill", description="v1", input_schema={}, output_schema={}, version="0.1.0"))
        activate_skill_in_store(store, first.id)
        second = create_next_skill_version_in_store(store, first.id).skill

        result = activate_skill_in_store(store, second.id)

        self.assertEqual(result.skill.status, SkillStatus.ACTIVE)
        self.assertEqual(result.skill.rollback_version, "0.1.0")
        self.assertEqual(store.skills.get(first.id).status, SkillStatus.DEPRECATED)

    def test_rollback_reactivates_previous_version(self) -> None:
        store = InMemoryStore()
        first = store.skills.save(Skill(name="Planner skill", description="v1", input_schema={}, output_schema={}, version="1.0.0"))
        activate_skill_in_store(store, first.id)
        second = create_next_skill_version_in_store(store, first.id).skill
        activate_skill_in_store(store, second.id)

        result = rollback_skill_in_store(store, second.id)

        self.assertEqual(result.active_skill.id, first.id)
        self.assertEqual(result.active_skill.status, SkillStatus.ACTIVE)
        self.assertEqual(store.skills.get(second.id).status, SkillStatus.DEPRECATED)
        self.assertEqual(result.target_version, "1.0.0")


if __name__ == "__main__":
    unittest.main()
