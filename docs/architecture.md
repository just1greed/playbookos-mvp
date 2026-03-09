# PlaybookOS 架构设计

## 1. 总体架构

PlaybookOS 推荐采用三层架构：

1. `Plane`：工作台 / 知识入口 / 协作界面
2. `Temporal`：持久化编排与任务运行时
3. `OpenAI Agents SDK`：Agent 执行内核与工具编排

配套基础设施：

- `Postgres`：事务数据、状态机、任务图、审计记录
- `Object Storage`：SOP 原件、附件、生成产物、评测数据集
- `Tracing / Eval`：运行追踪、回放评测、质量分析

## 2. 系统分层

### 2.1 Control Plane

负责配置、治理和可视化：

- Goal 管理
- Playbook 编译与版本管理
- Skill 注册与审批策略配置
- MCP Server 注册与权限边界
- Board / Inbox / Review / Learned 展示
- 人工审批与人工补充输入

### 2.2 Orchestration Plane

由 Temporal 驱动：

- Goal 启动 workflow
- Task DAG 调度
- 超时、重试、补偿
- 长时间挂起与恢复
- 子工作流编排
- Worker 负载分发

当前仓库已先落一层 `Temporal-ready` 编排核心：

- `planner` 生成 Task DAG
- `orchestrator` 推进任务状态并创建 `Run`
- 输出 `TemporalWorkflowSpec` 作为后续 workflow/activity 输入草案
- `dispatch` / `complete task` 链路已可本地运行和测试

### 2.3 Execution Plane

由 OpenAI Agents SDK 和执行 worker 组成：

- Agent 选择与 handoff
- MCP tool 调用
- session / trace 管理
- guardrails
- human-in-the-loop 中断点
- 产物生成与结果回传

## 3. 逻辑模块

- `ingestion`：接收 SOP、附件与外部事件
- `compiler`：把 SOP 解析并编译为 Playbook
- `planner`：把 Goal + Playbook 转成 Task DAG
- `dispatcher`：根据技能、权限和队列把 Task 分发给 worker
- `supervisor`：管理执行环境、审批门禁、失败恢复
- `executor`：封装 OpenAI Agents SDK 执行逻辑
- `reflection`：生成反思提案并触发评测
- `registry`：管理 Skill 与 MCPServer 元数据
- `board`：聚合 Goal / Task / Run 状态用于展示

## 4. 关键交互

### 4.1 Goal 到 Task

- 用户在 Plane 中创建 Goal
- Control Plane 将 Goal 写入 Postgres
- Temporal workflow 启动 planner
- planner 根据 Playbook 输出 Task DAG
- dispatcher 将可执行节点投递给 worker

### 4.2 Task 到 Run

- worker 拉取 Task
- supervisor 加载 Skill、MCP 权限和审批策略
- executor 调用 Agents SDK 执行
- 执行日志、trace 和 artifact 回写数据库 / 对象存储
- Task 状态根据结果推进到下一节点

当前本地骨架已实现：

- `POST /api/goals/{goal_id}/dispatch`：创建可派发批次和 `Run`
- `POST /api/tasks/{task_id}/complete`：标记完成并推进下游依赖
- `POST /api/runs/{run_id}/approve`：推进 `waiting_human` 任务继续执行
- `POST /api/runs/{run_id}/reject`：把任务和 Goal 标记为阻塞/失败

### 4.3 Run 到 Reflection

- 任务结束后触发 reflection pipeline
- reflector 生成失败分类和改进提案
- eval runner 使用回放集对提案进行评测
- 通过后进入人工批准
- 批准后发布新的 Skill 版本

## 5. 安全边界

- MCP 权限按 Skill 级别显式声明
- Run 执行环境必须隔离
- 文件、Git、工单、Shell 工具默认只读或最小权限
- 高风险操作必须进入 HITL
- Reflection 无法直接写生产 Skill

## 6. 推荐模块边界

### 6.1 API 服务

建议负责：

- Goal / Playbook / Skill / Task 查询与变更
- Webhook 接收
- 审批入口
- Board 聚合查询

### 6.2 Worker 服务

建议负责：

- Temporal activity 执行
- Agents SDK 运行
- 产物上传
- trace 回写
- 超时与错误分类

### 6.3 Reflector 服务

建议负责：

- 复盘分析
- skill patch proposal 生成
- evaluation pipeline
- publish gating

## 7. MVP 裁剪建议

第一阶段不必一次实现全部能力，优先顺序：

1. Goal / Playbook / Task / Run 主链路
2. Planner + Orchestrator 本地闭环
3. Board 状态机和审批中断
4. Artifact 持久化
5. Reflection proposal + 人工批准
6. Skill 版本发布与回放评测

## 8. 当前缺口与补齐顺序（2026-03-09）

结合当前代码状态，最大缺口不在后半段执行链，而在前半段建模链：

1. `SOP ingestion`：上传或粘贴原始 SOP、附件与来源元数据
2. `compiler/parser`：把原始 SOP 解析为 `Playbook + compiled_spec.steps + MCP hints`
3. `skill recommendation`：根据步骤语义、工具需求和风险提示生成 Skill 草案
4. `authoring wizard`：引导用户确认 Skill 描述、MCP 范围、审批策略、评测策略
5. `artifact/object storage`：保留 SOP 原件、附件与解析产物，支撑审计与回放

当前仓库已经能跑通 `Goal -> Playbook -> Task -> Run -> Reflection` 主链，但尚未完整支持“上传任意格式 SOP 后自动解析成对象，并主动引导用户配置 Skill”的前置建模流程。

目前第 1、2、3、4 项已经落下第一版闭环：用户可导入原始 SOP 文本/文本文件，系统会解析为 Playbook、给出 MCP hints 与 Skill 建议，并通过 authoring wizard 主动引导补齐 Skill 配置。

第 5 项也补上了最小实现：新增本地 `object_store`，把原始 SOP 原文保存为独立对象，并通过 `playbook.compiled_spec.source_object_*` 与 `/api/objects/*` 接口对外暴露，满足最基本的审计、回放和原文回看。

截至 2026-03-09，距离“用户上传任意格式 SOP 后自动解析成各种对象，并主动引导用户配置 Skill”的目标，当前仍剩以下缺口：

1. `任意格式` 本轮不优先：当前实现有意收敛到 `Markdown SOP`，先把“从 SOP 中找工具 -> 识别需要的 MCP -> 引导上传对应 Skill”这条提示词链打磨清楚；PDF、Docx、图片、多附件后续再补。
2. `附件拆解` 仍未完成：对象存储当前只保留原始文本主体，尚未建立附件索引、分块、引用关系与解析产物树。
3. `对象归一化` 仍未完成：已能生成 Playbook 与 Skill 草案，但 Knowledge、Task template、approval checklist 等派生对象还没有在 ingestion 阶段自动物化。
4. `主动引导` 仍是第一版：authoring wizard 已能补齐 schema / approval / evaluation 默认值，但缺少逐步问答式确认、风险解释和发布门禁。
5. `外部对象存储` 仍未完成：当前实现是本地文件目录，后续还需要升级到真正的云对象存储与评测数据集治理。
