import unittest

from playbookos.ui import build_dashboard_html


class DashboardHtmlTestCase(unittest.TestCase):
    def test_dashboard_html_includes_core_sections_and_endpoints(self) -> None:
        html = build_dashboard_html(
            {
                "goals": {"draft": 1, "blocked": 2},
                "tasks": {"ready": 3},
                "runs": {"waiting_human": 1, "succeeded": 5},
                "artifacts": {"run_report": 4},
                "reflections": {"proposed": 2, "published": 1},
            }
        )

        self.assertIn("PlaybookOS Console", html)
        self.assertIn("Control Board", html)
        self.assertIn("Quick Resource Peek", html)
        self.assertIn("/api/board", html)
        self.assertIn("/api/goals", html)
        self.assertIn("/api/artifacts", html)
        self.assertIn('const apiBase = "/api";', html)
        self.assertIn('"artifacts": {"run_report": 4}', html)

    def test_dashboard_html_escapes_custom_api_base(self) -> None:
        html = build_dashboard_html({"goals": {}}, api_base='/api" onclick="alert(1)')

        self.assertIn("&quot; onclick=&quot;alert(1)", html)
        self.assertNotIn('<a class="endpoint-link" href="/api" onclick="alert(1)/goals"', html)


if __name__ == "__main__":
    unittest.main()
