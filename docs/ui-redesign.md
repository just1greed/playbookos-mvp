# PlaybookOS 前端重构方案（2026-03-09）

## 1. 目标

这次前端重构不再把首页做成“所有模块长页面堆叠”，而是改成一个真正的控制台壳层：

- 默认打开即进入全局看板
- 左侧是稳定的导航目录
- 中间主区域只承载当前选中的工作台节点
- 设置与业务工作台分离
- 先完成信息架构、页面文案、交互分层与实施 TODO，再进入实现阶段

本次设计遵循两个原则：

1. `先全局、后节点`：用户一进来先看系统是否健康、卡在哪、正在跑什么，而不是先看编辑表单。
2. `先导航壳、后模块细节`：先把页面骨架、导航体系、状态模型与共享组件定下来，再逐页实现。

---

## 2. 顶层信息架构

前端重构后分成三层：

### A. 全局层

用于回答：

- 系统现在整体健康吗？
- 哪些 Goal / Task / Run 正在推进？
- 卡点在哪个节点？
- 学习闭环有没有在持续发生？

对应页面：

- `全局看板`

### B. 工作台层

用于回答：

- 某一类对象怎么创建、编辑、复用、排查？
- 它和上游/下游对象的关系是什么？
- 当前这一类对象的待处理项是什么？

对应导航节点：

- `目标`
- `SOP`
- `Skill`
- `MCP`
- `知识库`
- `任务`
- `会话`
- `自动迭代`
- `审批流`
- `提示词`

### C. 设置层

用于回答：

- 模型和执行策略怎么配置？
- 系统默认行为是什么？
- 会话和运行时怎么治理？

对应页面：

- `模型设置`
- `全局设置`
- `会话管理`

---

## 3. 页面壳层设计

## 3.1 总体布局

采用三段式布局：

- `左侧导航栏`：固定宽度，承载目录、分组、当前状态点、折叠入口
- `顶部上下文栏`：承载当前页面标题、全局筛选器、刷新按钮、环境状态
- `主内容区`：渲染当前选中的页面模块

## 3.2 左侧导航分组

建议分为四组：

### `总览`

- 全局看板

### `工作台`

- 目标
- SOP
- Skill
- MCP
- 知识库
- 任务
- 会话
- 自动迭代
- 审批流
- 提示词

### `设置`

- 模型设置
- 全局设置
- 会话管理

### `系统`

- API 健康
- 错误记录
- 版本信息

说明：

- `系统` 组可以先不做成完整页面，但导航结构先预留。
- 左侧每个节点后面可显示一个轻量状态徽标，如待审批数量、草稿数量、失败数量。

## 3.3 顶部上下文栏

顶部栏统一包含：

- 当前页面标题
- 页面副标题
- 全局刷新按钮
- 全局作用域筛选器
- 最近刷新时间
- 环境状态标签

推荐的全局作用域筛选器：

- `全部 Goal`
- `按 Goal`
- `按 SOP`
- `按状态`

第一版实现时，不要求所有页面都支持复杂筛选，但顶部筛选组件要先设计成统一壳。

---

## 4. 默认首页：全局看板

## 4.1 页面目标

用户打开首页后，第一眼应该看到：

- 当前系统里一共有多少对象
- 哪些流程在运行
- 哪里阻塞了
- 学习闭环有没有在产出
- 下一步最值得点进去处理的是什么

## 4.2 页面结构

全局看板建议分成六块：

### 1）系统摘要卡片

展示：

- Goal 总数 / 状态分布
- Task 总数 / 状态分布
- Run 总数 / 状态分布
- Session 总数 / 状态分布
- Approval / Knowledge Update / Reflection 数量

目标：让用户在 5 秒内判断系统是否“活着”。

### 2）运行流程总览

用一条横向流程带展示：

`Goal -> SOP -> Skill/MCP -> Task -> Run -> Acceptance -> Reflection -> Knowledge`

每个节点显示：

- 当前对象数
- 待处理数
- 异常数
- 可点击进入对应工作台

### 3）关键阻塞区

展示：

- waiting_human runs
- blocked goals
- failed runs
- rejected reflections
- missing MCP / missing Skill 的 SOP 引导项

目标：让用户先处理阻塞，而不是先翻明细。

### 4）进行中任务区

展示：

- 当前 running / ready / waiting_human 的 Task
- 对应 Goal / SOP / Skill / assignee queue
- 一键跳转到任务或审批流页面

### 5）自动迭代动态区

展示：

- 最近的 reflection proposals
- knowledge updates
- newly published SOP patches
- draft skill / draft MCP 建议

### 6）推荐动作区

系统主动给出下一步建议，例如：

- `有 3 个 Run 等待审批，建议先进入审批流`
- `这份 SOP 识别出 github/slack，但缺少 github MCP，建议先创建 MCP draft`
- `有 2 个 draft Skill 还没补 authoring pack`

## 4.3 首页文案建议

- 页面标题：`全局看板`
- 页面副标题：`先看系统健康度、流程进度和阻塞点，再进入具体工作台处理对象。`
- 核心按钮：
  - `刷新全局状态`
  - `查看流程总览`
  - `打开待处理事项`
  - `查看最近学习产出`

---

## 5. 各工作台节点设计

## 5.1 目标工作台

### 页面目标

管理业务目标与目标级推进状态。

### 关键模块

- Goal 列表
- Goal 概览卡
- Goal 状态过滤
- Goal 详情抽屉
- Goal 动作区：plan / dispatch / autopilot

### 首批重点能力

- 创建 Goal
- 查看 Goal 当前状态与下游对象数量
- 从 Goal 直接进入 Task / Session / Learning 视角

### 页面文案

- 标题：`目标工作台`
- 副标题：`管理业务目标、推进节奏和目标级执行闭环。`

## 5.2 SOP 工作台

### 页面目标

管理 SOP / Playbook 的导入、解析、编译、补丁审阅与对象关系。

### 关键模块

- SOP 列表
- 导入区（Markdown 为主）
- 解析摘要
- 工具识别与 Skill/MCP 引导
- SOP patch review
- 关联 Task / Skill / MCP 视图

### 首批重点能力

- 导入 Markdown SOP
- 看 steps / detected tools / missing MCP / suggested Skill
- 一键进入 Skill 或 MCP 工作台继续补齐

### 页面文案

- 标题：`SOP 工作台`
- 副标题：`从 Markdown SOP 到 Playbook、工具识别、补丁审阅与执行入口。`

## 5.3 Skill 工作台

### 页面目标

管理 Skill 的草稿、版本、依赖 MCP、authoring pack 与发布状态。

### 关键模块

- Skill 列表
- Draft / Active / Deprecated 分栏
- Authoring Wizard 区
- 版本链视图
- 依赖 MCP 关系图

### 首批重点能力

- 创建 Skill
- 应用 authoring pack
- 查看版本链
- 从 SOP 建议回填 Skill 表单

### 页面文案

- 标题：`Skill 工作台`
- 副标题：`管理技能草稿、版本演进、依赖 MCP 与发布策略。`

## 5.4 MCP 工作台

### 页面目标

管理 MCP registry、草稿 MCP、配置状态和后续连通性治理。

### 关键模块

- MCP 列表
- Draft / Active / Error 分栏
- MCP 详情编辑器
- 来自 SOP 的 draft MCP 建议
- 依赖该 MCP 的 Skill / SOP 列表

### 首批重点能力

- 创建 / 编辑 MCP
- 查看缺口来源（哪份 SOP、哪条 tooling guidance）
- 标记状态

### 后续重点能力

- 连接验证
- 凭证配置
- 健康检查
- scope 风险提示

### 页面文案

- 标题：`MCP 工作台`
- 副标题：`管理 MCP 注册表、草稿接入、依赖关系和后续运行时治理。`

## 5.5 知识库工作台

### 页面目标

管理知识条目与知识更新提案。

### 关键模块

- KnowledgeBase 列表
- KnowledgeUpdate 队列
- 应用 / 拒绝入口
- 关联 Goal / Task / Reflection 视图

### 页面文案

- 标题：`知识库工作台`
- 副标题：`管理知识沉淀、更新提案与任务执行上下文。`

## 5.6 任务工作台

### 页面目标

管理 Task DAG、任务状态与执行入口。

### 关键模块

- Task 列表
- 状态泳道：inbox / ready / running / waiting_human / done
- DAG 关系视图
- Task 详情抽屉
- 关联 Run / Acceptance / Knowledge 视图

### 页面文案

- 标题：`任务工作台`
- 副标题：`查看任务图、执行状态、阻塞依赖和任务级动作。`

## 5.7 会话工作台

### 页面目标

管理 supervisor / worker session 树，以及会话级调度上下文。

### 关键模块

- Session 树
- Goal 维度汇总
- Worker 子会话明细
- 会话摘要 / 输入上下文 / 输出上下文

### 页面文案

- 标题：`会话工作台`
- 副标题：`追踪主控会话、子会话树和执行上下文流转。`

## 5.8 自动迭代工作台

### 页面目标

集中展示反思、学习、补丁、版本晋级和系统推荐动作。

### 关键模块

- Reflection proposal 列表
- KnowledgeUpdate 列表
- Skill draft / new version 建议
- SOP patch publish 记录
- 自动迭代推荐动作

### 页面文案

- 标题：`自动迭代工作台`
- 副标题：`管理反思提案、知识回写、补丁发布和学习闭环。`

## 5.9 审批流工作台

### 页面目标

集中处理所有需要人工介入的节点。

### 关键模块

- waiting_human runs
- pending acceptances
- pending knowledge updates
- reflection approvals
- 高风险动作队列

### 页面文案

- 标题：`审批流工作台`
- 副标题：`集中处理等待人工确认、验收、批准与拒绝的关键节点。`

## 5.10 提示词工作台

### 页面目标

把系统里真正用到的 prompt block 可视化、版本化、可调试化。

### 关键模块

- prompt block 列表
- 按用途分类：tool discovery / skill upload / mcp upload / authoring / reflection
- prompt 详情区
- 输入上下文预览
- 未来的版本比较区

### 首批重点能力

- 先只做只读展示
- 让用户看清楚“系统现在在用哪些提示词”

### 后续能力

- prompt 编辑
- prompt 实验
- prompt 版本对比

### 页面文案

- 标题：`提示词工作台`
- 副标题：`查看系统关键提示词、用途、输入上下文和后续调优入口。`

---

## 6. 设置页面设计

## 6.1 模型设置

### 页面目标

管理当前 AI 模型和接口配置。

### 第一版字段

- provider（先只读或枚举）
- api format（responses / chat.completions）
- model
- base url
- timeout
- max output tokens
- temperature

### 页面文案

- 标题：`模型设置`
- 副标题：`管理当前 AI 模型、接口格式和调用参数。`

## 6.2 全局设置

### 页面目标

管理系统级默认行为。

### 第一版字段

- 默认语言
- 默认刷新频率
- 默认视图（首页是否固定到全局看板）
- 错误记录路径
- 对象存储路径
- 是否显示实验性模块

### 页面文案

- 标题：`全局设置`
- 副标题：`管理控制台默认行为、显示偏好和系统级参数。`

## 6.3 会话管理

### 页面目标

管理用户侧会话与执行上下文治理。

### 第一版功能

- 查看 supervisor / worker session 总量
- 查看异常 session
- 清理失效 session（后续）
- 查看最近会话树

### 页面文案

- 标题：`会话管理`
- 副标题：`查看会话资源、异常状态和后续治理入口。`

---

## 7. 共享组件设计

重构时先抽象这几类共享组件：

- `AppShell`：左侧导航 + 顶栏 + 主内容区
- `NavSection`：导航分组
- `PageHeader`：标题 / 副标题 / 操作按钮 / 刷新时间
- `StatusPill`：状态徽标
- `MetricCard`：全局摘要卡
- `EntityTable`：通用列表
- `DetailDrawer`：对象详情抽屉
- `ActionQueueCard`：待处理事项卡
- `FlowRibbon`：全局流程带
- `EmptyState`：空态

注意：

- 先做结构统一，不急着一开始就把所有对象卡片做得很复杂。
- 共享组件要优先满足“可在单文件前端里组织代码”，避免再次回到一个超长模板函数里。

---

## 8. 路由与状态建议

虽然当前前端是单文件 Dashboard，但重构时建议至少引入页面级状态概念：

- `route = dashboard | goals | playbooks | skills | mcp | knowledge | tasks | sessions | learning | approvals | prompts | model-settings | global-settings | session-admin`
- 用 hash route 或轻量路由状态即可，不一定要引入前端框架

共享状态分三层：

- `boardSnapshot`：给全局看板和导航徽标用
- `resourceCache`：按资源类型缓存列表
- `uiState`：当前页面、筛选条件、选中对象、语言、最近刷新时间

---

## 9. 实施顺序 TODO

## Phase 1：壳层与导航

- [x] 新建 `AppShell` 布局
- [x] 左侧导航分组与路由状态
- [x] 顶部上下文栏
- [x] 默认首页切到全局看板
- [x] 导航与页面标题联动

## Phase 2：全局看板

- [x] 系统摘要卡
- [x] 流程总览带
- [x] 阻塞区
- [x] 进行中任务区
- [x] 自动迭代动态区
- [x] 推荐动作区

## Phase 3：基础工作台

- [ ] 目标工作台
- [~] SOP 工作台（已补页面级 focus 卡片、SOP 导入引导与资源过滤）
- [~] Skill 工作台（已补页面级 focus 卡片、authoring/版本入口与资源过滤）
- [~] MCP 工作台（已补注册表/接入缺口双栏内容区）
- [~] 知识库工作台（已补知识条目/更新提案双栏内容区）
- [~] 任务工作台（已补任务队列/执行压力双栏内容区）

## Phase 4：治理与观察页面

- [~] 会话工作台（已补会话时间线/会话健康双栏内容区）
- [~] 自动迭代工作台（已补学习流水线/学习队列双栏内容区）
- [~] 审批流工作台（已补待审批/待评审 focus 卡片）
- [~] 提示词工作台（已补 SOP prompt blocks 的 route focus，只读）

## Phase 5：设置页

- [~] 模型设置（已补运行时模型/请求格式实时摘要）
- [~] 全局设置（已补 UI / API / 快照实时摘要）
- [~] 会话管理（已补 session/event/child session 实时摘要）

## Phase 6：后续增强

- [ ] MCP 连接验证与健康检查 UI
- [ ] Prompt 编辑 / 实验 / 版本对比
- [ ] SOP patch diff 专门页面
- [ ] 更强的全局筛选器与跨对象联动

---

## 10. 当前实现映射与缺口

当前页面里已经存在但需要重组的能力：

- Board 状态分布
- Action Center
- Session Tree
- Supervisor Center
- Patch Review
- Skill Version Center
- Workbench 表单
- Authoring Wizard
- Execution Inspector
- Ingestion Guidance

这些并不是要删掉，而是要重新放位：

- `Board / Action / Rhythm` -> 放入 `全局看板`
- `Workbench 表单` -> 分拆到各工作台
- `Patch Review / Reflection / Knowledge Update` -> 放入 `自动迭代工作台`
- `waiting_human / accept / approve` -> 放入 `审批流工作台`
- `prompt blocks / ingestion prompts` -> 放入 `提示词工作台`
- `Session Tree / Supervisor Center` -> 放入 `会话工作台`
- `Execution Inspector` -> 可先挂在 `会话工作台` 或 `任务工作台`

---

## 11. 本轮设计结论

本轮达成的设计结论是：

1. 首页必须先切换为 `全局看板`，而不是继续展示一个超长工作台拼盘。
2. 左侧导航必须成为稳定的一级结构，把对象管理、学习治理和系统设置分开。
3. `目标 / SOP / Skill / MCP / 知识库 / 任务 / 会话 / 自动迭代 / 审批流 / 提示词` 这十个工作台节点是合理的第一版目录。
4. `模型设置 / 全局设置 / 会话管理` 作为设置页单独成组，避免和业务对象混在一起。
5. 实现顺序先做壳层与全局看板，再逐个把已有模块迁移到对应工作台，不做一次性大爆改。

## 12. 实施记录

- 2026-03-09：已完成第一阶段壳层改造，前端现在具备左侧导航、顶部页面上下文栏、hash 路由切换、页面标题联动，以及默认进入 `全局看板` 的行为。
- 2026-03-09：已在首页补上 `任务流程总览` 区块，用 `Goal -> SOP -> Skill/MCP -> Task -> Run -> Acceptance/Reflection -> Knowledge` 的摘要链路展示系统推进状态。

- 2026-03-09：已完成第二轮页面级重构，`SOP / Skill / 审批流 / 提示词` 路由新增 focus 卡片，首页之外的工作台开始具备自己的状态摘要，不再只是共享一套长页面。
- 2026-03-09：`Quick Resource Peek` 已改为按当前路由过滤，只展示当前工作台最相关的对象（例如 SOP 页看 `playbooks / skills / mcp / reflections`，审批页看 `runs / reflections / knowledge updates / tasks`）。
- 2026-03-09：修复了本轮重构中丢失的 `renderResourceRows / renderWorkbenchOptions / editor helpers / submit handlers`，重新保证 Dashboard 在 8081 预览环境可正常启动与刷新。

- 2026-03-09：已继续完成第三轮工作台迁移，`MCP / 知识库 / 任务` 路由新增专属双栏内容区，不再只剩创建表单；现在会先展示注册表、知识回写、任务压力等与当前节点最相关的实体。

- 2026-03-09：已继续补完整体首页，新增 `关键阻塞区 / 推荐动作区` 双栏区块；首页现在会主动汇总 blocked goals、waiting_human runs、失败执行、被拒绝反思和 SOP 检测出的 MCP 缺口，并给出下一步应进入的工作台。

- 2026-03-09：已继续完成 `会话 / 自动迭代 / 设置页` 的页面迁移。会话页新增 `会话时间线 / 会话健康`，自动迭代页新增 `学习流水线 / 学习队列`，设置页三张卡片也开始展示实时运行摘要，而不是纯占位文案。

- 2026-03-09：已补上首页剩余两块核心区：`进行中任务区 / 自动迭代动态区`。现在默认首页已经具备系统摘要、流程总览、关键阻塞、推荐动作、进行中任务和学习动态六块核心信息。

- 2026-03-09：已把顶部全局范围从静态文案升级为真实筛选联动，支持 `全部 / 按 Goal / 按 SOP / 按状态` 两级过滤；当前页面摘要、路由内容区、资源速览、操作区和侧边导航计数都会跟随过滤结果刷新。

---

## 10. 当前已落地（2026-03-09，模型设置）

本轮已经把“设置页可编辑能力”的第一块真正落地：`模型设置` 不再只是摘要卡，而是具备运行时可编辑表单。

### 已实现

- 新增运行时设置存储：`data/runtime_settings.json`
- 新增统一运行时设置层：`src/playbookos/runtime_settings.py`
- Dashboard 设置页已支持编辑以下字段：
  - `base_url`
  - `model`
  - `api_format`
  - `timeout_seconds`
  - `temperature`
  - `max_output_tokens`
  - `organization`
  - `project`
  - `api_key`
- 前端已接入：
  - `GET /api/runtime-settings`
  - `PUT /api/runtime-settings`
- Preview Server 与 FastAPI App 的执行入口，现统一读取运行时模型配置，而不再只依赖进程启动时环境变量

### 当前意义

这意味着：

- 用户可以直接在 UI 中切换模型网关和模型名
- 可以先保留环境变量默认值，再按页面覆盖部分字段
- API Key 不会明文回显，只展示 masked preview
- 后续做“多模型 / 环境切换 / provider presets”时，已经有统一状态入口

### 当前新增（全局设置 + 会话管理）

本轮继续把设置页从“摘要页”推进到“治理页”：

- `全局设置` 已支持：
  - 默认语言
  - 自动刷新间隔
  - 默认全局筛选范围
  - 默认首页路由
  - 是否显示 `系统` 导航分组
- 这些设置已经真正驱动 Dashboard 行为：
  - 无本地覆盖时自动应用默认语言
  - 自动刷新定时器按设置生效
  - 默认路由与默认筛选范围会在首次进入时接管页面初始态
  - 侧边栏可按设置隐藏 `系统` 分组
- `会话管理` 已支持：
  - 按 Goal 过滤
  - 按 Run 过滤
  - 选择具体 session
  - 更新 session 的状态 / 标题 / objective / summary

### 当前新增（模型设置增强）

本轮继续把 `模型设置` 从“纯参数编辑”推进到“可切换、可验证”：

- 已新增 `provider preset`：
  - `OpenAI / Responses`
  - `OpenAI / Chat Completions`
  - `Custom OpenAI-Compatible`
- 前端支持一键把 preset 回填到 `base_url / api_format / model`
- 已新增 `POST /api/runtime-settings/test`，可对当前表单里的模型配置做连通性探测
- 没有 API Key 时，测试接口会返回明确的 `missing_api_key`，而不是前端直接报错
- 连接成功时会回显 `response_id / response_model / output_preview`，方便快速确认网关与模型是否通

### 下一步设置方向

设置页后续仍缺：

- `全局设置` 里的更多系统级参数（对象存储路径、错误日志策略、实验开关）
- `会话管理` 的批量治理动作（归档、批量关闭、异常会话清理）
- 模型设置里的保存历史 / 最近成功配置 / 多环境切换

