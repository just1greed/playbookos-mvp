# PlaybookOS

- 中文：PlaybookOS 是一个面向 AI 工作流的控制面系统（AI Work Operating System）。它把 `Goal -> SOP -> Skill / MCP -> Task -> Run -> Acceptance / Reflection / Knowledge` 做成可追踪、可审批、可恢复、可迭代的一条主链。
- English: PlaybookOS is a control plane for AI work. It turns `Goal -> SOP -> Skill / MCP -> Task -> Run -> Acceptance / Reflection / Knowledge` into a trackable, reviewable, recoverable, and continuously improvable operating loop.

## 项目简介 / Overview

- 中文：这个仓库不是“再做一个聊天机器人 UI”，而是在做一套让人类与外部 agent 都能操作的工作系统。它的重点是把目标、SOP、能力、执行、验收、复盘、知识沉淀统一到同一个控制面里。
- English: This repository is not “just another chat UI.” It is a work operating system that both humans and external agents can use to manage goals, SOPs, capabilities, execution, acceptance, reflection, and knowledge in one control plane.

- 中文：当前版本是一个可运行的 MVP，强调 `Markdown-first`、本地可跑、对象可追踪、agent 可接入。
- English: The current version is a runnable MVP focused on `Markdown-first` SOP ingestion, local execution, traceable objects, and external-agent integration.

## 它是什么 / What It Is

- 中文：一个把业务目标拆成 Playbook、Task、Run，并把 Skill / MCP / 知识沉淀接进来的控制面系统。
- English: A control plane that breaks business goals into playbooks, tasks, and runs, while connecting capabilities such as skills, MCP servers, and knowledge updates.

- 中文：一个支持人类操作台和外部 agent 操作面的系统；Dashboard 给人看，agent-facing API 和 skill 给 OpenClaw 这类 agent 用。
- English: A system with both a human dashboard and an agent-facing surface; the dashboard serves humans, while APIs and skills serve OpenClaw-like agents.

- 中文：一个强调“先把链路跑通，再逐步补治理”的 runnable-first 项目。
- English: A runnable-first project that prioritizes a working end-to-end loop before adding deeper governance.

## 它不是什么 / What It Is Not

- 中文：它不是一个通用大模型框架替代品，也不是完整的 MCP runtime 平台。
- English: It is not a general-purpose LLM framework replacement, nor a full MCP runtime platform.

- 中文：它当前还不是多格式文档理解平台；现阶段只正式支持 `Markdown SOP`。
- English: It is not yet a multi-format document understanding platform; the current supported ingestion format is `Markdown SOP` only.

- 中文：它也还不是完整的托管运营系统；更细粒度的 agent identity、回滚、巡检、治理仍在后续计划里。
- English: It is also not yet a fully managed operations system; finer-grained agent identity, rollback, patrol loops, and governance are still planned work.

## 当前真实状态 / Current Status

- 中文：仓库已经实现本地可运行的 API、SQLite 持久化、本地对象存储、任务编排主链、前端预览控制台、Markdown SOP ingestion，以及第一版 agent-facing control plane。
- English: The repository already includes a runnable API, SQLite persistence, local object storage, execution orchestration, a preview dashboard, Markdown SOP ingestion, and a first agent-facing control plane.

- 中文：当前最稳的主链是：`上传或粘贴 Markdown SOP -> 解析步骤与工具域 -> 识别 Skill / MCP 缺口 -> 生成 Playbook / draft Skill / draft MCP -> 进入 Task / Run / Reflection / Knowledge 链路`。
- English: The most stable flow today is: `submit Markdown SOP -> parse steps and tool domains -> identify Skill / MCP gaps -> generate Playbook / draft Skill / draft MCP -> continue into Task / Run / Reflection / Knowledge`.

- 中文：当前对外 agent 已可通过 `manifest / context / intake / apply / delegation profile` 接口发现能力、同步上下文、规划操作并在授权边界内执行一部分 builder 动作。
- English: External agents can already use `manifest / context / intake / apply / delegation profile` APIs to discover capabilities, sync context, plan operations, and execute a subset of builder actions within delegation limits.

## 核心主链 / Core Flow

- 中文：`Goal` 定义目标；`Playbook` 承载 SOP 编译结果；`Skill` 与 `MCPServer` 描述能力；`Task` 与 `Run` 描述执行；`Acceptance / Reflection / KnowledgeUpdate` 负责验收、复盘与知识回写。
- English: `Goal` defines intent; `Playbook` stores compiled SOPs; `Skill` and `MCPServer` describe capabilities; `Task` and `Run` describe execution; `Acceptance / Reflection / KnowledgeUpdate` handle review, learning, and knowledge write-back.

- 中文：控制面的核心不是“直接调用模型”，而是“让对象、状态、依赖、审批、学习都留痕”。
- English: The control plane is not primarily about “calling a model,” but about making objects, states, dependencies, approvals, and learning traceable.

## 当前已实现能力 / Implemented Today

- 中文：控制面对象：`Goal`、`Playbook`、`Skill`、`MCPServer`、`KnowledgeBase`、`KnowledgeUpdate`、`Task`、`Session`、`Run`、`Acceptance`、`Artifact`、`Reflection`、`Event`、`StoredObject`、`DelegationProfile`。
- English: Implemented control-plane objects include `Goal`, `Playbook`, `Skill`, `MCPServer`, `KnowledgeBase`, `KnowledgeUpdate`, `Task`, `Session`, `Run`, `Acceptance`, `Artifact`, `Reflection`, `Event`, `StoredObject`, and `DelegationProfile`.

- 中文：SOP ingestion：支持 `Markdown SOP` 解析、步骤提取、工具域识别、Skill 建议、MCP 缺口识别、prompt blocks 生成，以及 draft Skill / draft MCP 物化。
- English: SOP ingestion supports `Markdown SOP` parsing, step extraction, tool-domain detection, Skill suggestions, MCP gap detection, prompt-block generation, and draft Skill / draft MCP materialization.

- 中文：执行链：支持 `Playbook -> Task DAG` 规划、依赖推进、Run 创建、Supervisor / Worker Session、waiting_human 与审批状态联动、Reflection 与 KnowledgeUpdate 主链。
- English: The execution chain supports `Playbook -> Task DAG` planning, dependency progression, run creation, Supervisor / Worker sessions, waiting-human/approval transitions, and Reflection / KnowledgeUpdate flows.

- 中文：控制台：已具备全局看板、左侧工作台导航、模型设置、全局设置、会话管理、MCP probe、任务/学习摘要等页面骨架与交互。
- English: The dashboard already includes a global board, left-side workbench navigation, model settings, global settings, session management, MCP probing, and task/learning summaries.

- 中文：Agent 接入：已提供 `GET /api/agent/manifest`、`GET /api/agent/context`、`POST /api/agent/intake`、`POST /api/agent/apply`、`GET/POST/PUT /api/delegation-profiles*`，以及 `skills/playbookos-operator/`。
- English: Agent integration already includes `GET /api/agent/manifest`, `GET /api/agent/context`, `POST /api/agent/intake`, `POST /api/agent/apply`, `GET/POST/PUT /api/delegation-profiles*`, plus the `skills/playbookos-operator/` package.

## 快速启动 / Quick Start

### 1) 安装 / Install

```bash
cd /home/greed/playbookos-mvp
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

- 中文：要求 Python `3.11+`。
- English: Python `3.11+` is required.

### 2) 启动 API / Run the API

```bash
cd /home/greed/playbookos-mvp
PYTHONPATH=src python3 -m playbookos.api.app
```

- 中文：默认监听 `http://127.0.0.1:8000`。
- English: The API listens on `http://127.0.0.1:8000` by default.

### 3) 启动预览控制台 / Run the Preview Dashboard

```bash
cd /home/greed/playbookos-mvp
PYTHONPATH=src python3 -m playbookos.ui.preview_server --demo --host 0.0.0.0 --port 8081
```

- 中文：默认演示地址为 `http://127.0.0.1:8081`；加 `--demo` 会使用内置演示数据。
- English: The preview dashboard is available at `http://127.0.0.1:8081`; `--demo` serves built-in demo data.

## 给 OpenClaw / 外部 Agent 的快速接入 / Quick Integration for OpenClaw-like Agents

### 接入原则 / Integration Model

- 中文：PlaybookOS 不是要求外部 agent “看网页点击按钮”，而是提供一套 agent-friendly API 和配套 skill，让 agent 能理解系统对象、操作顺序和授权边界。
- English: PlaybookOS does not expect external agents to “read the web UI and click buttons.” Instead, it exposes agent-friendly APIs and a companion skill so agents can understand objects, operation order, and delegation boundaries.

### 最短接入步骤 / Shortest Path

1. `git clone` 本仓库，并让外部 agent 能读取 `skills/playbookos-operator/SKILL.md`。
2. 调用 `GET /api/agent/manifest`，获取 PlaybookOS 的对象、接口和推荐操作顺序。
3. 调用 `GET /api/agent/context`，同步当前 blocked goals、draft skills、MCP 健康状态、等待审批项等上下文。
4. 如果人类给出的是对话或 Markdown SOP，先调用 `POST /api/agent/intake` 做 dry-run 规划。
5. 如果系统启用了 delegation profile，再调用 `POST /api/agent/apply` 执行授权范围内的 builder 操作。

### 推荐调用顺序 / Recommended Sequence

```text
manifest -> context -> intake -> delegation profile lookup/create -> apply
```

### 最小示例 / Minimal Example

```bash
curl -s http://127.0.0.1:8000/api/agent/manifest
curl -s http://127.0.0.1:8000/api/agent/context
```

- 中文：当人类上传一份 Markdown SOP 时，agent 应优先把原始 SOP 发给 `/api/agent/intake`，让系统先产出结构化操作计划、Skill 建议、MCP 缺口和可复用候选，再决定是否 apply。
- English: When a human uploads a Markdown SOP, the agent should first send it to `/api/agent/intake` so the system can produce a structured operation plan, Skill suggestions, MCP gaps, and reuse candidates before deciding whether to apply changes.

### 相关文件 / Relevant Files

- `skills/playbookos-operator/SKILL.md`
- `docs/agent-operator.md`
- `docs/managed-agent-demo.md`

## 目录与文档 / Repo Map

- `src/playbookos/api/app.py`：FastAPI 控制面单一事实来源 / single source of truth for the API.
- `src/playbookos/ui/preview_server.py`：无 FastAPI 依赖的预览控制台 / preview dashboard server.
- `src/playbookos/ingestion/`：Markdown SOP 解析与 Skill / MCP 引导 / Markdown SOP ingestion and capability guidance.
- `src/playbookos/planner/`：Playbook 到任务图规划 / Playbook-to-task planning.
- `src/playbookos/orchestrator/`：任务推进与 Temporal-ready 规格输出 / orchestration and Temporal-ready specs.
- `src/playbookos/supervisor/`：会话、事件、审批联动 / sessions, events, and approvals.
- `src/playbookos/reflection/`：复盘与知识回写 / reflection and knowledge write-back.
- `docs/mvp-plan.md`：MVP 技术路线与缺口 / MVP plan and remaining gaps.
- `docs/ui-redesign.md`：控制台信息架构 / dashboard redesign plan.
- `docs/records/progress.md`：持续进展记录 / progress log.
- `docs/records/iteration-memory.md`：阶段结论与 TODO / iteration memory and TODOs.

## 关键接口 / Key APIs

- `GET /api/board`：全局看板快照 / board snapshot.
- `GET /api/goals`、`POST /api/goals`：目标管理 / goal management.
- `GET /api/playbooks`、`POST /api/playbooks`：Playbook 管理 / playbook management.
- `POST /api/playbooks/ingest`：Markdown SOP ingestion.
- `POST /api/playbooks/{playbook_id}/skill-drafts`：基于 SOP 建 draft Skill / materialize draft skills from SOP guidance.
- `POST /api/playbooks/{playbook_id}/mcp-drafts`：基于 SOP 建 draft MCP / materialize draft MCP servers from SOP guidance.
- `POST /api/mcp-servers/{mcp_server_id}/probe`：MCP 健康探测 / MCP health probe.
- `GET /api/runtime-settings`、`PUT /api/runtime-settings`、`POST /api/runtime-settings/test`：模型运行时配置与连通性测试 / model runtime settings and probe.
- `GET /api/agent/manifest`、`GET /api/agent/context`、`POST /api/agent/intake`、`POST /api/agent/apply`：外部 agent 控制面 / external-agent control plane.

- 中文：完整接口请以 `src/playbookos/api/app.py` 为准。
- English: For the complete API surface, use `src/playbookos/api/app.py` as the source of truth.

## 当前限制 / Current Limitations

- 中文：SOP ingestion 当前只正式支持 `Markdown`，不支持 PDF、Docx、图片等正式解析链路。
- English: SOP ingestion officially supports `Markdown` only for now; PDF, Docx, and image pipelines are not yet implemented.

- 中文：MCP 当前只有登记与 health probe，尚未完成完整 runtime、credential、tool execution 与治理闭环。
- English: MCP support currently includes registration and health probing, but not a full runtime, credential, tool-execution, or governance stack.

- 中文：agent 托管目前是第一版：可发现、可规划、可按 delegation apply 一部分 builder 动作，但还缺更细粒度 identity、事务回滚、巡检与治理链。
- English: Managed agent operation is a first version: it supports discovery, planning, and delegated apply for a subset of builder actions, but still lacks finer identity, rollback, patrol, and governance flows.

- 中文：Dashboard 已完成全局看板与工作台信息架构，但部分工作台仍在持续细化中。
- English: The dashboard already has a global board and workbench information architecture, while some workbenches are still being refined.

## 验证 / Validation

```bash
cd /home/greed/playbookos-mvp
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'
```

## 下一步建议 / Recommended Next Steps

- 中文：如果你是人类操作者，建议先跑 `Preview Dashboard`，再用一份真实的 Markdown SOP 走一次 ingestion。
- English: If you are a human operator, start with the preview dashboard and run one real Markdown SOP through ingestion.

- 中文：如果你是 OpenClaw 这类外部 agent 的维护者，建议先接入 `playbookos-operator` skill，然后按 `manifest -> context -> intake -> apply` 跑通一条托管链。
- English: If you maintain an OpenClaw-like external agent, start by loading the `playbookos-operator` skill and run the `manifest -> context -> intake -> apply` loop end to end.
