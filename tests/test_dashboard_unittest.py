import unittest

from playbookos.ui import build_dashboard_html


class DashboardHtmlTestCase(unittest.TestCase):
    def test_dashboard_html_includes_core_sections_endpoints_and_language_toggle(self) -> None:
        html = build_dashboard_html(
            {
                "goals": {"draft": 1, "blocked": 2},
                "tasks": {"ready": 3},
                "runs": {"waiting_human": 1, "succeeded": 5},
                "artifacts": {"run_report": 4},
                "reflections": {"proposed": 2, "published": 1},
            }
        )

        self.assertIn("PlaybookOS 控制台", html)
        self.assertIn("PlaybookOS Console", html)
        self.assertIn('id="lang-zh"', html)
        self.assertIn('id="lang-en"', html)
        self.assertIn('localStorage.getItem(\'playbookos-language\')', html)
        self.assertIn('applyLanguage(\'en\')', html)
        self.assertIn('/api/board', html)
        self.assertIn("fetchJson('goals')", html)
        self.assertIn("fetchJson('skills')", html)
        self.assertIn("fetchJson('sessions')", html)
        self.assertIn("fetchJson('acceptances')", html)
        self.assertIn("fetchJson('events')", html)
        self.assertIn("fetchJson('artifacts')", html)
        self.assertIn("const endpoint = `${apiBase}/${section}`;", html)
        self.assertIn('const apiBase = "/api";', html)
        self.assertIn('"artifacts": {"run_report": 4}', html)

    def test_dashboard_html_escapes_custom_api_base(self) -> None:
        html = build_dashboard_html({"goals": {}}, api_base='/api" onclick="alert(1)')

        self.assertIn("&quot; onclick=&quot;alert(1)", html)
        self.assertNotIn('<a class="endpoint-link" href="/api" onclick="alert(1)/goals"', html)


if __name__ == "__main__":
    unittest.main()
