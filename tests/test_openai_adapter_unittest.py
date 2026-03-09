import os
import unittest
from unittest.mock import patch

from playbookos.domain.models import RunStatus
from playbookos.executor.service import ExecutionContext, OpenAIAgentsSDKAdapter, OpenAIExecutionConfig


class FakeTransport:
    def __init__(self, response_payload: dict):
        self.response_payload = response_payload
        self.calls: list[dict] = []

    def post_json(self, url: str, headers: dict[str, str], payload: dict[str, object], timeout_seconds: float) -> dict:
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout_seconds": timeout_seconds,
            }
        )
        return self.response_payload


class OpenAIAdapterTestCase(unittest.TestCase):
    def make_context(self) -> ExecutionContext:
        return ExecutionContext(
            goal_id="goal-1",
            goal_title="Ship launch",
            objective="Complete launch execution",
            task_id="task-1",
            task_name="Publish release notes",
            task_description="Draft and publish notes",
            playbook_id="playbook-1",
            playbook_name="Launch SOP",
            playbook_version="0.1.0",
            compiled_steps=["Collect changes", "Draft notes", "Publish"],
            mcp_servers=["github", "slack"],
            knowledge_items=[{"id": "kb-1", "name": "Previous launch", "content": "Checklist"}],
            skill_id="skill-1",
            approval_required=False,
        )

    def test_adapter_prepares_payload_without_api_key(self) -> None:
        config = OpenAIExecutionConfig(
            api_key=None,
            base_url="https://api.example.com/v1",
            model="gpt-4.1",
            api_format="responses",
        )
        adapter = OpenAIAgentsSDKAdapter(config=config, transport=FakeTransport({}))

        result = adapter.execute(self.make_context())

        self.assertEqual(result.status, RunStatus.SUCCEEDED)
        self.assertEqual(result.metrics["openai_mode"], "prepared_only")
        self.assertEqual(result.metrics["openai_request_format"], "responses")
        self.assertEqual(result.tool_calls[0]["request_url"], "https://api.example.com/v1/responses")
        self.assertEqual(result.tool_calls[0]["payload"]["model"], "gpt-4.1")
        self.assertIn("input", result.tool_calls[0]["payload"])

    def test_adapter_uses_chat_completions_when_configured(self) -> None:
        transport = FakeTransport(
            {
                "id": "chatcmpl-123",
                "model": "gpt-4.1-mini",
                "choices": [
                    {
                        "message": {
                            "content": "Release notes drafted and ready for review."
                        }
                    }
                ],
                "usage": {"prompt_tokens": 11, "completion_tokens": 7},
            }
        )
        config = OpenAIExecutionConfig(
            api_key="test-key",
            base_url="https://api.example.com/v1",
            model="gpt-4.1-mini",
            api_format="chat.completions",
            timeout_seconds=12.0,
        )
        adapter = OpenAIAgentsSDKAdapter(config=config, transport=transport)

        result = adapter.execute(self.make_context())

        self.assertEqual(result.status, RunStatus.SUCCEEDED)
        self.assertEqual(result.metrics["openai_mode"], "online")
        self.assertEqual(result.metrics["openai_response_id"], "chatcmpl-123")
        self.assertEqual(transport.calls[0]["url"], "https://api.example.com/v1/chat/completions")
        self.assertIn("messages", transport.calls[0]["payload"])
        self.assertEqual(transport.calls[0]["payload"]["model"], "gpt-4.1-mini")
        self.assertIn("Release notes drafted", result.output_text)
        self.assertEqual(result.tool_calls[-1]["action"], "response_received")

    def test_config_reads_current_environment_shape(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "env-key",
                "OPENAI_BASE_URL": "https://gateway.example.com/v1",
                "OPENAI_MODEL": "gpt-4.1-nano",
                "PLAYBOOKOS_OPENAI_API_FORMAT": "chat.completions",
                "PLAYBOOKOS_OPENAI_TIMEOUT": "33",
            },
            clear=False,
        ):
            config = OpenAIExecutionConfig.from_env()

        self.assertEqual(config.api_key, "env-key")
        self.assertEqual(config.base_url, "https://gateway.example.com/v1")
        self.assertEqual(config.model, "gpt-4.1-nano")
        self.assertEqual(config.api_format, "chat.completions")
        self.assertEqual(config.timeout_seconds, 33.0)


if __name__ == "__main__":
    unittest.main()
