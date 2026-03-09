import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from playbookos.runtime_settings import RuntimeSettingsStore

try:
    from fastapi.testclient import TestClient
    from playbookos.api.app import create_app
    from playbookos.api.store import InMemoryStore
except ModuleNotFoundError:
    TestClient = None
    create_app = None
    InMemoryStore = None


class RuntimeSettingsStoreTestCase(unittest.TestCase):
    def test_store_merges_env_defaults_and_masks_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "PLAYBOOKOS_OPENAI_BASE_URL": "https://gateway.example.com/v1",
                "PLAYBOOKOS_OPENAI_MODEL": "gpt-4.1-mini",
                "PLAYBOOKOS_OPENAI_API_KEY": "env-secret-key",
                "PLAYBOOKOS_OPENAI_API_FORMAT": "chat.completions",
                "PLAYBOOKOS_RUNTIME_SETTINGS_PATH": f"{tmpdir}/runtime_settings.json",
            },
            clear=False,
        ):
            store = RuntimeSettingsStore(path=None)
            settings = store.get_settings()

        self.assertEqual(settings["model"]["base_url"], "https://gateway.example.com/v1")
        self.assertEqual(settings["model"]["model"], "gpt-4.1-mini")
        self.assertEqual(settings["model"]["api_format"], "chat.completions")
        self.assertTrue(settings["model"]["has_api_key"])
        self.assertEqual(settings["model"]["api_key_preview"], "env-***-key")
        self.assertFalse(settings["model"]["has_overrides"])
        self.assertEqual(settings["global"]["default_language"], "zh")
        self.assertEqual(settings["global"]["default_scope_kind"], "all")
        self.assertEqual(settings["global"]["default_route"], "dashboard")
        self.assertEqual(settings["global"]["auto_refresh_seconds"], 0)
        self.assertTrue(settings["global"]["show_system_group"])

    def test_store_persists_overrides_and_clears_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "PLAYBOOKOS_OPENAI_BASE_URL": "https://api.openai.com/v1",
                "PLAYBOOKOS_OPENAI_MODEL": "gpt-4.1",
                "PLAYBOOKOS_OPENAI_API_KEY": "env-secret-key",
            },
            clear=False,
        ):
            store = RuntimeSettingsStore(path=Path(tmpdir) / "runtime_settings.json")
            updated = store.update_model_settings(
                {
                    "base_url": "https://proxy.example.com/v1/",
                    "model": "gpt-4.1-nano",
                    "api_format": "invalid-format",
                    "timeout_seconds": "22",
                    "temperature": "0.7",
                    "max_output_tokens": "900",
                    "organization": "org_123",
                    "project": "proj_456",
                    "api_key": "override-secret-key",
                }
            )
            reloaded = RuntimeSettingsStore(path=Path(tmpdir) / "runtime_settings.json")
            global_updated = reloaded.update_global_settings({"default_language": "en", "auto_refresh_seconds": 15, "default_scope_kind": "status", "default_route": "tasks", "show_system_group": False})
            cleared = reloaded.update_model_settings({"clear_api_key": True})

        self.assertEqual(updated["model"]["base_url"], "https://proxy.example.com/v1")
        self.assertEqual(updated["model"]["model"], "gpt-4.1-nano")
        self.assertEqual(updated["model"]["api_format"], "responses")
        self.assertEqual(updated["model"]["timeout_seconds"], 22.0)
        self.assertEqual(updated["model"]["temperature"], 0.7)
        self.assertEqual(updated["model"]["max_output_tokens"], 900)
        self.assertEqual(updated["model"]["organization"], "org_123")
        self.assertEqual(updated["model"]["project"], "proj_456")
        self.assertEqual(updated["model"]["api_key_preview"], "over***-key")
        self.assertTrue(updated["model"]["has_overrides"])
        self.assertEqual(global_updated["global"]["default_language"], "en")
        self.assertEqual(global_updated["global"]["auto_refresh_seconds"], 15)
        self.assertEqual(global_updated["global"]["default_scope_kind"], "status")
        self.assertEqual(global_updated["global"]["default_route"], "tasks")
        self.assertFalse(global_updated["global"]["show_system_group"])
        self.assertTrue(global_updated["global"]["has_overrides"])
        self.assertTrue(cleared["model"]["has_api_key"])
        self.assertEqual(cleared["model"]["api_key_preview"], "env-***-key")


@unittest.skipIf(TestClient is None or create_app is None or InMemoryStore is None, "fastapi not installed")
class RuntimeSettingsApiTestCase(unittest.TestCase):
    def test_runtime_settings_api_reads_and_updates_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "PLAYBOOKOS_RUNTIME_SETTINGS_PATH": f"{tmpdir}/runtime_settings.json",
                "PLAYBOOKOS_OPENAI_BASE_URL": "https://gateway.example.com/v1",
                "PLAYBOOKOS_OPENAI_MODEL": "gpt-4.1",
                "PLAYBOOKOS_OPENAI_API_KEY": "env-secret-key",
            },
            clear=False,
        ):
            app = create_app(store=InMemoryStore())
            client = TestClient(app)

            current = client.get("/api/runtime-settings")
            self.assertEqual(current.status_code, 200)
            self.assertEqual(current.json()["model"]["model"], "gpt-4.1")
            self.assertEqual(current.json()["global"]["default_language"], "zh")

            updated = client.put(
                "/api/runtime-settings",
                json={
                    "model": {
                        "base_url": "https://proxy.example.com/v1",
                        "model": "gpt-4.1-mini",
                        "api_format": "chat.completions",
                        "temperature": 0.4,
                        "max_output_tokens": 1200,
                    },
                    "global": {
                        "default_language": "en",
                        "auto_refresh_seconds": 12,
                        "default_scope_kind": "status",
                        "default_route": "tasks",
                        "show_system_group": False
                    }
                },
            )

        self.assertEqual(updated.status_code, 200)
        payload = updated.json()["model"]
        self.assertEqual(payload["base_url"], "https://proxy.example.com/v1")
        self.assertEqual(payload["model"], "gpt-4.1-mini")
        self.assertEqual(payload["api_format"], "chat.completions")
        self.assertEqual(payload["temperature"], 0.4)
        self.assertEqual(payload["max_output_tokens"], 1200)
        self.assertTrue(payload["has_api_key"])
        self.assertEqual(updated.json()["global"]["default_language"], "en")
        self.assertEqual(updated.json()["global"]["auto_refresh_seconds"], 12)
        self.assertEqual(updated.json()["global"]["default_scope_kind"], "status")
        self.assertEqual(updated.json()["global"]["default_route"], "tasks")
        self.assertFalse(updated.json()["global"]["show_system_group"])


if __name__ == "__main__":
    unittest.main()
