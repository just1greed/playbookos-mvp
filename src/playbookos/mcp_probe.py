from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol
from urllib import error, request

from playbookos.api.store import StoreProtocol
from playbookos.domain.models import MCPServer, MCPServerStatus, utc_now
from playbookos.supervisor import append_event


class MCPProbeError(ValueError):
    pass


@dataclass(slots=True)
class MCPProbeResult:
    ok: bool
    status: str
    message: str
    endpoint: str
    transport: str
    tested_at: str
    timeout_seconds: float
    http_status: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "message": self.message,
            "endpoint": self.endpoint,
            "transport": self.transport,
            "tested_at": self.tested_at,
            "timeout_seconds": self.timeout_seconds,
            "http_status": self.http_status,
        }


class MCPProbeTransport(Protocol):
    def probe(self, endpoint: str, *, transport: str, timeout_seconds: float) -> MCPProbeResult: ...


class UrllibMCPProbeTransport:
    def probe(self, endpoint: str, *, transport: str, timeout_seconds: float) -> MCPProbeResult:
        tested_at = utc_now().isoformat()
        normalized_transport = str(transport or "").strip() or "streamable_http"
        if normalized_transport not in {"streamable_http", "http", "https", "sse"}:
            raise MCPProbeError(f"Unsupported MCP transport for probe: {normalized_transport}")
        target = str(endpoint or "").strip()
        if not target:
            raise MCPProbeError("MCP endpoint is required")
        req = request.Request(
            target,
            method="GET",
            headers={
                "User-Agent": "PlaybookOS-MCPProbe/0.1",
                "Accept": "application/json, text/plain, */*",
            },
        )
        try:
            with request.urlopen(req, timeout=max(1.0, float(timeout_seconds))) as response:
                status_code = int(getattr(response, "status", 200) or 200)
            ok = 200 <= status_code < 400
            return MCPProbeResult(
                ok=ok,
                status="ok" if ok else "http_error",
                message="Probe succeeded." if ok else f"Probe returned HTTP {status_code}.",
                endpoint=target,
                transport=normalized_transport,
                tested_at=tested_at,
                timeout_seconds=float(timeout_seconds),
                http_status=status_code,
            )
        except error.HTTPError as exc:
            status_code = int(getattr(exc, "code", 0) or 0)
            return MCPProbeResult(
                ok=False,
                status="http_error",
                message=f"Probe returned HTTP {status_code}.",
                endpoint=target,
                transport=normalized_transport,
                tested_at=tested_at,
                timeout_seconds=float(timeout_seconds),
                http_status=status_code,
            )
        except error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            return MCPProbeResult(
                ok=False,
                status="network_error",
                message=f"Probe failed: {reason}",
                endpoint=target,
                transport=normalized_transport,
                tested_at=tested_at,
                timeout_seconds=float(timeout_seconds),
            )


def probe_mcp_server_in_store(
    store: StoreProtocol,
    mcp_server_id: str,
    *,
    timeout_seconds: float = 5.0,
    transport: MCPProbeTransport | None = None,
) -> tuple[MCPServer, dict[str, Any]]:
    item = store.mcp_servers.get(mcp_server_id)
    prober = transport or UrllibMCPProbeTransport()
    result = prober.probe(item.endpoint, transport=item.transport, timeout_seconds=float(timeout_seconds))
    auth_config = dict(item.auth_config or {})
    auth_config["health"] = result.to_dict()
    item.auth_config = auth_config
    item.status = MCPServerStatus.ACTIVE if result.ok else MCPServerStatus.ERROR
    item.updated_at = utc_now()
    store.mcp_servers.save(item)
    append_event(
        store,
        entity_type="mcp_server",
        entity_id=item.id,
        event_type="mcp_server.probed",
        payload=result.to_dict(),
        source="human",
    )
    return item, result.to_dict()
