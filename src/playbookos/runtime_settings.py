from __future__ import annotations

import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from threading import RLock
from typing import Any

from playbookos.domain.models import utc_now
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
class ModelProfile:
    name: str
    settings: RuntimeModelSettings
    updated_at: str

    def to_public_dict(self) -> dict[str, Any]:
        effective = self.settings.merge(OpenAIExecutionConfig.from_env())
        return {
            "name": self.name,
            "updated_at": self.updated_at,
            **self.settings.to_public_dict(effective=effective),
        }


@dataclass(slots=True)
class RuntimeGlobalSettings:
    default_language: str | None = None
    auto_refresh_seconds: int | None = None
    default_scope_kind: str | None = None
    default_route: str | None = None
    show_system_group: bool | None = None
    environment_label: str | None = None

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
        environment_label = (self.environment_label or _environment_label_from_env()).strip() or "local"
        return {
            "default_language": default_language,
            "auto_refresh_seconds": auto_refresh_seconds,
            "default_scope_kind": default_scope_kind,
            "default_route": default_route,
            "show_system_group": bool(show_system_group),
            "environment_label": environment_label,
            "has_overrides": any(
                value is not None
                for value in [
                    self.default_language,
                    self.auto_refresh_seconds,
                    self.default_scope_kind,
                    self.default_route,
                    self.show_system_group,
                    self.environment_label,
                ]
            ),
        }


class RuntimeSettingsStore:
    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._lock = RLock()
        self._model_settings = RuntimeModelSettings()
        self._global_settings = RuntimeGlobalSettings()
        self._model_profiles: dict[str, ModelProfile] = {}
        self._active_model_profile: str | None = None
        self._last_successful_model_test: dict[str, Any] | None = None
        self._load()

    def _load(self) -> None:
        if not self.path or not self.path.exists():
            return
        payload = json.loads(self.path.read_text() or "{}")
        model = payload.get("model", {})
        global_settings = payload.get("global", {})
        self._model_settings = _runtime_model_settings_from_dict(model)
        self._global_settings = RuntimeGlobalSettings(
            default_language=(str(global_settings.get("default_language") or "").strip() or None),
            auto_refresh_seconds=int(global_settings["auto_refresh_seconds"]) if global_settings.get("auto_refresh_seconds") not in {None, ""} else None,
            default_scope_kind=(str(global_settings.get("default_scope_kind") or "").strip() or None),
            default_route=(str(global_settings.get("default_route") or "").strip() or None),
            show_system_group=bool(global_settings["show_system_group"]) if global_settings.get("show_system_group") is not None else None,
            environment_label=(str(global_settings.get("environment_label") or "").strip() or None),
        )
        self._active_model_profile = (str(payload.get("active_model_profile") or "").strip() or None)
        self._last_successful_model_test = dict(payload.get("last_successful_model_test") or {}) or None
        self._model_profiles = {}
        for item in payload.get("model_profiles", []) or []:
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            self._model_profiles[name] = ModelProfile(
                name=name,
                settings=_runtime_model_settings_from_dict(item.get("settings", {})),
                updated_at=str(item.get("updated_at") or utc_now().isoformat()),
            )

    def _save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "model": _runtime_model_settings_to_dict(self._model_settings),
                    "global": {
                        "default_language": self._global_settings.default_language,
                        "auto_refresh_seconds": self._global_settings.auto_refresh_seconds,
                        "default_scope_kind": self._global_settings.default_scope_kind,
                        "default_route": self._global_settings.default_route,
                        "show_system_group": self._global_settings.show_system_group,
                        "environment_label": self._global_settings.environment_label,
                    },
                    "model_profiles": [
                        {
                            "name": item.name,
                            "updated_at": item.updated_at,
                            "settings": _runtime_model_settings_to_dict(item.settings),
                        }
                        for item in self.model_profiles()
                    ],
                    "active_model_profile": self._active_model_profile,
                    "last_successful_model_test": self._last_successful_model_test,
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
                "model_profiles": [item.to_public_dict() for item in self.model_profiles()],
                "active_model_profile": self._active_model_profile,
                "last_successful_model_test": dict(self._last_successful_model_test or {}) or None,
            }

    def model_profiles(self) -> list[ModelProfile]:
        return sorted(self._model_profiles.values(), key=lambda item: (item.updated_at, item.name), reverse=True)

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
            if model_payload:
                self._apply_model_settings_to(self._model_settings, model_payload)
                self._active_model_profile = None
            self._apply_global_settings(global_payload)
            self._save()
            return self.get_settings()

    def save_model_profile(self, name: str, payload: dict[str, Any] | None = None, *, make_active: bool = False) -> dict[str, Any]:
        profile_name = str(name or "").strip()
        if not profile_name:
            raise ValueError("Profile name is required")
        with self._lock:
            candidate = replace(self._model_settings)
            self._apply_model_settings_to(candidate, dict(payload or {}))
            self._model_profiles[profile_name] = ModelProfile(
                name=profile_name,
                settings=candidate,
                updated_at=utc_now().isoformat(),
            )
            if make_active:
                self._model_settings = replace(candidate)
                self._active_model_profile = profile_name
            self._save()
            return self.get_settings()

    def activate_model_profile(self, name: str) -> dict[str, Any]:
        profile_name = str(name or "").strip()
        if not profile_name:
            raise ValueError("Profile name is required")
        with self._lock:
            profile = self._model_profiles.get(profile_name)
            if profile is None:
                raise ValueError(f"Unknown model profile: {profile_name}")
            self._model_settings = replace(profile.settings)
            self._active_model_profile = profile_name
            self._save()
            return self.get_settings()

    def test_model_settings(
        self,
        payload: dict[str, Any] | None = None,
        *,
        transport: OpenAITransport | None = None,
    ) -> dict[str, Any]:
        model_payload = dict(payload or {})
        with self._lock:
            candidate = replace(self._model_settings)
            self._apply_model_settings_to(candidate, model_payload)
            effective = candidate.merge(OpenAIExecutionConfig.from_env())
            active_profile = self._active_model_profile
        request_url = effective.request_url()
        result: dict[str, Any] = {
            "ok": False,
            "request_url": request_url,
            "api_format": effective.api_format,
            "model": effective.model,
            "base_url": effective.base_url,
            "has_api_key": bool(effective.api_key),
            "mode": "probe",
            "active_model_profile": active_profile,
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
        success = {
            "tested_at": utc_now().isoformat(),
            "request_url": request_url,
            "api_format": effective.api_format,
            "model": effective.model,
            "base_url": effective.base_url,
            "response_id": response.get("id"),
            "response_model": response.get("model", effective.model),
            "output_preview": _probe_output_preview(effective.api_format, response),
            "active_model_profile": active_profile,
            "provider_preset": str(model_payload.get("provider_preset") or "").strip() or None,
        }
        with self._lock:
            self._last_successful_model_test = success
            self._save()
        result.update(
            {
                "ok": True,
                "status": "ok",
                "message": "Connectivity test succeeded.",
                "response_id": response.get("id"),
                "response_model": response.get("model", effective.model),
                "usage": response.get("usage", {}),
                "output_preview": success["output_preview"],
                "last_successful_model_test": success,
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
                for field_name in ["base_url", "api_format", "model"]:
                    if field_name not in payload:
                        payload[field_name] = preset.get(field_name, "")
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
        if "environment_label" in payload:
            value = str(payload.get("environment_label") or "").strip() or None
            self._global_settings.environment_label = value


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


def _runtime_model_settings_to_dict(settings: RuntimeModelSettings) -> dict[str, Any]:
    return {
        "api_key": settings.api_key,
        "base_url": settings.base_url,
        "model": settings.model,
        "api_format": settings.api_format,
        "timeout_seconds": settings.timeout_seconds,
        "temperature": settings.temperature,
        "max_output_tokens": settings.max_output_tokens,
        "organization": settings.organization,
        "project": settings.project,
    }


def _runtime_model_settings_from_dict(payload: dict[str, Any]) -> RuntimeModelSettings:
    return RuntimeModelSettings(
        api_key=payload.get("api_key"),
        base_url=payload.get("base_url"),
        model=payload.get("model"),
        api_format=payload.get("api_format"),
        timeout_seconds=float(payload["timeout_seconds"]) if payload.get("timeout_seconds") not in {None, ""} else None,
        temperature=float(payload["temperature"]) if payload.get("temperature") not in {None, ""} else None,
        max_output_tokens=int(payload["max_output_tokens"]) if payload.get("max_output_tokens") not in {None, ""} else None,
        organization=payload.get("organization"),
        project=payload.get("project"),
    )


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


def _environment_label_from_env() -> str:
    return (os.getenv("PLAYBOOKOS_ENVIRONMENT_LABEL") or "local").strip() or "local"


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
