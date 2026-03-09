import tempfile
import unittest
from pathlib import Path

from playbookos.domain.models import Playbook
from playbookos.object_store import LocalObjectStore, attach_source_object_to_playbook


class ObjectStoreTestCase(unittest.TestCase):
    def test_local_object_store_round_trip_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalObjectStore(tmpdir)

            stored = store.put_text(
                kind="sop_source",
                title="Demo SOP",
                text="# Demo\nstep 1",
                mime_type="text/markdown; charset=utf-8",
                suffix=".md",
                metadata={"source_kind": "markdown"},
            )

            self.assertTrue((Path(tmpdir) / f"{stored.id}.md").exists())
            self.assertTrue((Path(tmpdir) / f"{stored.id}.json").exists())
            self.assertEqual(store.get_meta(stored.id).checksum, stored.checksum)
            self.assertEqual(store.get_text(stored.id), "# Demo\nstep 1")
            self.assertEqual(store.list_objects()[0].id, stored.id)

    def test_attach_source_object_updates_playbook_compiled_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalObjectStore(tmpdir)
            playbook = Playbook(name="Launch SOP", source_kind="markdown", source_uri="file:///tmp/launch.md")

            stored = attach_source_object_to_playbook(
                playbook,
                source_text="# Launch\n1. Draft note",
                source_kind="markdown",
                source_uri="file:///tmp/launch.md",
                object_store=store,
            )

            self.assertEqual(playbook.compiled_spec["source_object_id"], stored.id)
            self.assertEqual(playbook.compiled_spec["source_object_uri"], stored.uri)
            self.assertEqual(playbook.compiled_spec["source_object_checksum"], stored.checksum)
            self.assertEqual(playbook.compiled_spec["source_object_mime_type"], stored.mime_type)
            self.assertEqual(stored.metadata["playbook_id"], playbook.id)
            self.assertEqual(stored.metadata["source_uri"], "file:///tmp/launch.md")


if __name__ == "__main__":
    unittest.main()
