# PlaybookOS Operator Workflows

## Bootstrap a session

1. `GET /api/agent/manifest`
2. `GET /api/agent/context`
3. Read `suggested_next_actions`
4. If the human gave a vague request, use `POST /api/agent/intake`

## Turn a conversation into a Playbook

1. Collect Markdown SOP or derive it from the conversation.
2. `POST /api/agent/intake` with `message`, `markdown_sop`, and optional `goal_id`.
3. `POST /api/playbooks/ingest`
4. If needed, create skill drafts from `/api/playbooks/{playbook_id}/skill-drafts`.
5. If needed, create MCP drafts from `/api/playbooks/{playbook_id}/mcp-drafts`.
6. Apply `/api/skills/{skill_id}/apply-authoring-pack` to draft skills.

## Manage the system on behalf of a human

1. Poll `/api/agent/context` and `/api/board`.
2. Surface `waiting_human` runs and blocked goals first.
3. Probe unhealthy MCP servers before trusting them.
4. Process reflections and knowledge updates after execution.
5. Keep humans in the loop for approvals, publishing, activation, and rollback.
