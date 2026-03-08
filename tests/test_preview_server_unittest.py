import unittest

from playbookos.ui.preview_server import build_demo_store


class PreviewServerTestCase(unittest.TestCase):
    def test_build_demo_store_populates_dashboard_entities(self) -> None:
        store = build_demo_store()
        snapshot = store.board_snapshot()

        self.assertGreaterEqual(sum(snapshot["goals"].values()), 2)
        self.assertGreaterEqual(sum(snapshot["tasks"].values()), 2)
        self.assertGreaterEqual(sum(snapshot["runs"].values()), 2)
        self.assertGreaterEqual(sum(snapshot["artifacts"].values()), 1)
        self.assertGreaterEqual(sum(snapshot["reflections"].values()), 1)


if __name__ == "__main__":
    unittest.main()
