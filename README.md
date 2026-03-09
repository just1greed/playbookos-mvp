# PlaybookOS

- English version: `README-EN.md`
- PlaybookOS 是一个面向 AI 工作流的控制面系统（AI Work Operating System）。它把 `Goal -> SOP -> Skill / MCP -> Task -> Run -> Acceptance / Reflection / Knowledge` 做成可追踪、可审批、可恢复、可迭代的一条主链。

## 项目简介

- 这个仓库不是“再做一个聊天机器人 UI”，而是在做一套让人类与外部 agent 都能操作的工作系统。
- 它的重点是把目标、SOP、能力、执行、验收、复盘、知识沉淀统一到同一个控制面里。
- 当前版本是一个可运行的 MVP，强调 `Markdown-first`、本地可跑、对象可追踪、agent 可接入。

## 它是什么

- 一个把业务目标拆成 Playbook、Task、Run，并把 Skill / MCP / 知识沉淀接进来的控制面系统。
- 一个支持人类操作台和外部 agent 操作面的系统；Dashboard 给人看，agent-facing API 和 skill 给 OpenClaw 这类 agent 用。
- 一个强调“先把链路跑通，再逐步补治理”的 runnable-first 项目。

## 它不是什么

- 它不是一个通用大模型框架替代品，也不是完整的 MCP runtime 平台。
- 它当前还不是多格式文档理解平台；现阶段只正式支持 `Markdown SOP`。
- 它也还不是完整的托管运营系统；更细粒度的 agent identity、回滚、巡检、治理仍在后续计划里。

## 当前真实状态

- 仓库已经实现本地可运行的 API、SQLite 持久化、本地对象存储、任务编排主链、前端预览控制台、Markdown SOP ingestion，以及第一版 agent-facing control plane。
- 当前最稳的主链是：`上传或粘贴 Markdown SOP -> 解析步骤与工具域 -> 识别 Skill / MCP 缺口 -> 生成 Playbook / draft Skill / draft MCP -> 进入 Task / Run / Reflection / Knowledge 链路`。
- 当前对外 agent 已可通过 `manifest / context / intake / apply / delegation profile` 接口发现能力、同步上下文、规划操作并在授权边界内执行一部分 builder 动作。

## 核心主链

- `Goal` 定义目标；`Playbook` 承载 SOP 编译结果；`Skill` 与 `MCPServer` 描述能力；`Task` 与 `Run` 描述执行；`Acceptance / Reflection / KnowledgeUpdate` 负责验收、复盘与知识回写。
- 控制面的核心不是“直接调用模型”，而是“让对象、状态、依赖、审批、学习都留痕”。

## 当前已实现能力

- 控制面对象：`Goal`、`Playbook`、`Skill`、`MCPServer`、`KnowledgeBase`、`KnowledgeUpdate`、`Task`、`Session`、`Run`、`Acceptance`、`Artifact`、`Reflection`、`Event`、`StoredObject`、`DelegationProfile`。
- SOP ingestion：支持 `Markdown SOP` 解析、步骤提取、工具域识别、Skill 建议、MCP 缺口识别、prompt blocks 生成，以及 draft Skill / draft MCP 物化。
- 执行链：支持 `Playbook -> Task DAG` 规划、依赖推进、Run 创建、Supervisor / Worker Session、waiting_human 与审批状态联动、Reflection 与 KnowledgeUpdate 主链。
- 控制台：已具备全局看板、左侧工作台导航、模型设置、全局设置、会话管理、MCP probe、任务/学习摘要等页面骨架与交互。
- Agent 接入：已提供 `GET /api/agent/manifest`、`GET /api/agent/context`、`POST /api/agent/intake`、`POST /api/agent/apply`、`GET/POST/PUT /api/delegation-profiles*`，以及 `skills/playbookos-operator/`。

## 快速启动

### 1) 安装

```bash
cd /home/greed/playbookos-mvp
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

- 要求 Python `3.11+`。

### 2) 启动 API

```bash
cd /home/greed/playbookos-mvp
PYTHONPATH=src python3 -m playbookos.api.app
```

- 默认监听 `http://127.0.0.1:8000`。

### 3) 启动预览控制台

```bash
cd /home/greed/playbookos-mvp
PYTHONPATH=src python3 -m playbookos.ui.preview_server --demo --host 0.0.0.0 --port 8081
```

- 默认演示地址为 `http://127.0.0.1:8081`；加 `--demo` 会使用内置演示数据。

## 给 OpenClaw / 外部 Agent 的快速接入

### 接入原则

- PlaybookOS 不是要求外部 agent “看网页点击按钮”，而是提供一套 agent-friendly API 和配套 skill，让 agent 能理解系统对象、操作顺序和授权边界。

### 最短接入步骤

1. `git clone` 本仓库，并让外部 agent 能读取 `skills/playbookos-operator/SKILL.md`。
2. 调用 `GET /api/agent/manifest`，获取 PlaybookOS 的对象、接口和推荐操作顺序。
3. 调用 `GET /api/agent/context`，同步当前 blocked goals、draft skills、MCP 健康状态、等待审批项等上下文。
4. 如果人类给出的是对话或 Markdown SOP，先调用 `POST /api/agent/intake` 做 dry-run 规划。
5. 如果系统启用了 delegation profile，再调用 `POST /api/agent/apply` 执行授权范围内的 builder 操作。

### 推荐调用顺序

```text
manifest -> context -> intake -> delegation profile lookup/create -> apply
```

### 最小示例

```bash
curl -s http://127.0.0.1:8000/api/agent/manifest
curl -s http://127.0.0.1:8000/api/agent/context
```

- 当人类上传一份 Markdown SOP 时，agent 应优先把原始 SOP 发给 `/api/agent/intake`，让系统先产出结构化操作计划、Skill 建议、MCP 缺口和可复用候选，再决定是否 apply。

### 5 分钟跑通示例

- 最简单且最稳定的方式，是直接使用仓库内置的脚本来跑完整链路。

```bash
cd /home/greed/playbookos-mvp
bash scripts/openclaw_demo.sh
```

- 这个脚本会自动执行 `manifest -> context -> intake -> delegation profile -> apply`，并从 intake 结果中动态提取推荐的 `operation_ids`。
- 成功后，脚本会打印 `created_resources`，其中通常至少包含 `playbook`、`skill`、`mcp_server` 三类对象。

### 脚本参数

```bash
PLAYBOOKOS_API_BASE=http://127.0.0.1:8000 PLAYBOOKOS_AGENT_ID=openclaw-main bash scripts/openclaw_demo.sh
```

- 默认 API 地址为 `http://127.0.0.1:8000`，也可以通过 `PLAYBOOKOS_API_BASE`、`PLAYBOOKOS_AGENT_ID` 覆盖。
- 如果你需要自己编排请求，也可以先看 `scripts/openclaw_demo.sh`，它已经把完整请求顺序和动态 `operation_ids` 提取逻辑写好。

### 相关文件

- `skills/playbookos-operator/SKILL.md`
- `docs/agent-operator.md`
- `docs/managed-agent-demo.md`
- `scripts/openclaw_demo.sh`

## 目录与文档

- `src/playbookos/api/app.py`：FastAPI 控制面单一事实来源。
- `src/playbookos/ui/preview_server.py`：无 FastAPI 依赖的预览控制台。
- `src/playbookos/ingestion/`：Markdown SOP 解析与 Skill / MCP 引导。
- `src/playbookos/planner/`：Playbook 到任务图规划。
- `src/playbookos/orchestrator/`：任务推进与 Temporal-ready 规格输出。
- `src/playbookos/supervisor/`：会话、事件、审批联动。
- `src/playbookos/reflection/`：复盘与知识回写。
- `docs/mvp-plan.md`：MVP 技术路线与缺口。
- `docs/ui-redesign.md`：控制台信息架构。
- `docs/records/progress.md`：持续进展记录。
- `docs/records/iteration-memory.md`：阶段结论与 TODO。

## 关键接口

- `GET /api/board`：全局看板快照。
- `GET /api/goals`、`POST /api/goals`：目标管理。
- `GET /api/playbooks`、`POST /api/playbooks`：Playbook 管理。
- `POST /api/playbooks/ingest`：Markdown SOP ingestion。
- `POST /api/playbooks/{playbook_id}/skill-drafts`：基于 SOP 建 draft Skill。
- `POST /api/playbooks/{playbook_id}/mcp-drafts`：基于 SOP 建 draft MCP。
- `POST /api/mcp-servers/{mcp_server_id}/probe`：MCP 健康探测。
- `GET /api/runtime-settings`、`PUT /api/runtime-settings`、`POST /api/runtime-settings/test`：模型运行时配置与连通性测试。
- `GET /api/agent/manifest`、`GET /api/agent/context`、`POST /api/agent/intake`、`POST /api/agent/apply`：外部 agent 控制面。

- 完整接口请以 `src/playbookos/api/app.py` 为准。

## 当前限制

- SOP ingestion 当前只正式支持 `Markdown`，不支持 PDF、Docx、图片等正式解析链路。
- MCP 当前只有登记与 health probe，尚未完成完整 runtime、credential、tool execution 与治理闭环。
- agent 托管目前是第一版：可发现、可规划、可按 delegation apply 一部分 builder 动作，但还缺更细粒度 identity、事务回滚、巡检与治理链。
- Dashboard 已完成全局看板与工作台信息架构，但部分工作台仍在持续细化中。

## 验证

```bash
cd /home/greed/playbookos-mvp
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'
bash -n scripts/openclaw_demo.sh
```

## 下一步建议

- 如果你是人类操作者，建议先跑 `Preview Dashboard`，再用一份真实的 Markdown SOP 走一次 ingestion。
- 如果你是 OpenClaw 这类外部 agent 的维护者，建议先接入 `playbookos-operator` skill，然后按 `manifest -> context -> intake -> apply` 跑通一条托管链。
