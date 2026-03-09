from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any

from playbookos.executor import OpenAIExecutionConfig


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


class RuntimeSettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self._lock = RLock()
        self._model_settings = RuntimeModelSettings()
        self._load()

    def _load(self) -> None:
        if not self.path or not self.path.exists():
            return
        payload = json.loads(self.path.read_text() or "{}")
        model = payload.get("model", {})
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
                    }
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
            return {"model": self._model_settings.to_public_dict(effective=effective)}

    def update_model_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            if payload.get("clear_api_key"):
                self._model_settings.api_key = None
            elif "api_key" in payload and str(payload.get("api_key") or "").strip():
                self._model_settings.api_key = str(payload.get("api_key") or "").strip()
            for field_name in ["base_url", "model", "api_format", "organization", "project"]:
                if field_name in payload:
                    value = str(payload.get(field_name) or "").strip() or None
                    setattr(self._model_settings, field_name, value)
            if "timeout_seconds" in payload:
                value = payload.get("timeout_seconds")
                self._model_settings.timeout_seconds = float(value) if value not in {None, ""} else None
            if "temperature" in payload:
                value = payload.get("temperature")
                self._model_settings.temperature = float(value) if value not in {None, ""} else None
            if "max_output_tokens" in payload:
                value = payload.get("max_output_tokens")
                self._model_settings.max_output_tokens = int(value) if value not in {None, ""} else None
            if self._model_settings.api_format not in {None, "responses", "chat.completions"}:
                self._model_settings.api_format = "responses"
            self._save()
            return self.get_settings()


def create_runtime_settings_store_from_env() -> RuntimeSettingsStore:
    raw_path = (os.getenv("PLAYBOOKOS_RUNTIME_SETTINGS_PATH") or "data/runtime_settings.json").strip()
    return RuntimeSettingsStore(Path(raw_path) if raw_path else None)


def _mask_secret(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}***{value[-4:]}"
