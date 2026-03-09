# PlaybookOS 托管 Agent 演示示例（2026-03-09）

## 目标

这份示例记录当前已经跑通的一条最小闭环：

`manifest -> delegation profile -> agent apply -> playbook/skill/mcp draft materialization`

它的意义不是展示所有治理细节都已完成，而是证明：

- 外部 agent 已能发现 PlaybookOS 能力
- 已能在受限 delegation 边界内执行一组显式计划步骤
- 已能把 Markdown SOP 真正落成系统对象

## 演示前提

- PlaybookOS preview 已启动
- 使用 demo 数据或本地运行时 store
- agent 已持有 `playbookos-operator` skill

## 演示步骤

### 1. 读取 manifest

调用：`GET /api/agent/manifest`

验证点：

- 能看到 `playbookos-operator`
- 能看到 `manifest/context/intake/apply`
- 能看到 `delegation_profile` 对象类型

### 2. 创建 delegation profile

调用：`POST /api/delegation-profiles`

示例意图：为 `openclaw-main` 创建一个仅允许 SOP ingest、skill draft、mcp draft 的托管边界。

验证点：

- 生成 `delegation_profile_id`
- 约束包含 `allowed_endpoints`
- 约束包含 `max_operations_per_apply`

### 3. 执行 agent apply

调用：`POST /api/agent/apply`

示例输入：

- `message`：把这份 SOP 导入系统并补齐 skill 和 mcp
- `markdown_sop`：

```md
# Weekly report

1. Research competitor updates in Notion
2. Draft summary and send to Slack
```

- `agent_id`：`openclaw-main`
- `delegation_profile_id`：上一步生成的 profile id
- `operation_ids`：
  - `ingest_playbook`
  - `create_skill_draft_0`
  - `create_mcp_draft_notion`

验证点：

- 返回 `execution_mode = applied`
- 返回 `applied_operation_ids`
- 返回新建的 `playbook / skill / mcp_server` 资源 id

## 演示结果

这轮已验证：

- `GET /api/agent/manifest` 可返回 agent-facing 控制面描述
- `GET/POST /api/delegation-profiles*` 可读写托管边界
- `POST /api/agent/apply` 可在 delegation 约束下真实创建：
  - `Playbook`
  - `Skill draft`
  - `MCP draft`

## 当前边界

这仍然只是“最小可跑通”演示，不代表以下细节已经全部完成：

- 更细粒度的 agent identity 审计
- 完整的错误归因与系统级 issue 提交流程
- apply 的事务回滚
- 托管模式的定时巡检与自动升级

## 当前结论

项目当前优先级应保持为：

1. 先把外部 agent 的完整主链跑通
2. 再逐步补日志治理、审计、回滚、托管巡检等细节能力
