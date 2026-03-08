# PlaybookOS PRD

## 1. 产品定义

PlaybookOS 是一个 AI 工作操作系统，用来把组织中的 SOP、知识资产、工具权限、任务编排、Agent 执行、人工审批和反思迭代沉淀为统一工作闭环。

## 2. 产品目标

### 2.1 核心目标

- 让团队能够把目标（Goal）转成可执行任务 DAG
- 让 SOP 从文档资产变成可执行 Playbook
- 让技能（Skill）和工具（MCP Server）以版本化、可控权限方式被调度
- 让长任务具备 durable execution、恢复、重试、审批和 trace
- 让每次执行后的经验沉淀形成 Reflection proposal，并通过评测与批准晋级

### 2.2 成功标准

MVP 阶段至少支持：

- 创建 Goal，并定义约束、验收标准、预算与截止时间
- 上传 SOP / 附件，并编译成 Playbook
- 基于 Playbook 生成 Task DAG
- 任务进入统一状态流转：`Inbox -> Ready -> Running -> Waiting Human -> Blocked -> Review -> Done -> Learned`
- 每个 Run 记录 trace、产物、失败分类与反思提案
- Reflection 不直接修改线上 Skill，必须经过评测和人工批准

## 3. 目标用户

- AI Automation / Ops 团队
- 内部流程数字化团队
- 需要长任务、多步骤审批、可恢复执行的业务团队
- 需要用 Plane 作为工作台、用 Agent/Worker 作为执行面的团队

## 4. 非目标

MVP 不追求：

- 通用聊天产品
- 纯 Prompt 管理平台
- 无状态的“调用一次模型就结束”的单步 Agent
- 直接让模型改生产配置/技能/权限
- 复杂 BI 或大规模多租户计费体系

## 5. 核心对象

PlaybookOS 只保留八个一等对象：

- `Goal`
- `Playbook`
- `Skill`
- `MCPServer`
- `Task`
- `Run`
- `Artifact`
- `Reflection`

## 6. 核心流程

### 6.1 配置流程

- 上传 SOP / 附件
- 解析文档并生成结构化步骤
- 编译为 Playbook
- 绑定 Skill 与 MCP Server
- 定义 Goal 与完成标准

### 6.2 执行流程

- Planner 将 Goal 拆成 Task DAG
- Dispatcher 根据技能、负载、权限和审批要求派发任务
- Worker Supervisor 在隔离执行环境中运行任务
- 危险动作进入 HITL 审批
- Run 记录 trace、日志、产物和状态变迁

### 6.3 学习流程

- Reflector 汇总失败类别、经验与补丁提案
- 对 Skill patch 做回放评测
- 人工批准后发布新版本
- Board 将已学到的经验归档到 `Learned`

## 7. 板面状态设计

- `Inbox`：新进入系统、尚未准备
- `Ready`：前置条件满足，等待执行
- `Running`：正在执行
- `Waiting Human`：等待人工输入或审批
- `Blocked`：外部依赖未满足
- `Review`：执行结束，等待验收
- `Done`：验收通过
- `Learned`：已完成复盘沉淀

## 8. 风险与约束

### 8.1 必须避免的坑

- 把 MCP 当工作流引擎
- 把多 Agent 对话当任务系统
- 让自我进化直接改线上能力
- 给所有 Skill 全局写权限
- 让长任务只依赖内存上下文

### 8.2 约束原则

- 所有状态必须持久化
- 所有危险工具必须显式审批
- 所有 Skill 必须有输入/输出 schema
- 所有 Skill 升级必须经过 eval 和 approve
- 所有 Run 必须可追踪、可回放、可审计
