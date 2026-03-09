from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from threading import RLock
from typing import Any

from playbookos.executor import OpenAIExecutionConfig
from playbookos.executor.service import ExecutionError, OpenAITransport, UrllibOpenAITransport

_ALLOWED_LANGUAGES = {"zh", "en"}
_ALLOWED_SCOPE_KINDS = {"all", "goal", "playbook", "status"}
_ALLOWED_ROUTES = {
    "dashboard",
    "goals",
    "playbooks",
    "skills",
    "mcp",
    "knowledge",
    "tasks",
    "sessions",
    "learning",
    "approvals",
    "prompts",
    "model-settings",
    "global-settings",
    "session-admin",
    "system",
}
_PROVIDER_PRESETS = [
    {
        "id": "openai-responses",
        "label": "OpenAI / Responses",
        "base_url": "https://api.openai.com/v1",
        "api_format": "responses",
        "model": "gpt-4.1",
        "description": "Default OpenAI Responses API preset.",
    },
    {
        "id": "openai-chat",
        "label": "OpenAI / Chat Completions",
        "base_url": "https://api.openai.com/v1",
        "api_format": "chat.completions",
        "model": "gpt-4.1-mini",
        "description": "Compatibility preset using chat.completions.",
    },
    {
        "id": "custom-compatible",
        "label": "Custom OpenAI-Compatible",
        "base_url": "",
        "api_format": "responses",
        "model": "",
        "description": "Fill in your own compatible gateway and model.",
    },
]


@dataclass(slots=True)
class RuntimeModelSettings:
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    api_format: str | None = None
    timeout_seconds: float | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    organization: str | None = None
    project: str | None = None

    def merge(self, base: OpenAIExecutionConfig) -> OpenAIExecutionConfig:
        return OpenAIExecutionConfig(
            api_key=self.api_key if self.api_key not in {None, ""} else base.api_key,
            base_url=(self.base_url or base.base_url).rstrip("/"),
            model=self.model or base.model,
            api_format=self.api_format or base.api_format,
            timeout_seconds=float(self.timeout_seconds) if self.timeout_seconds is not None else base.timeout_seconds,
            temperature=self.temperature if self.temperature is not None else base.temperature,
            max_output_tokens=self.max_output_tokens if self.max_output_tokens is not None else base.max_output_tokens,
            organization=self.organization if self.organization not in {None, ""} else base.organization,
            project=self.project if self.project not in {None, ""} else base.project,
        )

    def to_public_dict(self, *, effective: OpenAIExecutionConfig) -> dict[str, Any]:
        api_key = self.api_key if self.api_key not in {None, ""} else effective.api_key
        return {
            "base_url": effective.base_url,
            "model": effective.model,
            "api_format": effective.api_format,
            "timeout_seconds": effective.timeout_seconds,
            "temperature": effective.temperature,
            "max_output_tokens": effective.max_output_tokens,
            "organization": effective.organization,
            "project": effective.project,
            "has_api_key": bool(api_key),
            "api_key_preview": _mask_secret(api_key),
            "has_overrides": any(
                value not in {None, ""}
                for value in [
                    self.api_key,
                    self.base_url,
                    self.model,
                    self.api_format,
                    self.timeout_seconds,
                    self.temperature,
                    self.max_output_tokens,
                    self.organization,
                    self.project,
                ]
            ),
        }


@dataclass(slots=True)
class RuntimeGlobalSettings:
    default_language: str | None = None
    auto_refresh_seconds: int | None = None
    default_scope_kind: str | None = None
    default_route: str | None = None
    show_system_group: bool | None = None

    def effective(self) -> dict[str, Any]:
        default_language = self.default_language or _default_language_from_env()
        if default_language not in _ALLOWED_LANGUAGES:
            default_language = "zh"
        default_scope_kind = self.default_scope_kind or _default_scope_kind_from_env()
        if default_scope_kind not in _ALLOWED_SCOPE_KINDS:
            default_scope_kind = "all"
        default_route = self.default_route or _default_route_from_env()
        if default_route not in _ALLOWED_ROUTES:
            default_route = "dashboard"
        auto_refresh_seconds = self.auto_refresh_seconds
        if auto_refresh_seconds is None:
            auto_refresh_seconds = _auto_refresh_seconds_from_env()
        auto_refresh_seconds = max(0, int(auto_refresh_seconds))
        show_system_group = self.show_system_group
        if show_system_group is None:
            show_system_group = _show_system_group_from_env()
        return {
            "default_language": default_language,
            "auto_refresh_seconds": auto_refresh_seconds,
            "default_scope_kind": default_scope_kind,
            "default_route": default_route,
            "show_system_group": bool(show_system_group),
            "has_overrides": any(
                value is not None
                for value in [
                    self.default_language,
                    self.auto_refresh_seconds,
                    self.default_scope_kind,
                    self.default_route,
                    self.show_system_group,
                ]
            ),
        }


class RuntimeSettingsStore:
    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._lock = RLock()
        self._model_settings = RuntimeModelSettings()
        self._global_settings = RuntimeGlobalSettings()
        self._load()

    def _load(self) -> None:
        if not self.path or not self.path.exists():
            return
        payload = json.loads(self.path.read_text() or "{}")
        model = payload.get("model", {})
        global_settings = payload.get("global", {})
        self._model_settings = RuntimeModelSettings(
            api_key=model.get("api_key"),
            base_url=model.get("base_url"),
            model=model.get("model"),
            api_format=model.get("api_format"),
            timeout_seconds=float(model["timeout_seconds"]) if model.get("timeout_seconds") not in {None, ""} else None,
            temperature=float(model["temperature"]) if model.get("temperature") not in {None, ""} else None,
            max_output_tokens=int(model["max_output_tokens"]) if model.get("max_output_tokens") not in {None, ""} else None,
            organization=model.get("organization"),
            project=model.get("project"),
        )
        self._global_settings = RuntimeGlobalSettings(
            default_language=(str(global_settings.get("default_language") or "").strip() or None),
            auto_refresh_seconds=int(global_settings["auto_refresh_seconds"]) if global_settings.get("auto_refresh_seconds") not in {None, ""} else None,
            default_scope_kind=(str(global_settings.get("default_scope_kind") or "").strip() or None),
            default_route=(str(global_settings.get("default_route") or "").strip() or None),
            show_system_group=bool(global_settings["show_system_group"]) if global_settings.get("show_system_group") is not None else None,
        )

    def _save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "model": {
                        "api_key": self._model_settings.api_key,
                        "base_url": self._model_settings.base_url,
                        "model": self._model_settings.model,
                        "api_format": self._model_settings.api_format,
                        "timeout_seconds": self._model_settings.timeout_seconds,
                        "temperature": self._model_settings.temperature,
                        "max_output_tokens": self._model_settings.max_output_tokens,
                        "organization": self._model_settings.organization,
                        "project": self._model_settings.project,
                    },
                    "global": {
                        "default_language": self._global_settings.default_language,
                        "auto_refresh_seconds": self._global_settings.auto_refresh_seconds,
                        "default_scope_kind": self._global_settings.default_scope_kind,
                        "default_route": self._global_settings.default_route,
                        "show_system_group": self._global_settings.show_system_group,
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    def openai_config(self) -> OpenAIExecutionConfig:
        with self._lock:
            return self._model_settings.merge(OpenAIExecutionConfig.from_env())

    def get_settings(self) -> dict[str, Any]:
        with self._lock:
            effective = self.openai_config()
            return {
                "model": self._model_settings.to_public_dict(effective=effective),
                "global": self._global_settings.effective(),
                "provider_presets": provider_presets(),
            }

    def update_model_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.update_settings({"model": payload})

    def update_global_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.update_settings({"global": payload})

    def update_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            model_payload: dict[str, Any]
            global_payload: dict[str, Any]
            if "model" in payload or "global" in payload:
                model_payload = dict(payload.get("model") or {})
                global_payload = dict(payload.get("global") or {})
            else:
                model_payload = dict(payload)
                global_payload = {}
            self._apply_model_settings_to(self._model_settings, model_payload)
            self._apply_global_settings(global_payload)
            self._save()
            return self.get_settings()

    def test_model_settings(
        self,
        payload: dict[str, Any] | None = None,
        *,
        transport: OpenAITransport | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            candidate = replace(self._model_settings)
            self._apply_model_settings_to(candidate, dict(payload or {}))
            effective = candidate.merge(OpenAIExecutionConfig.from_env())
        request_url = effective.request_url()
        result: dict[str, Any] = {
            "ok": False,
            "request_url": request_url,
            "api_format": effective.api_format,
            "model": effective.model,
            "base_url": effective.base_url,
            "has_api_key": bool(effective.api_key),
            "mode": "probe",
        }
        if not effective.api_key:
            result.update(
                {
                    "status": "missing_api_key",
                    "message": "No API key configured. Save a key or provide one before testing connectivity.",
                }
            )
            return result
        probe_payload = _probe_payload(effective)
        probe_transport = transport or UrllibOpenAITransport()
        try:
            response = probe_transport.post_json(
                request_url,
                effective.headers(),
                probe_payload,
                min(float(effective.timeout_seconds), 10.0),
            )
        except ExecutionError as exc:
            result.update(
                {
                    "status": "error",
                    "message": str(exc),
                    "error_class": exc.__class__.__name__,
                }
            )
            return result
        result.update(
            {
                "ok": True,
                "status": "ok",
                "message": "Connectivity test succeeded.",
                "response_id": response.get("id"),
                "response_model": response.get("model", effective.model),
                "usage": response.get("usage", {}),
                "output_preview": _probe_output_preview(effective.api_format, response),
            }
        )
        return result

    def _apply_model_settings_to(self, target: RuntimeModelSettings, payload: dict[str, Any]) -> None:
        if not payload:
            return
        preset_id = str(payload.get("provider_preset") or "").strip()
        if preset_id:
            preset = provider_preset_by_id(preset_id)
            if preset is not None:
                preset_payload = {
                    "base_url": preset.get("base_url", ""),
                    "api_format": preset.get("api_format", "responses"),
                    "model": preset.get("model", ""),
                }
                for field_name in ["base_url", "api_format", "model"]:
                    if field_name not in payload:
                        payload[field_name] = preset_payload[field_name]
        if payload.get("clear_api_key"):
            target.api_key = None
        elif "api_key" in payload and str(payload.get("api_key") or "").strip():
            target.api_key = str(payload.get("api_key") or "").strip()
        for field_name in ["base_url", "model", "api_format", "organization", "project"]:
            if field_name in payload:
                value = str(payload.get(field_name) or "").strip() or None
                setattr(target, field_name, value)
        if "timeout_seconds" in payload:
            value = payload.get("timeout_seconds")
            target.timeout_seconds = float(value) if value not in {None, ""} else None
        if "temperature" in payload:
            value = payload.get("temperature")
            target.temperature = float(value) if value not in {None, ""} else None
        if "max_output_tokens" in payload:
            value = payload.get("max_output_tokens")
            target.max_output_tokens = int(value) if value not in {None, ""} else None
        if target.api_format not in {None, "responses", "chat.completions"}:
            target.api_format = "responses"

    def _apply_global_settings(self, payload: dict[str, Any]) -> None:
        if not payload:
            return
        if "default_language" in payload:
            value = str(payload.get("default_language") or "").strip() or None
            self._global_settings.default_language = value if value in _ALLOWED_LANGUAGES else "zh"
        if "auto_refresh_seconds" in payload:
            value = payload.get("auto_refresh_seconds")
            self._global_settings.auto_refresh_seconds = max(0, int(value)) if value not in {None, ""} else None
        if "default_scope_kind" in payload:
            value = str(payload.get("default_scope_kind") or "").strip() or None
            self._global_settings.default_scope_kind = value if value in _ALLOWED_SCOPE_KINDS else "all"
        if "default_route" in payload:
            value = str(payload.get("default_route") or "").strip() or None
            self._global_settings.default_route = value if value in _ALLOWED_ROUTES else "dashboard"
        if "show_system_group" in payload:
            value = payload.get("show_system_group")
            self._global_settings.show_system_group = bool(value) if value is not None else None


def create_runtime_settings_store_from_env() -> RuntimeSettingsStore:
    raw_path = (os.getenv("PLAYBOOKOS_RUNTIME_SETTINGS_PATH") or "data/runtime_settings.json").strip()
    return RuntimeSettingsStore(Path(raw_path) if raw_path else None)


def provider_presets() -> list[dict[str, Any]]:
    return [dict(item) for item in _PROVIDER_PRESETS]


def provider_preset_by_id(preset_id: str) -> dict[str, Any] | None:
    target = str(preset_id or "").strip()
    for item in _PROVIDER_PRESETS:
        if item["id"] == target:
            return dict(item)
    return None


def _probe_payload(config: OpenAIExecutionConfig) -> dict[str, Any]:
    if config.api_format == "chat.completions":
        return {
            "model": config.model,
            "messages": [
                {"role": "system", "content": "Reply with a short connectivity confirmation."},
                {"role": "user", "content": "Reply with the single word PONG."},
            ],
            "max_tokens": 16,
            "temperature": 0,
        }
    return {
        "model": config.model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Reply with the single word PONG."},
                ],
            }
        ],
        "max_output_tokens": 16,
        "temperature": 0,
    }


def _probe_output_preview(api_format: str, response: dict[str, Any]) -> str:
    if api_format == "chat.completions":
        choices = response.get("choices") or []
        if choices and isinstance(choices[0], dict):
            message = choices[0].get("message") or {}
            content = message.get("content")
            if isinstance(content, str):
                return content[:120]
        return ""
    output = response.get("output") or []
    for item in output:
        if not isinstance(item, dict):
            continue
        for content in item.get("content") or []:
            if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                return str(content.get("text") or "")[:120]
    return str(response.get("output_text") or "")[:120]


def _default_language_from_env() -> str:
    value = (os.getenv("PLAYBOOKOS_DEFAULT_LANGUAGE") or "zh").strip().lower()
    return value if value in _ALLOWED_LANGUAGES else "zh"


def _default_scope_kind_from_env() -> str:
    value = (os.getenv("PLAYBOOKOS_DEFAULT_SCOPE_KIND") or "all").strip().lower()
    return value if value in _ALLOWED_SCOPE_KINDS else "all"


def _default_route_from_env() -> str:
    value = (os.getenv("PLAYBOOKOS_DEFAULT_ROUTE") or "dashboard").strip()
    return value if value in _ALLOWED_ROUTES else "dashboard"


def _auto_refresh_seconds_from_env() -> int:
    raw = (os.getenv("PLAYBOOKOS_AUTO_REFRESH_SECONDS") or "0").strip() or "0"
    try:
        return max(0, int(raw))
    except ValueError:
        return 0


def _show_system_group_from_env() -> bool:
    return _coerce_bool(os.getenv("PLAYBOOKOS_SHOW_SYSTEM_GROUP"), default=True)


def _coerce_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _mask_secret(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}***{value[-4:]}"
