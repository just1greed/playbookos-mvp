# PlaybookOS Agent Operator 方案（2026-03-09）

## 1. 为什么要做

PlaybookOS 不应该只是给人类看的控制台，也应该是给外部 agent 使用的控制面系统。

目标形态是：

- `PlaybookOS` 负责状态、规则、审批、审计与对象关系
- `OpenClaw` 这类外部 agent 负责理解人类对话、提出计划、执行授权内操作、持续运营系统

这意味着外部 agent 不能只“看网页”，而要能：

- 自动发现 PlaybookOS 当前能力
- 把人类对话映射成结构化对象操作
- 在授权范围内托管和运营系统
- 在高风险动作上回到 HITL

## 2. 第一版落地范围

本轮先落三块：

1. `PlaybookOS Operator Skill`
2. `agent-friendly API`：manifest / context / intake
3. 文档与记忆记录，明确后续 delegation 演进方向

## 3. Agent 接入面

### 3.1 Manifest

`GET /api/agent/manifest`

用于回答：

- 这个系统支持哪些对象
- 每类对象支持哪些动作
- 推荐的 agent 使用顺序是什么
- 哪些动作属于高风险

### 3.2 Context

`GET /api/agent/context`

用于回答：

- 当前 board 状态如何
- 是否有 blocked goals / waiting_human runs
- 是否有 draft skills / unhealthy MCP / learning backlog
- 下一步建议优先处理什么

### 3.3 Intake

`POST /api/agent/intake`

用于把人类自然语言请求或 Markdown SOP 先转换成：

- `detected_intents`
- `missing_information`
- `follow_up_questions`
- `recommended_operations`
- `sop_preview`

注意：`intake` 第一版是 **dry-run planning surface**，不会直接修改系统状态。

## 4. Skill 设计

仓库内新增：`skills/playbookos-operator/`

它的定位不是产品宣传，而是给外部 agent 的操作指引：

- 先 bootstrap manifest/context
- 再用 intake 理解对话
- 最后调用显式控制面 API

Skill 当前支持四种模式：

- `discover`
- `builder`
- `operator`
- `steward`

## 5. 当前已支持的 agent 能力

截至 2026-03-09，外部 agent 已能：

- 发现 PlaybookOS 当前对象和推荐工作流
- 读取系统当前阻塞点和建议动作
- 把对话和 Markdown SOP 先转成 dry-run 操作计划
- 为 Markdown SOP 输出 Skill 草案建议、MCP 缺口、后续操作序列

## 6. 还未完成的部分

这仍然只是第一版，还缺：

1. `delegation profile`：授权边界、审批门槛、预算与巡检策略
2. `agent identity`：区分 human / operator-agent / delegate-agent
3. `dry-run -> apply` 的事务性执行编排
4. 更强的 `conversation -> object extraction`，尤其是 Goal/Task/Skill 细粒度字段提取
5. 真实托管循环：定时巡检、自动处理、人工升级

## 7. 推荐下一步

优先顺序建议改为：

1. `agent manifest/context/intake` 稳定化
2. `delegation profile` 与 agent 身份/审计
3. 对外 agent 的 apply/execution plan
4. 托管模式下的运营循环
