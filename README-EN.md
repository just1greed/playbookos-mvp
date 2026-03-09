# PlaybookOS

- 中文版本：`README.md`
- PlaybookOS is a control plane for AI work. It turns `Goal -> SOP -> Skill / MCP -> Task -> Run -> Acceptance / Reflection / Knowledge` into a trackable, reviewable, recoverable, and continuously improvable operating loop.

## Overview

- This repository is not “just another chat UI.” It is a work operating system that both humans and external agents can use.
- Its focus is to unify goals, SOPs, capabilities, execution, acceptance, reflection, and knowledge into one control plane.
- The current version is a runnable MVP focused on `Markdown-first`, local execution, traceable objects, and agent integration.

## What It Is

- A control plane that breaks business goals into playbooks, tasks, and runs, while connecting skills, MCP servers, and knowledge updates.
- A system with both a human dashboard and an agent-facing surface; the dashboard serves humans, while APIs and skills serve OpenClaw-like agents.
- A runnable-first project that prioritizes a working end-to-end loop before deeper governance.

## What It Is Not

- It is not a general-purpose LLM framework replacement, nor a full MCP runtime platform.
- It is not yet a multi-format document understanding platform; the current supported ingestion format is `Markdown SOP` only.
- It is not yet a fully managed operations platform; finer-grained agent identity, rollback, patrol loops, and governance are still planned work.

## Current Status

- The repository already includes a runnable API, SQLite persistence, local object storage, execution orchestration, a preview dashboard, Markdown SOP ingestion, and a first agent-facing control plane.
- The most stable flow today is: `submit Markdown SOP -> parse steps and tool domains -> identify Skill / MCP gaps -> generate Playbook / draft Skill / draft MCP -> continue into Task / Run / Reflection / Knowledge`.
- External agents can already use `manifest / context / intake / apply / delegation profile` APIs to discover capabilities, sync context, plan operations, and execute a subset of builder actions within delegation limits.

## Core Flow

- `Goal` defines intent; `Playbook` stores compiled SOPs; `Skill` and `MCPServer` describe capabilities; `Task` and `Run` describe execution; `Acceptance / Reflection / KnowledgeUpdate` handle review, learning, and knowledge write-back.
- The control plane is not primarily about “calling a model,” but about making objects, states, dependencies, approvals, and learning traceable.

## Implemented Today

- Control-plane objects: `Goal`, `Playbook`, `Skill`, `MCPServer`, `KnowledgeBase`, `KnowledgeUpdate`, `Task`, `Session`, `Run`, `Acceptance`, `Artifact`, `Reflection`, `Event`, `StoredObject`, `DelegationProfile`.
- SOP ingestion: `Markdown SOP` parsing, step extraction, tool-domain detection, Skill suggestions, MCP gap detection, prompt-block generation, and draft Skill / draft MCP materialization.
- Execution chain: `Playbook -> Task DAG` planning, dependency progression, run creation, Supervisor / Worker sessions, waiting-human and approval transitions, Reflection and KnowledgeUpdate loops.
- Dashboard: global board, left-side workbench navigation, model settings, global settings, session management, MCP probe, and task/learning summaries.
- Agent integration: `GET /api/agent/manifest`, `GET /api/agent/context`, `POST /api/agent/intake`, `POST /api/agent/apply`, `GET/POST/PUT /api/delegation-profiles*`, plus `skills/playbookos-operator/`.

## Quick Start

### 1) Install

```bash
cd /home/greed/playbookos-mvp
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

- Python `3.11+` is required.

### 2) Run the API

```bash
cd /home/greed/playbookos-mvp
PYTHONPATH=src python3 -m playbookos.api.app
```

- The API listens on `http://127.0.0.1:8000` by default.

### 3) Run the Preview Dashboard

```bash
cd /home/greed/playbookos-mvp
PYTHONPATH=src python3 -m playbookos.ui.preview_server --demo --host 0.0.0.0 --port 8081
```

- The preview dashboard is available at `http://127.0.0.1:8081`; `--demo` serves built-in demo data.

## Quick Integration for OpenClaw-like Agents

### Integration Model

- PlaybookOS does not expect external agents to read the web UI and click buttons. It exposes an agent-friendly API surface and a companion skill so an agent can understand system objects, operation order, and delegation boundaries.

### Shortest Path

1. Clone the repository and make sure the external agent can read `skills/playbookos-operator/SKILL.md`.
2. Call `GET /api/agent/manifest` to fetch PlaybookOS objects, interfaces, and the recommended operation sequence.
3. Call `GET /api/agent/context` to sync blocked goals, draft skills, MCP health, waiting approvals, and other live state.
4. If the human provides a conversation request or a Markdown SOP, call `POST /api/agent/intake` first for a dry-run plan.
5. If a delegation profile is enabled, call `POST /api/agent/apply` to execute builder operations inside the authorized boundary.

### Recommended Sequence

```text
manifest -> context -> intake -> delegation profile lookup/create -> apply
```

### Minimal Example

```bash
curl -s http://127.0.0.1:8000/api/agent/manifest
curl -s http://127.0.0.1:8000/api/agent/context
```

- When a human uploads a Markdown SOP, the agent should first send it to `/api/agent/intake` so the system can produce a structured operation plan, Skill suggestions, MCP gaps, and reusable candidates before any apply step.

### 5-Minute Runnable Example

- The simplest and most stable way is to use the built-in script to run the full flow end to end.

```bash
cd /home/greed/playbookos-mvp
bash scripts/openclaw_demo.sh
```

- The script automatically runs `manifest -> context -> intake -> delegation profile -> apply` and dynamically extracts recommended `operation_ids` from the intake result.
- On success, it prints `created_resources`, which will usually include at least `playbook`, `skill`, and `mcp_server`.

### Script Parameters

```bash
PLAYBOOKOS_API_BASE=http://127.0.0.1:8000 PLAYBOOKOS_AGENT_ID=openclaw-main bash scripts/openclaw_demo.sh
```

- The default API base is `http://127.0.0.1:8000`; you can override it with `PLAYBOOKOS_API_BASE` and `PLAYBOOKOS_AGENT_ID`.
- If you need to orchestrate the requests yourself, inspect `scripts/openclaw_demo.sh`; it already contains the full request order and the logic for dynamic `operation_ids` extraction.

### Relevant Files

- `skills/playbookos-operator/SKILL.md`
- `docs/agent-operator.md`
- `docs/managed-agent-demo.md`
- `scripts/openclaw_demo.sh`

## Repo Map

- `src/playbookos/api/app.py`: single source of truth for the FastAPI control plane.
- `src/playbookos/ui/preview_server.py`: preview dashboard without FastAPI dependency.
- `src/playbookos/ingestion/`: Markdown SOP ingestion and Skill / MCP guidance.
- `src/playbookos/planner/`: Playbook-to-task planning.
- `src/playbookos/orchestrator/`: orchestration and Temporal-ready specs.
- `src/playbookos/supervisor/`: sessions, events, and approvals.
- `src/playbookos/reflection/`: reflection and knowledge write-back.
- `docs/mvp-plan.md`: MVP plan and remaining gaps.
- `docs/ui-redesign.md`: dashboard information architecture.
- `docs/articles/how-we-built-playbookos.md`: publish-ready build story.
- `docs/records/progress.md`: ongoing progress log.
- `docs/records/iteration-memory.md`: iteration conclusions and TODOs.

## Key APIs

- `GET /api/board`: board snapshot.
- `GET /api/goals`, `POST /api/goals`: goal management.
- `GET /api/playbooks`, `POST /api/playbooks`: playbook management.
- `POST /api/playbooks/ingest`: Markdown SOP ingestion.
- `POST /api/playbooks/{playbook_id}/skill-drafts`: materialize draft skills from SOP guidance.
- `POST /api/playbooks/{playbook_id}/mcp-drafts`: materialize draft MCP servers from SOP guidance.
- `POST /api/mcp-servers/{mcp_server_id}/probe`: MCP health probe.
- `GET /api/runtime-settings`, `PUT /api/runtime-settings`, `POST /api/runtime-settings/test`: model runtime settings and connectivity probe.
- `GET /api/agent/manifest`, `GET /api/agent/context`, `POST /api/agent/intake`, `POST /api/agent/apply`: external-agent control plane.

- For the complete API surface, use `src/playbookos/api/app.py` as the source of truth.

## Current Limitations

- SOP ingestion officially supports `Markdown` only; PDF, Docx, and image pipelines are not yet implemented.
- MCP support currently includes registration and health probing, but not a full runtime, credential, tool-execution, or governance stack.
- Managed agent operation is a first version: it supports discovery, planning, and delegated apply for a subset of builder actions, but still lacks finer identity, rollback, patrol, and governance flows.
- The dashboard already has a global board and workbench information architecture, while some workbenches are still being refined.

## Validation

```bash
cd /home/greed/playbookos-mvp
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'
bash -n scripts/openclaw_demo.sh
```

## Recommended Next Steps

- If you are a human operator, start with the preview dashboard and run one real Markdown SOP through ingestion.
- If you maintain an OpenClaw-like external agent, start by loading the `playbookos-operator` skill and run the `manifest -> context -> intake -> apply` loop end to end.


## Next Work Goals and Improvement Directions

### P0: Stabilize the current core loop

- Keep strengthening the `Markdown SOP -> tooling guidance -> draft Skill / draft MCP -> Task / Run / Reflection` loop, especially the parts that are easy to misread, break, or create duplicate objects.
- Continue hardening the `manifest / context / intake / apply` managed-agent path into a stable public interface so external agents do not need to guess behavior.
- Keep documentation, UI copy, API behavior, and actual implementation aligned, and avoid presenting backlog items as completed features.

### P1: Turn managed-agent support into a fuller execution surface

- Add finer-grained `agent identity`, delegation policy, and audit fields to distinguish human, operator-agent, and delegate-agent roles.
- Evolve `agent apply` from the current first builder version toward a more complete plan executor with better failure attribution, execution summaries, and rollback boundaries.
- Keep improving the `playbookos-operator` skill and runnable examples so OpenClaw-like agents can operate the system with less integration friction.

### P2: Move MCP from “registered” to “operable”

- Build on the current `probe` support with runtime, credential, tool execution, and stronger health governance.
- Map SOP tooling detection more reliably into MCP reuse, gap guidance, and onboarding actions instead of stopping at advisory copy.
- Prepare clearer object relationships and action surfaces for future skill binding, capability publishing, and runtime credential governance.

### P3: Complete the error, self-iteration, and issue loop

- Fully capture system errors, tool errors, and process errors, and split them into two routes: self-iteration optimization vs. system issue submission.
- Add a lightweight issue shortcut so system-level failures can be turned into trackable improvement tasks more easily.
- Make Reflection, KnowledgeUpdate, error logs, and capability revisions participate in one clearer closed loop.

### P4: Finish the console as a long-term operations surface

- Continue filling in workbench detail pages, cross-page linking, URL state, shareable filters, and object-detail navigation.
- Let the settings area take on more environment-governance tasks such as profile lifecycle, restore-last-good configuration, import/export, and sensitive-data handling.
- Keep improving the global board so it not only reports state, but also produces more trustworthy next-action recommendations.

### Deferred Items

- Multi-format SOP and multi-attachment parsing still matter, but they remain lower priority than stabilizing the current `Markdown-first` loop.
- Full Temporal runtime integration, a full MCP platform layer, and deeper governance features stay on the roadmap, but they should not displace the current runnable-first priorities.
