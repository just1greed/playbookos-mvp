# PlaybookOS MVP

PlaybookOS 是一个面向 AI 工作流的“工作操作系统（AI Work Operating System）”。

它不是单纯的聊天式 Agent 框架，而是把 `Goal -> SOP -> Skill / MCP -> Task -> Run -> Acceptance / Reflection / Knowledge` 做成可追踪、可审批、可恢复、可迭代的控制面系统。

## 当前真实状态

当前仓库已经实现一条可运行的本地主链：

- 控制面 API：Goal / Playbook / Skill / MCP / Knowledge / Task / Run / Session / Acceptance / Reflection / Event / Object
- 本地持久化：SQLite + 本地对象存储
- 执行闭环：Planner、Orchestrator、Supervisor、Executor、Reflection
- 前端控制台：全局看板 + 左侧导航工作台 + 设置页
- Markdown SOP ingestion：从 SOP 中提取步骤、识别工具域、生成 Skill 建议、生成 MCP 缺口引导
- 设置治理：模型运行时设置、provider preset、连接测试、命名环境、全局设置、会话管理
- Agent 接入面：`/api/agent/manifest`、`/api/agent/context`、`/api/agent/intake` 与 `playbookos-operator` skill

当前重点是 **Markdown-first**：

- `playbooks/ingest` 现在只支持 `Markdown SOP`
- 系统会优先帮你回答：这份 SOP 需要哪些工具、哪些 MCP 已存在、还缺哪些 MCP、建议上传哪些 Skill
- PDF / Docx / 图片 / 多附件解析还没有做成正式能力

## 当前还没完成

以下仍然是后续计划，而不是当前已完成能力：

- 真正的 Temporal workflow 运行时接入
- 完整的 MCP runtime / credential / tool execution（当前仅完成 health probe 第一版）
- 完整的 delegation profile / agent identity / 托管运营闭环
- 多格式 SOP 与多附件解析
- 更细粒度的 SOP diff / patch review / publish gating
- Skill / MCP 的导入导出、完整治理与审计流
- Artifact blob 的外部对象存储治理

## 仓库结构

- `docs/prd.md`：产品定义与范围
- `docs/architecture.md`：系统架构与模块边界
- `docs/data-model.md`：核心对象与表结构草案
- `docs/mvp-plan.md`：MVP 模块、接口与里程碑
- `docs/ui-redesign.md`：前端重构方案与页面设计
- `docs/agent-operator.md`：外部 agent / OpenClaw 接入方案与 skill 设计
- `docs/records/progress.md`：持续进展记录
- `docs/records/iteration-memory.md`：阶段性结论与缺口排序
- `data/sql/postgres_schema.sql`：PostgreSQL schema 草案
- `data/sql/sqlite_schema.sql`：SQLite schema
- `src/playbookos/api/`：FastAPI 控制面
- `src/playbookos/ui/`：Dashboard HTML 与 Preview Server
- `src/playbookos/persistence/`：SQLite store 与装配
- `src/playbookos/object_store/`：本地对象存储
- `src/playbookos/ingestion/`：Markdown SOP 解析、Skill/MCP 引导
- `src/playbookos/planner/`：Playbook -> Task DAG
- `src/playbookos/orchestrator/`：任务推进与 Temporal-ready 规格输出
- `src/playbookos/supervisor/`：Supervisor / Worker Session、Acceptance、Event
- `src/playbookos/executor/`：执行适配层与 autopilot
- `src/playbookos/reflection/`：反思、知识回写与发布链
- `src/playbookos/runtime_settings.py`：模型与全局运行时设置
- `tests/`：单元测试
- `skills/`：给外部 agent 使用的 skill 包（当前含 `playbookos-operator`）

## 已实现能力

### 1. 控制面对象

当前已落地的核心对象包括：

- Goal
- Playbook
- Skill
- MCPServer
- KnowledgeBase
- KnowledgeUpdate
- Task
- Session
- Run
- Acceptance
- Artifact
- Reflection
- Event
- StoredObject

### 2. SOP ingestion（Markdown）

当前 ingest 主链支持：

- 上传 / 粘贴 Markdown SOP
- 启发式提取步骤并生成 `compiled_spec.steps`
- 识别 GitHub / Slack / Notion / Jira / Email / Sheets / Calendar 等工具域
- 生成 Skill 建议
- 生成 MCP 缺口与可复用候选
- 输出工具发现、Skill 上传、MCP 接入三类 prompt blocks
- 一键物化 draft Skill
- 一键物化 draft MCP
- 原始 SOP 持久化到本地对象存储，并通过 `/api/objects/*` 回看原文

### 3. 执行主链

当前执行链支持：

- `Playbook -> Task DAG` 规划
- 任务依赖推进与批次派发
- Supervisor / Worker Session 自动建立
- Run 执行与 Artifact 元数据生成
- waiting_human / approve / reject / complete 状态联动
- Run 反思、KnowledgeUpdate 提案、Reflection 评测 / 批准 / 发布

### 4. Dashboard / 设置页

当前内置控制台已经不是单页堆叠，而是：

- 默认首页：全局看板
- 左侧导航：目标、SOP、Skill、MCP、知识库、任务、会话、自动迭代、审批流、提示词
- 设置页：模型设置、全局设置、会话管理

MCP 工作台当前还支持：

- 对已登记 MCP 发起 `health probe`
- 展示最近一次探测状态、时间与消息
- 在 UI 中把“已登记但未探测”和“探测失败”的状态区分开

设置页当前支持：

- 运行时模型设置修改
- provider preset 应用
- 模型连通性测试
- 命名模型环境保存 / 激活
- 最近成功 probe 展示
- 全局默认语言 / 路由 / 筛选 / 自动刷新 / 环境标签
- 会话按 Goal / Run 过滤和基础更新

## API（以代码为准）

`src/playbookos/api/app.py` 是当前 API 的单一事实来源。下面是当前实际已实现的主要接口分组。

### 首页 / 系统

- `GET /`
- `GET /healthz`
- `GET /api/board`
- `GET /api/meta/enums`
- `GET /api/errors`
- `GET /api/agent/manifest`
- `GET /api/agent/context`
- `POST /api/agent/intake`

### 运行时设置

- `GET /api/runtime-settings`
- `PUT /api/runtime-settings`
- `POST /api/runtime-settings/test`
- `POST /api/runtime-settings/profiles`
- `POST /api/runtime-settings/profiles/activate`

### Goals

- `POST /api/goals`
- `GET /api/goals`
- `GET /api/goals/{goal_id}`
- `PUT /api/goals/{goal_id}`
- `POST /api/goals/{goal_id}/plan`
- `POST /api/goals/{goal_id}/dispatch`
- `POST /api/goals/{goal_id}/autopilot`
- `GET /api/goals/{goal_id}/learning`
- `POST /api/goals/{goal_id}/start`
- `POST /api/goals/{goal_id}/complete-review`

### Playbooks / ingestion

- `POST /api/playbooks/import`
- `POST /api/playbooks/ingest`
- `GET /api/playbooks`
- `GET /api/playbooks/{playbook_id}`
- `PUT /api/playbooks/{playbook_id}`
- `POST /api/playbooks/{playbook_id}/compile`
- `POST /api/playbooks/{playbook_id}/skill-drafts`
- `POST /api/playbooks/{playbook_id}/mcp-drafts`

### Skills

- `POST /api/skills`
- `GET /api/skills`
- `GET /api/skills/{skill_id}`
- `PUT /api/skills/{skill_id}`
- `GET /api/skills/{skill_id}/authoring-pack`
- `POST /api/skills/{skill_id}/apply-authoring-pack`
- `POST /api/skills/{skill_id}/create-version`
- `POST /api/skills/{skill_id}/activate`
- `POST /api/skills/{skill_id}/deprecate`
- `POST /api/skills/{skill_id}/rollback`

### MCP / Knowledge / Session

- `POST /api/mcp-servers`
- `GET /api/mcp-servers`
- `GET /api/mcp-servers/{mcp_server_id}`
- `PUT /api/mcp-servers/{mcp_server_id}`
- `POST /api/mcp-servers/{mcp_server_id}/probe`
- `POST /api/knowledge-bases`
- `GET /api/knowledge-bases`
- `GET /api/knowledge-bases/{knowledge_id}`
- `PUT /api/knowledge-bases/{knowledge_id}`
- `GET /api/knowledge-updates`
- `GET /api/knowledge-updates/{knowledge_update_id}`
- `POST /api/knowledge-updates/{knowledge_update_id}/apply`
- `POST /api/knowledge-updates/{knowledge_update_id}/reject`
- `GET /api/sessions`
- `GET /api/sessions/{session_id}`
- `PUT /api/sessions/{session_id}`

### Tasks / Runs / Artifacts / Objects / Reflections

- `POST /api/tasks`
- `GET /api/tasks`
- `GET /api/tasks/{task_id}`
- `PUT /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/accept`
- `POST /api/tasks/{task_id}/complete`
- `POST /api/runs`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `POST /api/runs/{run_id}/execute`
- `POST /api/runs/{run_id}/reflect`
- `POST /api/runs/{run_id}/approve`
- `POST /api/runs/{run_id}/reject`
- `POST /api/artifacts`
- `GET /api/artifacts`
- `GET /api/artifacts/{artifact_id}`
- `GET /api/objects`
- `GET /api/objects/{object_id}`
- `GET /api/objects/{object_id}/content`
- `POST /api/reflections`
- `GET /api/reflections`
- `POST /api/reflections/{reflection_id}/evaluate`
- `POST /api/reflections/{reflection_id}/approve`
- `POST /api/reflections/{reflection_id}/reject`
- `POST /api/reflections/{reflection_id}/publish`
- `GET /api/acceptances`
- `GET /api/acceptances/{acceptance_id}`
- `GET /api/events`

## 运行方式

### 1. API 服务

```bash
pip install -e .
playbookos-api
```

或者：

```bash
PYTHONPATH=src uvicorn playbookos.api.app:app --host 0.0.0.0 --port 8000
```

打开：`http://127.0.0.1:8000/`

### 2. Preview Demo

```bash
PYTHONPATH=src python3 -m playbookos.ui.preview_server --demo --host 0.0.0.0 --port 8081
```

打开：`http://127.0.0.1:8081/`

## 存储与环境变量

默认：

- SQLite：`data/playbookos.db`
- 错误日志：`data/error_records.jsonl`
- 对象存储：`data/object_store/`
- 运行时设置：`data/runtime_settings.json`

常用环境变量：

- `PLAYBOOKOS_DB_PATH`
- `DATABASE_URL`
- `PLAYBOOKOS_ERROR_LOG_PATH`
- `PLAYBOOKOS_OBJECT_STORE_PATH`
- `PLAYBOOKOS_RUNTIME_SETTINGS_PATH`
- `PLAYBOOKOS_OPENAI_API_KEY` / `OPENAI_API_KEY`
- `PLAYBOOKOS_OPENAI_BASE_URL` / `OPENAI_BASE_URL`
- `PLAYBOOKOS_OPENAI_MODEL` / `OPENAI_MODEL`
- `PLAYBOOKOS_OPENAI_API_FORMAT`
- `PLAYBOOKOS_OPENAI_TIMEOUT`
- `PLAYBOOKOS_OPENAI_MAX_OUTPUT_TOKENS`
- `PLAYBOOKOS_OPENAI_TEMPERATURE`

## 验证

常用本地验证命令：

```bash
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'
```

如果要校验 Dashboard 脚本，可从 `build_dashboard_html()` 提取 `<script>` 后执行 `node --check`。
