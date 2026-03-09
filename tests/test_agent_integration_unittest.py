import unittest
from pathlib import Path

try:
    from fastapi.testclient import TestClient
except Exception:
    TestClient = None

try:
    from playbookos.api.app import create_app
    from playbookos.api.store import InMemoryStore
    from playbookos.domain.models import Goal, GoalStatus, MCPServer, MCPServerStatus, Run, RunStatus, Skill, SkillStatus, Task
except Exception:
    create_app = None
    InMemoryStore = None
    Goal = None
    GoalStatus = None
    MCPServer = None
    MCPServerStatus = None
    Run = None
    RunStatus = None
    Skill = None
    SkillStatus = None
    Task = None


@unittest.skipIf(TestClient is None or create_app is None or InMemoryStore is None, "fastapi not installed")
class AgentIntegrationApiTestCase(unittest.TestCase):
    def test_agent_manifest_exposes_skill_and_workflows(self) -> None:
        app = create_app(store=InMemoryStore())
        client = TestClient(app)

        response = client.get('/api/agent/manifest')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['system_name'], 'PlaybookOS')
        self.assertEqual(payload['agent_skill']['name'], 'playbookos-operator')
        self.assertIn('/api/agent/intake', payload['bootstrap_sequence'][2])
        self.assertTrue(any(item['kind'] == 'playbook' for item in payload['object_types']))

    def test_agent_context_surfaces_blockers_and_unhealthy_mcp(self) -> None:
        store = InMemoryStore()
        blocked_goal = store.goals.save(Goal(title='Blocked goal', objective='Need approval', status=GoalStatus.BLOCKED))
        task = store.tasks.save(Task(goal_id=blocked_goal.id, playbook_id='pb_1', name='Review', description='Review task'))
        store.runs.save(Run(task_id=task.id, worker_type='operator', status=RunStatus.WAITING_HUMAN))
        store.skills.save(Skill(name='Draft skill', description='Needs authoring', input_schema={}, output_schema={}, status=SkillStatus.DRAFT))
        store.mcp_servers.save(MCPServer(name='github', transport='streamable_http', endpoint='https://example.com/mcp', status=MCPServerStatus.ERROR, auth_config={'health': {'ok': False, 'status': 'network_error'}}))
        app = create_app(store=store)
        client = TestClient(app)

        response = client.get('/api/agent/context')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['system_name'], 'PlaybookOS')
        self.assertEqual(payload['focus']['blocked_goals'][0]['title'], 'Blocked goal')
        self.assertEqual(payload['focus']['waiting_human_runs'][0]['status'], 'waiting_human')
        self.assertEqual(payload['focus']['unhealthy_mcp_servers'][0]['title'], 'github')
        self.assertTrue(payload['suggested_next_actions'])

    def test_agent_intake_builds_sop_plan_without_mutating(self) -> None:
        markdown = '# Weekly report\n\n1. Research competitor updates in Notion\n2. Draft summary and send to Slack\n'
        store = InMemoryStore()
        app = create_app(store=store)
        client = TestClient(app)

        response = client.post('/api/agent/intake', json={'message': '把这份 SOP 导入系统并帮我补 skill 和 mcp', 'markdown_sop': markdown, 'resource_name': 'Weekly Report SOP'})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['execution_mode'], 'dry_run_plan_only')
        self.assertIn('playbook', payload['detected_intents'])
        self.assertEqual(payload['sop_preview']['step_count'], 2)
        self.assertIn('slack', payload['sop_preview']['detected_mcp_servers'])
        endpoints = [item['endpoint'] for item in payload['recommended_operations']]
        self.assertIn('/api/playbooks/ingest', endpoints)
        self.assertIn('/api/playbooks/{playbook_id}/skill-drafts', endpoints)
        self.assertEqual(len(store.playbooks.list()), 0)

    def test_agent_intake_rejects_empty_request(self) -> None:
        app = create_app(store=InMemoryStore())
        client = TestClient(app)

        response = client.post('/api/agent/intake', json={'message': ''})

        self.assertEqual(response.status_code, 400)
        self.assertIn('message or markdown_sop is required', response.json()['detail'])


class OperatorSkillBundleTestCase(unittest.TestCase):
    def test_operator_skill_bundle_exists(self) -> None:
        root = Path('/home/greed/playbookos-mvp/skills/playbookos-operator')
        self.assertTrue((root / 'SKILL.md').exists())
        self.assertTrue((root / 'references' / 'object-model.md').exists())
        self.assertTrue((root / 'references' / 'workflows.md').exists())
        self.assertTrue((root / 'scripts' / 'pbos_api.py').exists())


if __name__ == '__main__':
    unittest.main()
