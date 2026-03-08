import unittest

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Goal, Playbook, Skill, Task


class SkillStoreTestCase(unittest.TestCase):
    def test_manual_skill_can_be_created_and_assigned_to_task(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Skill goal", objective="Attach a manual skill to a task"))
        playbook = store.playbooks.save(
            Playbook(name="Skill playbook", source_kind="markdown", source_uri="file:///tmp/skill.md", goal_id=goal.id)
        )
        skill = store.skills.save(
            Skill(name="Research skill", description="Collect and structure inputs", input_schema={"type": "object"}, output_schema={"type": "object"})
        )
        task = store.tasks.save(
            Task(
                goal_id=goal.id,
                playbook_id=playbook.id,
                name="Use skill",
                description="Task with an attached skill",
                assigned_skill_id=skill.id,
            )
        )

        self.assertEqual(store.skills.get(skill.id).name, "Research skill")
        self.assertEqual(store.tasks.get(task.id).assigned_skill_id, skill.id)


if __name__ == "__main__":
    unittest.main()
