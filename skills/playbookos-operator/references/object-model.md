# PlaybookOS Object Model

## Core graph

- `Goal`: top-level objective and success criteria.
- `Playbook`: compiled SOP, currently Markdown-first.
- `Skill`: reusable capability bound to SOP steps or tasks.
- `MCPServer`: external tool endpoint used by Skills and SOP steps.
- `KnowledgeBase`: reusable knowledge context.
- `Task`: executable unit with dependencies.
- `Run`: execution attempt for one task.
- `Acceptance`: HITL acceptance or rejection for a task/run.
- `Reflection`: post-run proposal for improvements.
- `KnowledgeUpdate`: learning item derived from reflection.

## Preferred relationships

- `Goal -> Playbook -> Task -> Run`
- `Playbook -> Skill drafts / MCP drafts`
- `Task -> assigned_skill_id`
- `Run -> Reflection -> KnowledgeUpdate`

## Important statuses

- `Goal`: watch for `blocked`.
- `Run`: watch for `waiting_human` and `failed`.
- `Skill`: watch for `draft` before activation.
- `MCPServer`: watch for `inactive` and `error`, then probe health.
