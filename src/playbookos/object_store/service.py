from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from playbookos.domain.models import Playbook, utc_now


@dataclass(slots=True)
class StoredObject:
    id: str
    kind: str
    title: str
    mime_type: str
    uri: str
    size_bytes: int
    checksum: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


class LocalObjectStore:
    def __init__(self, root_path: str | Path) -> None:
        self.root_path = Path(root_path)
        self.root_path.mkdir(parents=True, exist_ok=True)

    def put_bytes(
        self,
        *,
        kind: str,
        title: str,
        content: bytes,
        mime_type: str,
        metadata: dict[str, Any] | None = None,
        suffix: str = ".blob",
    ) -> StoredObject:
        object_id = str(uuid4())
        checksum = hashlib.sha256(content).hexdigest()
        object_path = self.root_path / f"{object_id}{suffix}"
        object_path.write_bytes(content)
        stored = StoredObject(
            id=object_id,
            kind=kind,
            title=title,
            mime_type=mime_type,
            uri=f"playbookos://object-store/{object_id}",
            size_bytes=len(content),
            checksum=checksum,
            created_at=utc_now(),
            metadata={**(metadata or {}), "suffix": suffix},
        )
        self._write_meta(stored)
        return stored

    def put_text(
        self,
        *,
        kind: str,
        title: str,
        text: str,
        mime_type: str = "text/plain; charset=utf-8",
        metadata: dict[str, Any] | None = None,
        suffix: str = ".txt",
    ) -> StoredObject:
        return self.put_bytes(
            kind=kind,
            title=title,
            content=text.encode("utf-8"),
            mime_type=mime_type,
            metadata=metadata,
            suffix=suffix,
        )

    def list_objects(self) -> list[StoredObject]:
        items: list[StoredObject] = []
        for meta_path in sorted(self.root_path.glob("*.json")):
            items.append(self._read_meta(meta_path.stem))
        items.sort(key=lambda item: item.created_at, reverse=True)
        return items

    def get_meta(self, object_id: str) -> StoredObject:
        return self._read_meta(object_id)

    def get_bytes(self, object_id: str) -> bytes:
        meta = self.get_meta(object_id)
        suffix = str(meta.metadata.get("suffix") or ".blob")
        return (self.root_path / f"{object_id}{suffix}").read_bytes()

    def get_text(self, object_id: str) -> str:
        return self.get_bytes(object_id).decode("utf-8")

    def _meta_path(self, object_id: str) -> Path:
        return self.root_path / f"{object_id}.json"

    def _write_meta(self, stored: StoredObject) -> None:
        payload = asdict(stored)
        payload["created_at"] = stored.created_at.isoformat()
        self._meta_path(stored.id).write_text(json.dumps(payload, ensure_ascii=False, indent=2))

    def _read_meta(self, object_id: str) -> StoredObject:
        payload = json.loads(self._meta_path(object_id).read_text())
        return StoredObject(
            id=payload["id"],
            kind=payload["kind"],
            title=payload["title"],
            mime_type=payload["mime_type"],
            uri=payload["uri"],
            size_bytes=int(payload["size_bytes"]),
            checksum=payload["checksum"],
            created_at=datetime.fromisoformat(payload["created_at"]),
            metadata=dict(payload.get("metadata", {})),
        )


def create_object_store_from_env() -> LocalObjectStore:
    root = os.getenv("PLAYBOOKOS_OBJECT_STORE_PATH") or "data/object_store"
    return LocalObjectStore(root)


def attach_source_object_to_playbook(
    playbook: Playbook,
    *,
    source_text: str,
    source_kind: str,
    source_uri: str | None = None,
    object_store: LocalObjectStore | None = None,
) -> StoredObject:
    store = object_store or create_object_store_from_env()
    suffix_map = {
        "markdown": ".md",
        "text": ".txt",
        "json": ".json",
        "csv": ".csv",
    }
    mime_map = {
        "markdown": "text/markdown; charset=utf-8",
        "text": "text/plain; charset=utf-8",
        "json": "application/json",
        "csv": "text/csv; charset=utf-8",
    }
    normalized_kind = str(source_kind or "text").strip().lower()
    stored = store.put_text(
        kind="sop_source",
        title=playbook.name,
        text=source_text,
        mime_type=mime_map.get(normalized_kind, "text/plain; charset=utf-8"),
        suffix=suffix_map.get(normalized_kind, ".txt"),
        metadata={
            "playbook_id": playbook.id,
            "playbook_name": playbook.name,
            "source_kind": normalized_kind,
            "source_uri": source_uri or playbook.source_uri,
        },
    )
    playbook.compiled_spec = {
        **playbook.compiled_spec,
        "source_object_id": stored.id,
        "source_object_uri": stored.uri,
        "source_object_checksum": stored.checksum,
        "source_object_mime_type": stored.mime_type,
    }
    playbook.updated_at = utc_now()
    return stored
