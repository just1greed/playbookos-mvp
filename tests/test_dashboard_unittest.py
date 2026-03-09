import unittest

from playbookos.ui import build_dashboard_html


class DashboardHtmlTestCase(unittest.TestCase):
    def test_dashboard_html_includes_workbench_bilingual_toggle_and_new_resources(self) -> None:
        html = build_dashboard_html(
            {
                "goals": {"draft": 1, "blocked": 2},
                "playbooks": {"compiled": 1},
                "knowledge_bases": {"draft": 2},
                "tasks": {"ready": 3},
                "runs": {"waiting_human": 1, "succeeded": 5},
                "acceptances": {"accepted": 1},
                "artifacts": {"run_report": 4},
                "reflections": {"proposed": 2, "published": 1},
            }
        )

        self.assertIn("PlaybookOS 控制台", html)
        self.assertIn("PlaybookOS Console", html)
        self.assertIn('id="lang-zh"', html)
        self.assertIn('id="lang-en"', html)
        self.assertIn('localStorage.getItem(\'playbookos-language\')', html)
        self.assertIn('data-i18n="workbench_title"', html)
        self.assertIn('id="goal-form"', html)
        self.assertIn('id="playbook-form"', html)
        self.assertIn('id="knowledge-form"', html)
        self.assertIn('id="task-form"', html)
        self.assertIn('resourcePaths = {"goals": "goals"', html)
        self.assertIn('"knowledge_bases": "knowledge-bases"', html)
        self.assertIn("postJson('knowledge-bases'", html)
        self.assertIn("postJson('playbooks/import'", html)
        self.assertIn("handleWorkbenchSubmit(handleTaskSubmit, event)", html)
        self.assertIn('const apiBase = "/api";', html)
        self.assertIn('"artifacts": {"run_report": 4}', html)

    def test_dashboard_html_escapes_custom_api_base(self) -> None:
        html = build_dashboard_html({"goals": {}}, api_base='/api" onclick="alert(1)')

        self.assertIn("&quot; onclick=&quot;alert(1)", html)
        self.assertNotIn('<a class="endpoint-link" href="/api" onclick="alert(1)/goals"', html)


if __name__ == "__main__":
    unittest.main()
