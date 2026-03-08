# PlaybookOS MVP

PlaybookOS 不是单纯的 Agent 框架，而是一个面向 AI 工作流的“工作操作系统（AI Work Operating System）”。

当前仓库先落第一版产品与技术基线，围绕以下三层组合构建：

- 工作台 / 知识层：`Plane`
- 持久化编排层：`Temporal`
- Agent 执行层：`OpenAI Agents SDK`

## 核心定位

PlaybookOS 用来把目标、SOP、技能、工具权限、执行记录和反思沉淀成一套可追踪、可审批、可恢复、可迭代的运行系统。

它面向的不是“多 Agent 聊天”，而是“目标 -> 任务 -> 执行 -> 产物 -> 复盘 -> 晋级”的闭环交付。

## MVP 原则

- 状态外置，不依赖内存会话
- 工具最小权限，不做全局写入放权
- 自我改进只产生提案，不直接改线上能力
- SOP 先编译为 Playbook，再参与执行
- 长任务必须支持恢复、重试、审批与追踪

## 仓库结构

- `docs/prd.md`：产品定义与范围
- `docs/architecture.md`：系统架构与模块边界
- `docs/data-model.md`：核心对象与表结构草案
- `docs/mvp-plan.md`：MVP 接口、模块与里程碑
- `docs/records/progress.md`：持续进展记录
- `data/sql/postgres_schema.sql`：PostgreSQL 表结构草案
- `data/sql/sqlite_schema.sql`：本地持久化开发 schema
- `src/playbookos/domain/`：核心领域模型
- `src/playbookos/api/`：FastAPI 控制面骨架
- `src/playbookos/persistence/`：持久化 store 与环境装配
- `src/playbookos/planner/`：Playbook -> Task DAG 规划器
- `src/playbookos/orchestrator/`：任务调度与 Temporal-ready 编排核心
- `src/playbookos/executor/`：OpenAI Agents SDK 适配层与 autopilot
- `src/playbookos/reflection/`：SOP/Playbook 改进提案与学习汇总
- `tests/`：基础测试

## 当前阶段

当前版本提供：

- 产品与架构基线文档
- 八个核心对象的 Python 领域模型
- FastAPI 控制面 API 骨架
- 基于 SQLite 的本地持久化数据流
- Playbook 驱动的任务规划器
- Orchestrator 调度核心与 Temporal-ready 工作流快照
- OpenAI Agents SDK 风格执行适配层
- Run 级 Artifact 元数据持久化与查询
- 一个优美的内置前端控制台首页（`GET /`）
- SOP 自我迭代提案骨架
- PostgreSQL schema 文件，供后续正式部署接入

## 已实现 API

- `GET /`
- `POST /api/goals`
- `GET /api/goals`
- `GET /api/goals/{goal_id}`
- `POST /api/goals/{goal_id}/plan`
- `POST /api/goals/{goal_id}/dispatch`
- `POST /api/goals/{goal_id}/autopilot`
- `GET /api/goals/{goal_id}/learning`
- `POST /api/goals/{goal_id}/start`
- `POST /api/goals/{goal_id}/complete-review`
- `POST /api/playbooks/import`
- `GET /api/playbooks`
- `GET /api/playbooks/{playbook_id}`
- `POST /api/playbooks/{playbook_id}/compile`
- `POST /api/tasks`
- `GET /api/tasks`
- `GET /api/tasks/{task_id}`
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
- `POST /api/reflections`
- `GET /api/reflections`
- `POST /api/reflections/{reflection_id}/evaluate`
- `POST /api/reflections/{reflection_id}/approve`
- `POST /api/reflections/{reflection_id}/reject`
- `POST /api/reflections/{reflection_id}/publish`
- `GET /api/board`
- `GET /api/meta/enums`
- `GET /healthz`

## Planner 规则

`planner` 会优先读取 `playbook.compiled_spec.steps` 来生成 `Task DAG`：

- 无显式依赖时，默认串行生成依赖链
- `depends_on` 可引用前序步骤名称，或前序步骤索引
- 无 `steps` 时，回退为一个默认执行任务
- 第一个可执行任务标记为 `ready`，其余依赖任务标记为 `inbox`
- 重复对同一个 `Goal` 执行规划时，不会重复创建任务

## Orchestrator 规则

`orchestrator` 负责把 `Task DAG` 推进成可执行运行批次：

- 把依赖已满足的 `inbox` 任务提升到 `ready`
- 为 `ready` 任务创建 `Run`
- 普通任务派发后进入 `running`
- 需要审批的任务派发后进入 `waiting_human`
- `POST /api/tasks/{task_id}/complete` 会完成当前任务，并自动推进下游节点
- 所有任务完成后，`Goal` 自动进入 `review`

当前实现不依赖 Temporal SDK，但已经输出 `TemporalWorkflowSpec`，后续可直接映射到真正的 Temporal workflow/activity 输入。

## Executor 规则

`executor` 负责把 `Run` 变成真正的执行动作：

- `OpenAIAgentsSDKAdapter` 生成与 OpenAI Agents SDK 对齐的执行载荷
- `DeterministicExecutorAdapter` 用于本地测试和无依赖环境
- `POST /api/runs/{run_id}/execute` 会执行单个 `Run`
- 每次执行会自动生成一个 `run_report` Artifact，沉淀输出、trace、tool_calls 和指标摘要
- 成功执行后会把任务推进到完成链路，失败/审批等待则保留为阻塞信号

## 自我迭代能力

你要的“给定一个 SOP 和 MCP，自动完成大量相似任务，并从经验反过来优化 SOP”现在已经有第一版骨架，但还不是最终闭环。

目前已实现：

- `POST /api/goals/{goal_id}/autopilot`：自动规划、调度、执行可自动完成的任务
- `POST /api/runs/{run_id}/reflect`：从单次 Run 生成 SOP patch proposal
- `GET /api/goals/{goal_id}/learning`：聚合一个 Goal 下的失败分类和 SOP 改进提案
- 成功模式、审批瓶颈、执行波动都会沉淀为 `sop_patch` 提案

当前还没做完的部分：

- 基于真实 OpenAI Agents SDK + MCP 调用结果的在线评测
- publish 后自动把 proposal 合并回更细粒度的 Skill/Playbook 发布策略
- Artifact blob 正式落到对象存储，而不只保存元数据

也就是说：

- “自动跑大量相似任务”已经有骨架
- “自动总结并提出 SOP 优化建议”已经有 proposal/evaluate/approve/publish 闭环
- “自动把建议无人工发布到生产”仍然没有做，而且按你的架构原则也不应该直接自动发布

## 存储说明

默认使用 SQLite 持久化到 `data/playbookos.db`，这样在当前环境里不依赖额外数据库驱动也能跑通 API。

当前已接入持久化的主表：

- `goals`
- `playbooks`
- `tasks`
- `runs`
- `artifacts`
- `reflections`

可用环境变量：

- `PLAYBOOKOS_DB_PATH`：自定义 SQLite 文件路径
- `DATABASE_URL=sqlite:///absolute/or/relative/path.db`：显式指定 SQLite URL
- `DATABASE_URL=postgresql://...`：当前会给出明确提示；正式 PostgreSQL schema 已放在 `data/sql/postgres_schema.sql`

## 本地运行

安装依赖后可直接启动：

```bash
pip install -e .
playbookos-api
```

或者：

```bash
uvicorn playbookos.api.app:app --host 0.0.0.0 --port 8000
```

启动后打开首页即可看到控制台：`http://127.0.0.1:8000/`

如果当前环境还没安装 `fastapi` / `uvicorn`，也可以直接用零依赖预览服务：

```bash
PYTHONPATH=src python3 -m playbookos.ui.preview_server --demo --port 8080
```

然后访问：`http://127.0.0.1:8080/`

## 下一步

下一步可以继续补：

- Temporal Python SDK 真正接入 workflow/activity
- PostgreSQL 运行时 adapter 或 SQLAlchemy/ORM 层
- 真实 OpenAI Agents SDK + MCP 调用执行器
- Dashboard 的交互筛选、详情页和更丰富的操作入口
- Artifact blob/object storage 落盘与下载能力
- Plane webhook / MCP 对接
