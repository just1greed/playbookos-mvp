import tempfile
import unittest
from pathlib import Path

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import Goal, KnowledgeBase
from playbookos.persistence.sqlite_store import SQLiteStore


class KnowledgeBaseStoreTestCase(unittest.TestCase):
    def test_in_memory_store_counts_knowledge_bases(self) -> None:
        store = InMemoryStore()
        goal = store.goals.save(Goal(title="Knowledge goal", objective="Store reusable context"))
        item = store.knowledge_bases.save(
            KnowledgeBase(
                name="Execution checklist",
                description="Shared launch notes",
                content="1. Verify goal\n2. Verify SOP\n3. Verify reviewer",
                tags=["ops", "checklist"],
                goal_id=goal.id,
            )
        )

        snapshot = store.board_snapshot()

        self.assertEqual(item.goal_id, goal.id)
        self.assertEqual(snapshot["knowledge_bases"]["draft"], 1)

    def test_sqlite_store_persists_knowledge_bases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "playbookos.db"
            store = SQLiteStore(db_path)
            goal = store.goals.save(Goal(title="Persistent knowledge", objective="Persist reusable memory"))
            item = store.knowledge_bases.save(
                KnowledgeBase(
                    name="Reviewer rubric",
                    description="Acceptance guidance",
                    content="Attach evidence and confirm acceptance criteria.",
                    tags=["review", "acceptance"],
                    goal_id=goal.id,
                    source_uri="file:///tmp/rubric.md",
                )
            )

            reopened = SQLiteStore(db_path)
            persisted = reopened.knowledge_bases.get(item.id)

            self.assertEqual(persisted.name, "Reviewer rubric")
            self.assertEqual(persisted.goal_id, goal.id)
            self.assertEqual(reopened.board_snapshot()["knowledge_bases"]["draft"], 1)


if __name__ == "__main__":
    unittest.main()
