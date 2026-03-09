# PlaybookOS 数据模型

## 1. 核心对象

### 1.1 Goal

字段建议：

- `id`
- `title`
- `objective`
- `constraints_json`
- `definition_of_done_json`
- `risk_level`
- `budget_amount`
- `budget_currency`
- `due_at`
- `status`
- `owner_id`
- `created_at`
- `updated_at`

### 1.2 Playbook

字段建议：

- `id`
- `goal_id`（可空）
- `name`
- `source_kind`
- `source_uri`
- `compiled_spec_json`
- `version`
- `status`
- `created_at`
- `updated_at`

### 1.3 Skill

字段建议：

- `id`
- `name`
- `version`
- `description`
- `input_schema_json`
- `output_schema_json`
- `required_mcp_servers_json`
- `approval_policy_json`
- `evaluation_policy_json`
- `rollback_version`
- `status`
- `created_at`
- `updated_at`

### 1.4 KnowledgeBase

字段建议：

- `id`
- `goal_id`（可空）
- `name`
- `description`
- `content`
- `tags_json`
- `source_uri`
- `status`
- `created_at`
- `updated_at`

### 1.5 MCPServer

字段建议：

- `id`
- `name`
- `transport`
- `endpoint`
- `auth_config_json`
- `scopes_json`
- `status`
- `created_at`
- `updated_at`

### 1.6 Task

字段建议：

- `id`
- `goal_id`
- `playbook_id`
- `parent_task_id`（可空）
- `name`
- `description`
- `status`
- `priority`
- `depends_on_json`
- `assigned_skill_id`
- `approval_required`
- `queue_name`
- `created_at`
- `updated_at`

### 1.7 Run

字段建议：

- `id`
- `task_id`
- `attempt`
- `status`
- `worker_type`
- `trace_id`
- `session_id`
- `started_at`
- `finished_at`
- `error_class`
- `error_message`
- `metrics_json`
- `created_at`

### 1.8 Artifact

字段建议：

- `id`
- `run_id`
- `kind`
- `title`
- `uri`
- `mime_type`
- `checksum`
- `version`
- `metadata_json`
- `created_at`

### 1.9 Reflection

字段建议：

- `id`
- `run_id`
- `failure_category`
- `summary`
- `proposal_json`
- `eval_status`
- `approval_status`
- `approved_by`
- `published_target_version`
- `created_at`
- `updated_at`

### 1.10 Session

字段建议：

- `id`
- `goal_id`
- `task_id`（可空）
- `run_id`（可空）
- `parent_session_id`（可空）
- `title`
- `kind`
- `status`
- `objective`
- `input_context_json`
- `output_context_json`
- `summary`
- `created_at`
- `updated_at`

### 1.11 Acceptance

字段建议：

- `id`
- `goal_id`
- `task_id`
- `run_id`（可空）
- `criteria_json`
- `status`
- `artifact_ids_json`
- `reviewer_id`
- `notes`
- `findings_json`
- `created_at`
- `updated_at`

### 1.12 Event

字段建议：

- `id`
- `entity_type`
- `entity_id`
- `event_type`
- `payload_json`
- `source`
- `created_at`

## 2. PostgreSQL 表草案

建议首批建立下列表：

- `goals`
- `playbooks`
- `skills`
- `mcp_servers`
- `tasks`
- `task_edges`
- `runs`
- `sessions`
- `acceptances`
- `artifacts`
- `reflections`
- `approvals`
- `events`

当前仓库已经提供第一版实际 schema 文件：

- `data/sql/postgres_schema.sql`
- `data/sql/sqlite_schema.sql`

其中已先落地并接入 API 持久化链路的主表为：

- `goals`
- `playbooks`
- `skills`
- `tasks`
- `sessions`
- `runs`
- `acceptances`
- `artifacts`
- `reflections`
- `events`

## 3. 关系说明

- 一个 `Goal` 可关联多个 `Task`
- 一个 `Goal` 可绑定一个或多个 `Playbook`
- 一个 `Playbook` 可编译出多个 `Task`
- 一个 `Task` 可触发多次 `Run`
- 一个 `Goal` 有一个主 `Supervisor Session`，并可派生多个子 `Worker Session`
- 一个 `Run` 对应一个可见的 `Worker Session`
- 一个 `Run` 可产出多个 `Artifact`
- 一个 `Task` 可对应多条 `Acceptance` 记录
- 一个 `Run` 最多关联一个主 `Reflection`
- 一个 `Reflection` 可发布一个新的 `Playbook` 版本
- 一个 `Skill` 可绑定多个 `Task`
- 一个 `Skill` 可依赖多个 `MCPServer`

## 4. 状态枚举建议

### 4.1 GoalStatus

- `draft`
- `ready`
- `running`
- `blocked`
- `review`
- `done`
- `learned`
- `archived`

### 4.2 TaskStatus

- `inbox`
- `ready`
- `running`
- `waiting_human`
- `blocked`
- `review`
- `done`
- `learned`
- `failed`

### 4.3 RunStatus

- `queued`
- `running`
- `waiting_human`
- `succeeded`
- `failed`
- `cancelled`
- `timed_out`

### 4.4 ReflectionStatus

- `proposed`
- `evaluating`
- `approved`
- `rejected`
- `published`

### 4.5 SessionKind

- `supervisor`
- `worker`

### 4.6 SessionStatus

- `planned`
- `running`
- `waiting_human`
- `completed`
- `failed`

### 4.7 AcceptanceStatus

- `pending`
- `accepted`
- `rejected`

## 5. 事件流建议

建议维护统一事件表 `events`，记录：

- 实体类型
- 实体 ID
- 事件类型
- 事件负载
- 操作人 / 系统来源
- 时间戳

这样可以支持审计、看板聚合和后续回放。
