import unittest

from playbookos.api.store import InMemoryStore
from playbookos.authoring import apply_skill_authoring_pack_in_store, build_skill_authoring_pack_in_store
from playbookos.ingestion import ingest_sop_in_store, materialize_suggested_skill_in_store


class SkillAuthoringWizardTestCase(unittest.TestCase):
    def test_build_authoring_pack_uses_linked_playbook_context(self) -> None:
        store = InMemoryStore()
        ingest_result = ingest_sop_in_store(
            store,
            name="Launch SOP",
            source_text="1. Draft release note.\n2. Notify Slack.\n3. Publish update.",
        )
        draft_result = materialize_suggested_skill_in_store(store, ingest_result.playbook.id, suggestion_index=0)

        pack = build_skill_authoring_pack_in_store(store, draft_result.skill.id)

        self.assertEqual(pack.skill_id, draft_result.skill.id)
        self.assertEqual(pack.playbook_id, ingest_result.playbook.id)
        self.assertTrue(pack.checklist)
        self.assertTrue(pack.recommended_input_schema)
        self.assertTrue(pack.recommended_output_schema)
        self.assertIn("Linked playbook", " ".join(pack.notes))

    def test_apply_authoring_pack_fills_missing_skill_fields(self) -> None:
        store = InMemoryStore()
        ingest_result = ingest_sop_in_store(
            store,
            name="Ops SOP",
            source_text="1. Collect context.\n2. Send email update.\n3. Publish summary.",
        )
        draft_result = materialize_suggested_skill_in_store(store, ingest_result.playbook.id, suggestion_index=0)

        result = apply_skill_authoring_pack_in_store(store, draft_result.skill.id)

        self.assertIn("input_schema", result.applied_fields)
        self.assertIn("output_schema", result.applied_fields)
        self.assertIn("approval_policy", result.applied_fields)
        self.assertIn("evaluation_policy", result.applied_fields)
        self.assertEqual(result.skill.evaluation_policy.get("playbook_id"), ingest_result.playbook.id)
        self.assertTrue(result.skill.input_schema.get("properties"))


if __name__ == "__main__":
    unittest.main()
