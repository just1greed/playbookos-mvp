import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from playbookos.executor.service import ExecutionError
from playbookos.runtime_settings import RuntimeSettingsStore

try:
    from fastapi.testclient import TestClient
    from playbookos.api.app import create_app
    from playbookos.api.store import InMemoryStore
except ModuleNotFoundError:
    TestClient = None
    create_app = None
    InMemoryStore = None


class FakeProbeTransport:
    def __init__(self, response_payload: dict | None = None, error: Exception | None = None) -> None:
        self.response_payload = response_payload or {}
        self.error = error
        self.calls: list[dict] = []

    def post_json(self, url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict:
        self.calls.append({
            "url": url,
            "headers": headers,
            "payload": payload,
            "timeout_seconds": timeout_seconds,
        })
        if self.error is not None:
            raise self.error
        return self.response_payload


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
        self.assertEqual(settings["provider_presets"][0]["id"], "openai-responses")
        self.assertEqual(settings["global"]["environment_label"], "local")
        self.assertEqual(settings["model_profiles"], [])
        self.assertIsNone(settings["active_model_profile"])
        self.assertIsNone(settings["last_successful_model_test"])

    def test_model_connectivity_probe_handles_missing_key(self) -> None:
        with patch.dict(os.environ, {"PLAYBOOKOS_OPENAI_API_KEY": ""}, clear=False):
            store = RuntimeSettingsStore(path=None)
            result = store.test_model_settings({"model": "gpt-4.1"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "missing_api_key")
        self.assertIn("No API key configured", result["message"])

    def test_model_connectivity_probe_uses_transport(self) -> None:
        transport = FakeProbeTransport(
            response_payload={
                "id": "resp-123",
                "model": "gpt-4.1-mini",
                "output": [
                    {"content": [{"type": "output_text", "text": "PONG"}]}
                ],
                "usage": {"total_tokens": 9},
            }
        )
        with patch.dict(
            os.environ,
            {
                "PLAYBOOKOS_OPENAI_API_KEY": "env-secret-key",
                "PLAYBOOKOS_OPENAI_BASE_URL": "https://api.openai.com/v1",
                "PLAYBOOKOS_OPENAI_MODEL": "gpt-4.1",
            },
            clear=False,
        ):
            store = RuntimeSettingsStore(path=None)
            result = store.test_model_settings({"provider_preset": "openai-responses", "model": "gpt-4.1-mini"}, transport=transport)

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["response_id"], "resp-123")
        self.assertEqual(result["output_preview"], "PONG")
        self.assertEqual(transport.calls[0]["url"], "https://api.openai.com/v1/responses")
        self.assertEqual(transport.calls[0]["payload"]["model"], "gpt-4.1-mini")
        self.assertEqual(result["last_successful_model_test"]["response_id"], "resp-123")
        self.assertEqual(store.get_settings()["last_successful_model_test"]["response_id"], "resp-123")

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
            global_updated = reloaded.update_global_settings({"default_language": "en", "auto_refresh_seconds": 15, "default_scope_kind": "status", "default_route": "tasks", "show_system_group": False, "environment_label": "staging"})
            profiled = reloaded.save_model_profile("staging", {"model": "gpt-4.1-mini", "base_url": "https://proxy.example.com/v1", "api_format": "responses"}, make_active=True)
            activated = reloaded.activate_model_profile("staging")
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
        self.assertEqual(global_updated["global"]["environment_label"], "staging")
        self.assertTrue(global_updated["global"]["has_overrides"])
        self.assertEqual(profiled["active_model_profile"], "staging")
        self.assertEqual(profiled["model_profiles"][0]["name"], "staging")
        self.assertEqual(activated["active_model_profile"], "staging")
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
                        "show_system_group": False,
                        "environment_label": "staging",
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
        self.assertEqual(updated.json()["global"]["environment_label"], "staging")


    def test_ingest_api_rejects_non_markdown_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "PLAYBOOKOS_RUNTIME_SETTINGS_PATH": f"{tmpdir}/runtime_settings.json",
            },
            clear=False,
        ):
            app = create_app(store=InMemoryStore())
            client = TestClient(app)

            response = client.post(
                "/api/playbooks/ingest",
                json={
                    "name": "Structured SOP",
                    "source_kind": "json",
                    "source_text": '{"steps": [{"name": "Prepare draft"}]}',
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Only Markdown SOP ingestion is supported right now", response.json()["detail"])

    def test_runtime_settings_profile_endpoints_validate_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, patch.dict(
            os.environ,
            {
                "PLAYBOOKOS_RUNTIME_SETTINGS_PATH": f"{tmpdir}/runtime_settings.json",
                "PLAYBOOKOS_OPENAI_BASE_URL": "https://api.openai.com/v1",
                "PLAYBOOKOS_OPENAI_MODEL": "gpt-4.1",
                "PLAYBOOKOS_OPENAI_API_KEY": "env-secret-key",
            },
            clear=False,
        ):
            app = create_app(store=InMemoryStore())
            client = TestClient(app)

            saved = client.post(
                "/api/runtime-settings/profiles",
                json={
                    "name": "staging",
                    "model": {
                        "model": "gpt-4.1-mini",
                        "base_url": "https://proxy.example.com/v1",
                        "api_format": "responses",
                    },
                },
            )
            missing = client.post("/api/runtime-settings/profiles/activate", json={"name": ""})
            activated = client.post("/api/runtime-settings/profiles/activate", json={"name": "staging"})

        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json()["model_profiles"][0]["name"], "staging")
        self.assertEqual(missing.status_code, 400)
        self.assertEqual(missing.json()["detail"], "Profile name is required")
        self.assertEqual(activated.status_code, 200)
        self.assertEqual(activated.json()["active_model_profile"], "staging")


if __name__ == "__main__":
    unittest.main()
