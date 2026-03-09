import unittest

from playbookos.api.store import InMemoryStore
from playbookos.domain.models import MCPServer, MCPServerStatus
from playbookos.mcp_probe import MCPProbeResult, probe_mcp_server_in_store


class FakeMCPProbeTransport:
    def __init__(self, result: MCPProbeResult) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    def probe(self, endpoint: str, *, transport: str, timeout_seconds: float) -> MCPProbeResult:
        self.calls.append({"endpoint": endpoint, "transport": transport, "timeout_seconds": timeout_seconds})
        return self.result


class MCPProbeTestCase(unittest.TestCase):
    def test_probe_updates_mcp_server_health_and_status(self) -> None:
        store = InMemoryStore()
        server = store.mcp_servers.save(
            MCPServer(name="github", transport="streamable_http", endpoint="https://example.com/mcp/github", status=MCPServerStatus.INACTIVE)
        )
        transport = FakeMCPProbeTransport(
            MCPProbeResult(
                ok=True,
                status="ok",
                message="Probe succeeded.",
                endpoint=server.endpoint,
                transport=server.transport,
                tested_at="2026-03-09T00:00:00+00:00",
                timeout_seconds=5.0,
                http_status=200,
            )
        )

        updated, probe = probe_mcp_server_in_store(store, server.id, timeout_seconds=5.0, transport=transport)

        self.assertEqual(updated.status, MCPServerStatus.ACTIVE)
        self.assertTrue(probe["ok"])
        self.assertEqual(updated.auth_config["health"]["status"], "ok")
        self.assertEqual(transport.calls[0]["endpoint"], server.endpoint)
        self.assertTrue(any(event.event_type == "mcp_server.probed" for event in store.events.list()))

    def test_probe_failure_marks_server_error(self) -> None:
        store = InMemoryStore()
        server = store.mcp_servers.save(
            MCPServer(name="slack", transport="streamable_http", endpoint="https://example.com/mcp/slack", status=MCPServerStatus.INACTIVE)
        )
        transport = FakeMCPProbeTransport(
            MCPProbeResult(
                ok=False,
                status="network_error",
                message="Probe failed: timeout",
                endpoint=server.endpoint,
                transport=server.transport,
                tested_at="2026-03-09T00:00:00+00:00",
                timeout_seconds=5.0,
                http_status=None,
            )
        )

        updated, probe = probe_mcp_server_in_store(store, server.id, timeout_seconds=5.0, transport=transport)

        self.assertEqual(updated.status, MCPServerStatus.ERROR)
        self.assertFalse(probe["ok"])
        self.assertEqual(updated.auth_config["health"]["status"], "network_error")


if __name__ == "__main__":
    unittest.main()
