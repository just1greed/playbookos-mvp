---
name: playbookos-operator
description: Operate PlaybookOS as an external agent. Use when an agent needs to discover PlaybookOS capabilities, turn human conversations into Goal/SOP/Skill/MCP/Task operations, or manage the system in delegated operator mode.
---

# PlaybookOS Operator

Use this skill when PlaybookOS is the control plane and the agent is the operator.

## Bootstrap

1. Call `GET /api/agent/manifest` once per session.
2. Call `GET /api/agent/context` before proposing operational actions.
3. If the human request is ambiguous or conversational, call `POST /api/agent/intake` first.
4. Only after intake, execute explicit control-plane APIs such as `/api/goals`, `/api/playbooks/ingest`, `/api/skills`, `/api/tasks`.

## Modes

- `discover`: Understand object types, workflows, and guardrails.
- `builder`: Create or update `Goal`, `Playbook`, `Skill`, `MCP`, `Knowledge`, and `Task` objects.
- `operator`: Plan, dispatch, approve, reject, reflect, and publish.
- `steward`: Monitor board health, waiting approvals, MCP health, and learning-loop backlog.

## Conversation Pattern

- If the human provides a Markdown SOP, send it to `/api/agent/intake` with `markdown_sop` first.
- If intake returns `recommended_operations`, present or execute them in order.
- Prefer `playbooks/ingest` over raw `playbooks/import` when the source is Markdown.
- Prefer reusing existing `Skill` and `MCP` candidates before creating duplicates.

## Governance

- Treat `/api/agent/intake` as planning only; it must not be assumed to mutate state.
- Ask for confirmation before approving runs, publishing reflections, activating skills, or performing actions that may cause external side effects.
- Use `/api/agent/context` to prioritize `waiting_human`, blocked goals, draft skills, and unhealthy MCP servers.

## Deterministic Helpers

- Use `scripts/pbos_api.py` for simple manifest/context/intake calls when a stable helper is preferable.

## References

- For object boundaries and node relationships, read `references/object-model.md`.
- For common operating sequences, read `references/workflows.md`.
