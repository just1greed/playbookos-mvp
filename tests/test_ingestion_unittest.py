import unittest

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Goal, PlaybookStatus
from playbookos.ingestion import SOPIngestionError, ingest_sop_in_store, materialize_suggested_skill_in_store
from playbookos.object_store import LocalObjectStore, attach_source_object_to_playbook


class SOPIngestionTestCase(unittest.TestCase):
    def test_ingest_markdown_sop_creates_compiled_playbook_and_skill_suggestions(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Launch release", objective="Ship the launch workflow"))

        result = ingest_sop_in_store(
            store,
            name="Launch SOP",
            goal_id=goal.id,
            source_kind="markdown",
            source_text="""
# Launch Checklist

1. Collect release notes from GitHub and summarize user-facing changes.
2. Draft the announcement in Notion and review messaging.
3. Notify the launch Slack channel and send the stakeholder email.
""",
        )

        self.assertEqual(result.playbook.status, PlaybookStatus.COMPILED)
        self.assertEqual(result.step_count, 3)
        self.assertIn("github", result.detected_mcp_servers)
        self.assertIn("slack", result.detected_mcp_servers)
        self.assertGreaterEqual(len(result.suggested_skills), 2)
        self.assertIsNotNone(result.tooling_guidance)
        self.assertIn("github", result.tooling_guidance.required_mcp_servers)
        self.assertGreaterEqual(len(result.tooling_guidance.prompt_blocks), 3)
        self.assertEqual(result.playbook.goal_id, goal.id)
        self.assertEqual(len(result.playbook.compiled_spec["steps"]), 3)
        self.assertIn("skill_suggestions", result.playbook.compiled_spec)
        self.assertIn("tooling_guidance", result.playbook.compiled_spec)

    def test_ingest_json_sop_uses_structured_steps(self) -> None:
        store = InMemoryStore()

        result = ingest_sop_in_store(
            store,
            name="Structured SOP",
            source_kind="json",
            source_text='{"steps": [{"name": "Prepare draft", "description": "Write the draft"}], "mcp_servers": ["github"]}',
        )

        self.assertEqual(result.step_count, 1)
        self.assertEqual(result.playbook.compiled_spec["steps"][0]["name"], "Prepare draft")
        self.assertEqual(result.detected_mcp_servers, ["github"])

    def test_ingest_requires_source_text(self) -> None:
        store = InMemoryStore()

        with self.assertRaises(SOPIngestionError):
            ingest_sop_in_store(store, name="Empty SOP", source_text="   ")

    def test_materialize_suggested_skill_creates_draft_skill(self) -> None:
        store = InMemoryStore()
        result = ingest_sop_in_store(
            store,
            name="Ops SOP",
            source_text="1. Draft the update.\n2. Notify Slack.\n3. Publish the summary.",
        )

        materialized = materialize_suggested_skill_in_store(store, result.playbook.id, suggestion_index=0)

        self.assertEqual(materialized.playbook.id, result.playbook.id)
        self.assertEqual(materialized.skill.status.value, "draft")
        self.assertTrue(materialized.skill.name)
        self.assertEqual(materialized.bound_step_count, 0)

    def test_materialize_suggested_skill_can_bind_unassigned_steps(self) -> None:
        store = InMemoryStore()
        result = ingest_sop_in_store(
            store,
            name="Bound SOP",
            source_text="1. Prepare release notes.\n2. Publish summary.",
        )

        materialized = materialize_suggested_skill_in_store(
            store,
            result.playbook.id,
            suggestion_index=0,
            bind_to_unassigned_steps=True,
        )

        rebound_playbook = store.playbooks.get(result.playbook.id)
        step_skills = [step.get("assigned_skill_id") for step in rebound_playbook.compiled_spec["steps"]]
        self.assertTrue(all(skill_id == materialized.skill.id for skill_id in step_skills))
        self.assertEqual(materialized.bound_step_count, 2)

    def test_attach_source_object_can_follow_ingestion_result(self) -> None:
        store = InMemoryStore()
        result = ingest_sop_in_store(
            store,
            name="Documented SOP",
            source_kind="markdown",
            source_uri="file:///tmp/documented.md",
            source_text="# Demo\n1. Prepare draft",
        )

        with self.subTest("object store attachment"):
            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as tmpdir:
                stored = attach_source_object_to_playbook(
                    result.playbook,
                    source_text="# Demo\n1. Prepare draft",
                    source_kind="markdown",
                    source_uri="file:///tmp/documented.md",
                    object_store=LocalObjectStore(tmpdir),
                )

                self.assertEqual(result.playbook.compiled_spec["source_object_id"], stored.id)
                self.assertEqual(result.playbook.compiled_spec["source_object_mime_type"], "text/markdown; charset=utf-8")


if __name__ == "__main__":
    unittest.main()
