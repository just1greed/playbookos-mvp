import tempfile
import unittest
from pathlib import Path

from playbookos.domain.models import Artifact, Goal, MCPServer, Playbook, Reflection, Run, Skill, Task
from playbookos.persistence.sqlite_store import SQLiteStore


class SQLiteStoreTestCase(unittest.TestCase):
    def test_store_persists_entities_across_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "playbookos.db"
            first_store = SQLiteStore(db_path)
            goal = first_store.goals.save(Goal(title="Persist goal", objective="Keep state on disk"))
            skill = first_store.skills.save(
                Skill(name="Persist skill", description="Keep reusable worker profile", input_schema={}, output_schema={})
            )
            mcp_server = first_store.mcp_servers.save(
                MCPServer(name="github", transport="streamable_http", endpoint="https://example.com/mcp/github")
            )
            playbook = first_store.playbooks.save(
                Playbook(name="Persist playbook", source_kind="markdown", source_uri="file:///tmp/demo.md", goal_id=goal.id)
            )
            task = first_store.tasks.save(
                Task(goal_id=goal.id, playbook_id=playbook.id, name="Persist task", description="Check sqlite storage", assigned_skill_id=skill.id)
            )
            run = first_store.runs.save(Run(task_id=task.id, worker_type="agents-sdk"))
            first_store.artifacts.save(
                Artifact(
                    run_id=run.id,
                    kind="run_report",
                    title="Persisted report",
                    uri="playbookos://runs/demo/report.json",
                    mime_type="application/json",
                    metadata={"task_id": task.id},
                )
            )
            first_store.reflections.save(
                Reflection(
                    run_id=run.id,
                    failure_category="none",
                    summary="Persistence works",
                    proposal={"next": "postgres"},
                )
            )

            second_store = SQLiteStore(db_path)
            self.assertEqual(second_store.goals.get(goal.id).title, "Persist goal")
            self.assertEqual(second_store.skills.get(skill.id).name, "Persist skill")
            self.assertEqual(second_store.mcp_servers.get(mcp_server.id).name, "github")
            self.assertEqual(second_store.tasks.get(task.id).goal_id, goal.id)
            self.assertEqual(second_store.tasks.get(task.id).assigned_skill_id, skill.id)
            self.assertEqual(second_store.runs.get(run.id).task_id, task.id)
            self.assertEqual(second_store.artifacts.list()[0].metadata["task_id"], task.id)
            self.assertEqual(second_store.board_snapshot()["skills"]["draft"], 1)
            self.assertEqual(second_store.board_snapshot()["mcp_servers"]["active"], 1)
            self.assertEqual(second_store.board_snapshot()["artifacts"]["run_report"], 1)
            self.assertEqual(second_store.board_snapshot()["reflections"]["proposed"], 1)


if __name__ == "__main__":
    unittest.main()
