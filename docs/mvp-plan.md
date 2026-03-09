# PlaybookOS MVP 技术方案

## 1. 技术路线

当前项目采用最稳可扩展路线：

- 工作台：`Plane`
- 编排：`Temporal`
- Agent 执行：`OpenAI Agents SDK`
- 数据库：`Postgres`
- 文件与产物：`Object Storage`

## 2. MVP 模块边界

### 2.1 `api`

职责：

- Goal CRUD
- Playbook 创建 / 编译触发
- Task / Run 查询
- 审批接口
- Board 聚合视图
- autopilot / learning 查询

### 2.2 `domain`

职责：

- Goal / Playbook / Skill / Knowledge / Task / Session / Run / Acceptance / Artifact / Reflection / Event 核心对象模型
- 枚举和值对象
- 基础校验规则

### 2.3 `planner`

职责：

- 根据 Goal + Playbook 生成 Task DAG
- 生成任务依赖边
- 输出可调度节点
- 保证重复规划不重复造任务

当前已实现：

- `playbook.compiled_spec.steps` -> `Task DAG`
- 默认串行依赖链生成
- `depends_on` 名称 / 索引依赖解析
- 无步骤时的回退任务生成
- `POST /api/goals/{goal_id}/plan`
- `POST /api/goals/{goal_id}/start` 自动触发规划

### 2.4 `orchestrator`

职责：

- Temporal workflow/activity 封装
- 重试、超时、补偿、恢复
- 队列与 worker 路由
- 任务推进与可派发批次生成

当前已实现：

- `dispatch_goal_in_store`
- `complete_task_in_store`
- `TemporalWorkflowSpec` 输出
- `POST /api/goals/{goal_id}/dispatch`
- `POST /api/tasks/{task_id}/complete`

### 2.5 `supervisor`

职责：

- 为 Goal 建立主控会话
- 为 Run 建立子会话
- 维护用户可见的事件流
- 维护任务验收与签收

当前已实现：

- `ensure_goal_supervisor_session`
- `ensure_worker_session_for_run`
- `update_session_for_run`
- `accept_task_in_store`
- `append_event`
- `GET /api/sessions`
- `GET /api/acceptances`
- `GET /api/events`
- `POST /api/tasks/{task_id}/accept`

### 2.6 `executor`

职责：

- OpenAI Agents SDK 封装
- MCP tool 绑定
- handoff / guardrails / session / trace
- HITL 中断点输出
- 批量自动执行相似任务

当前已实现：

- `OpenAIAgentsSDKAdapter` 载荷适配层
- `DeterministicExecutorAdapter` 本地无依赖执行器
- `execute_run_in_store`
- `autopilot_goal_in_store`
- 自动生成 `run_report` Artifact 元数据
- `POST /api/runs/{run_id}/execute`
- `POST /api/goals/{goal_id}/autopilot`

### 2.7 `reflection`

职责：

- 失败分类
- proposal 生成
- eval pipeline 入口
- publish gating
- SOP/Playbook 改进建议汇总

当前已实现：

- `reflect_run_in_store`
- `analyze_goal_learning`
- `evaluate_reflection_in_store`
- `approve_reflection_in_store`
- `publish_reflection_in_store`
- success / approval-bottleneck / execution-variance 的 proposal 归类
- `POST /api/runs/{run_id}/reflect`
- `GET /api/goals/{goal_id}/learning`
- `POST /api/reflections/{reflection_id}/evaluate`
- `POST /api/reflections/{reflection_id}/publish`

## 3. API 草案

### 3.1 Goals

- `POST /api/goals`
- `GET /api/goals`
- `GET /api/goals/{goal_id}`
- `POST /api/goals/{goal_id}/plan`
- `POST /api/goals/{goal_id}/dispatch`
- `POST /api/goals/{goal_id}/autopilot`
- `GET /api/goals/{goal_id}/learning`
- `POST /api/goals/{goal_id}/start`
- `POST /api/goals/{goal_id}/complete-review`

### 3.2 Playbooks

- `POST /api/playbooks/import`
- `POST /api/playbooks/{playbook_id}/compile`
- `GET /api/playbooks/{playbook_id}`

### 3.3 Skills / Sessions / Acceptances / Events

- `POST /api/skills`
- `GET /api/skills`
- `GET /api/skills/{skill_id}`
- `GET /api/sessions`
- `GET /api/sessions/{session_id}`
- `GET /api/acceptances`
- `GET /api/acceptances/{acceptance_id}`
- `GET /api/events`
- `POST /api/tasks/{task_id}/accept`

### 3.4 Tasks / Runs

- `GET /api/tasks`
- `GET /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/complete`
- `GET /api/runs/{run_id}`
- `POST /api/runs/{run_id}/execute`
- `POST /api/runs/{run_id}/reflect`
- `POST /api/runs/{run_id}/approve`
- `POST /api/runs/{run_id}/reject`

### 3.5 Reflections

- `GET /api/reflections`
- `POST /api/reflections/{reflection_id}/evaluate`
- `POST /api/reflections/{reflection_id}/approve`
- `POST /api/reflections/{reflection_id}/reject`
- `POST /api/reflections/{reflection_id}/publish`

### 3.6 Artifacts

- `POST /api/artifacts`
- `GET /api/artifacts`
- `GET /api/artifacts/{artifact_id}`

## 4. 目录规划

建议逐步演进为：

- `src/playbookos/api/`
- `src/playbookos/domain/`
- `src/playbookos/planner/`
- `src/playbookos/orchestrator/`
- `src/playbookos/ui/`：控制台与工作台页面
- `src/playbookos/supervisor/`
- `src/playbookos/executor/`
- `src/playbookos/reflection/`
- `src/playbookos/registry/`

## 5. 迭代里程碑

### Milestone 1：项目骨架

- 领域模型
- 文档基线
- 基础测试
- 仓库说明

### Milestone 2：控制面主链路

- Goal / Playbook / Skill / Knowledge / Task / Run API
- Session / Acceptance / Event API
- Board 查询
- SQLite 持久化
- Planner 任务拆解
- Orchestrator 调度核心
- Supervisor 可视化会话链路
- Executor 适配层
- Reflection 学习摘要

### Milestone 3：编排与执行

- Temporal workflow
- 真实 executor 适配层
- 审批中断
- Artifact 持久化
- proposal -> eval -> approve -> publish

### Milestone 4：反思与晋级

- Reflection proposal
- Eval gating
- 人工批准
- Skill version publish
- 回放评测与回归集

## 5.1 进行中的缺口收敛（2026-03-09）

在 `MCP runtime / credential / health` 方向，当前先补 `health probe`，暂不直接实现完整 tool runtime：

- 已实现：MCP 注册、CRUD、SOP 缺口 draft MCP、MCP endpoint health probe
- 未实现：凭证治理、真正的 MCP 握手与 tool 调用、租户级权限与审计

因此下一阶段的落地顺序调整为：

1. MCP health / connectivity
2. MCP credential / auth 治理
3. MCP runtime / tool execution
4. 更强的 Skill / SOP / Knowledge 联动

## 5.2 Agent-facing Control Plane（2026-03-09）

为了让 OpenClaw 这类外部 agent 能真正使用和托管 PlaybookOS，MVP 需要新增一条 agent-facing surface：

- `GET /api/agent/manifest`：能力发现
- `GET /api/agent/context`：运行上下文同步
- `POST /api/agent/intake`：自然语言 / Markdown SOP -> dry-run 操作计划
- `POST /api/agent/apply`：按 delegation 约束执行显式计划步骤
- `GET/POST/PUT /api/delegation-profiles*`：外部 agent 的托管边界与审批门槛
- `skills/playbookos-operator/`：给外部 agent 的操作 skill

这一层的原则是：

1. `manifest/context/intake` 负责理解与规划
2. 真实变更仍走显式控制面 API
3. 高风险动作继续保留 HITL 和审批边界

## 6. 当前代码落地策略

当前仓库已实现：

- `domain` 层稳定核心对象
- `api` 控制面基础路由
- `persistence` 持久化 store
- `planner` 从 Playbook 生成 Task DAG
- `orchestrator` 推进任务和生成 `Run`
- `supervisor` 维护主控会话、子会话、验收与事件流
- `executor` 执行 `Run` 并支持 autopilot
- `reflection` 为 SOP 生成改进 proposal

下一步建议优先：

- patch diff、版本回放与审批视图
- 主控会话对子会话的更细粒度并行调度
- 真实 OpenAI Agents SDK + MCP 调用
- Artifact blob/object storage 持久化
- Temporal workflow 对接 planner/orchestrator/executor/supervisor
