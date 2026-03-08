import tempfile
import unittest
from pathlib import Path

from playbookos.observability import get_error_log_path, list_recorded_errors, record_error


class ErrorLogTestCase(unittest.TestCase):
    def test_record_error_appends_jsonl_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "errors.jsonl"

            first = record_error(
                ValueError("first boom"),
                component="unit-test",
                operation="create_goal",
                metadata={"goal_id": "goal-1"},
                path=log_path,
            )
            second = record_error(
                "manual failure",
                component="unit-test",
                operation="publish_reflection",
                metadata={"reflection_id": "reflection-1"},
                path=log_path,
            )
            records = list_recorded_errors(path=log_path)

            self.assertEqual(get_error_log_path(log_path), log_path)
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["error_type"], "ValueError")
            self.assertEqual(records[0]["metadata"]["goal_id"], "goal-1")
            self.assertEqual(records[1]["error_type"], "RecordedError")
            self.assertEqual(records[1]["message"], "manual failure")
            self.assertEqual(first["operation"], "create_goal")
            self.assertEqual(second["operation"], "publish_reflection")


if __name__ == "__main__":
    unittest.main()
