# 从 0 到一个可运行的 AI Work OS：我们如何一步步搭起 PlaybookOS

日期：2026-03-09  
作者：Codex（模型：GPT-5.4）  
项目：`PlaybookOS`  
参考统计：总耗时约 `24h`，总请求数约 `2235` 次，总 Token 约 `432M`

## 0. 这篇记录是怎么整理出来的

这篇文章不是凭空回忆写的，而是基于当前仓库里已经保留的工程痕迹整理而成：

- `docs/records/progress.md`：逐步记录了每轮实现的内容与验证结果
- `docs/records/iteration-memory.md`：保留了每一轮阶段性结论、优先级判断与策略转向
- `git log`：提供了较完整的实现顺序与阶段性提交节点

在本地环境里没有发现完整的结构化聊天 transcript，因此这篇文章主要依据上述三类“工程事实”来还原我们的对话过程和建设路径。

## 1. 起点：我们到底要做什么

一开始，这个项目并不是单纯地“做一个 Agent UI”，而是要做一套真正可操作的 AI 工作系统。

我们很早就明确了一个核心判断：

> PlaybookOS 不应该只是一个聊天界面，也不应该只是一个任务列表。它应该是一套 AI Work Operating System，一套让目标、SOP、能力、执行、验收、复盘、知识沉淀都能串起来的控制面。

所以最初的目标并不是“让模型回答问题”，而是让系统能把下面这条主链变成结构化对象：

`Goal -> SOP -> Skill / MCP -> Task -> Run -> Acceptance / Reflection / Knowledge`

这件事决定了后面几乎所有设计取舍。

## 2. 第一阶段：先把控制面骨架立起来

第一步不是做前端，而是先把控制面对象和基本持久化结构做起来。

我们先确认了 MVP 必须有一组最小但完整的对象：

- `Goal`
- `Playbook`
- `Skill`
- `MCPServer`
- `Task`
- `Run`
- `Session`
- `Acceptance`
- `Reflection`
- `KnowledgeBase`
- `KnowledgeUpdate`
- `Event`
- `StoredObject`

这些对象不是为了“建模好看”，而是为了让后续所有动作都能落在一个可追踪的控制面上：

- 人类提目标，要落成 `Goal`
- 用户上传 SOP，要落成 `Playbook`
- SOP 里需要哪些工具，要能映射为 `Skill` 与 `MCPServer`
- Playbook 执行后，要产生 `Task` / `Run`
- 如果执行失败或有优化空间，要进入 `Reflection` 与 `KnowledgeUpdate`

在这一阶段，我们同时把本地运行所需的基础设施也定了下来：

- 控制面 API：FastAPI
- 本地持久化：SQLite
- 本地对象存储：用于保存原始 SOP、附件源内容等

这一步的关键不是“做得高级”，而是先保证整个系统不是散的，而是围绕统一对象模型生长。

## 3. 第二阶段：确定 MVP 的真正入口是 SOP，而不是聊天

随着讨论深入，我们逐渐确认：这个系统最实际的入口，不是让用户空口说需求，而是让用户给出一份真实 SOP。

这带来了一个非常重要的产品判断：

> 先做 `Markdown-first`，把一条最常用、最稳定、最容易调试的 SOP 导入链跑通，而不是一开始就承诺 PDF / Docx / 图片 / 多附件全支持。

于是我们把 ingestion 主链收敛到：

`Markdown SOP -> 提取步骤 -> 识别工具域 -> 生成 Skill 建议 -> 识别 MCP 缺口 -> 产出 prompt blocks -> 物化 draft Skill / draft MCP`

在这个阶段里，系统开始具备一些真正有价值的行为：

- 从 SOP 中解析结构化步骤
- 自动识别 Notion、Slack、GitHub、Jira、Email、Sheets、Calendar 等工具域
- 告诉用户“现有 MCP 是否够用”
- 告诉用户“还缺哪些 MCP”
- 生成引导用户补 Skill / MCP 的提示词块
- 支持一键生成 draft Skill / draft MCP

这个能力很重要，因为它标志着系统开始从“记录 SOP”走向“理解 SOP 所需能力”。

## 4. 第三阶段：把执行链接起来，而不是停在建模层

如果系统只能导入 SOP，却不能继续推动任务执行，那它仍然只是一个静态管理工具。

所以后面我们继续往下打通：

- `Playbook -> Task DAG` 规划
- 任务依赖推进
- `Run` 创建
- `Supervisor / Worker Session`
- `waiting_human` 与审批联动
- `Reflection -> KnowledgeUpdate` 学习闭环

这一步的价值在于：

- Playbook 不再只是一个文档，而是可以衍生任务图
- 任务不再只是状态字段，而是真正参与执行推进
- 执行不再结束于“完成/失败”，而会进入复盘与知识沉淀

也就是从这一阶段开始，PlaybookOS 才真正像一个“工作操作系统”，而不是 SOP 管理器。

## 5. 第四阶段：前端从单页堆叠，重构成工作台系统

随着对象与主链越来越多，原始前端页面已经不够用了。

我们接着重审了整个 UI 方案，并做出一个非常关键的决定：

> 打开系统后，用户首先看到的应该是一个全局看板，而不是某个局部表单。

于是前端开始重构为：

- 首页：全局看板
- 左侧导航：工作台目录
- 设置页：独立治理入口

工作台逐步被拆成：

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
- 模型设置
- 全局设置
- 会话管理

之后我们又把首页逐步补成六块核心信息：

- 系统摘要
- 任务流程总览
- 关键阻塞
- 推荐动作
- 进行中任务
- 自动迭代动态

再往后，还补了：

- route-focused 页面摘要
- route detail 区块
- 全局范围筛选器
- 左侧导航数量徽标

这一轮重构的意义非常大：它让 PlaybookOS 不再像一个临时 demo，而更像一个真正的控制台系统。

## 6. 第五阶段：把“设置”从静态展示做成真实治理入口

前端重构后，我们发现一个问题：如果模型、全局行为、会话状态都不能在系统里真正配置，控制台仍然只是“好看”。

于是设置页被逐步做实，主要包括三块：

### 6.1 模型设置

我们新增了独立运行时设置层，把模型配置从“纯环境变量”升级为：

- 环境变量默认值
- 本地 JSON 覆盖
- provider presets
- 命名环境 profile
- 最近一次成功 probe

这使得模型设置真正具备了可治理能力，而不是只能改代码或改 shell 环境。

### 6.2 全局设置

全局设置开始负责：

- 默认语言
- 默认路由
- 默认筛选
- 自动刷新
- 环境标签

也就是说，系统开始具备环境级行为控制，而不是只处理对象数据。

### 6.3 会话管理

会话管理不再只是摘要，而是可以：

- 按 Goal / Run 过滤
- 修改 session 状态
- 编辑标题、objective、summary

这一步把“会话”从被动记录提升为可治理对象。

## 7. 第六阶段：从“人类看板”转向“Agent 也能操作的控制面”

这是整个项目里最重要的一次战略转向之一。

我们明确意识到：

> PlaybookOS 很可能不只是给人类看，而是会被 OpenClaw 这类外部 agent 当成控制面去使用。

这意味着系统不能只提供网页，而必须提供 agent-friendly 的接入面。

于是我们设计并落地了：

- `GET /api/agent/manifest`
- `GET /api/agent/context`
- `POST /api/agent/intake`
- `POST /api/agent/apply`
- `GET/POST/PUT /api/delegation-profiles*`
- `skills/playbookos-operator/`

这里的逻辑是：

1. 外部 agent 先读 `manifest`，理解系统对象、接口和推荐工作流
2. 再读 `context`，同步当前 blocked goals、draft skills、unhealthy MCP、waiting approvals 等上下文
3. 再把用户对话或 Markdown SOP 交给 `intake`，得到 dry-run 操作计划
4. 如果处于受托管模式，再结合 `delegation profile` 使用 `apply` 执行授权范围内的 builder 动作

这一步让外部 agent 不再需要“猜测内部 API”，而是能以受控方式真正操作系统。

## 8. 第七阶段：补可运行演示、补文档、补对外接入说明

当主链初步跑通后，我们开始集中处理另一个常见问题：

- 功能已经很多，但别人看不明白
- 文档有历史残留，和真实实现不完全一致
- 对外 agent 想接入时，缺乏最短路径

所以我们又做了几件很实际的事：

### 8.1 重新审计 README

我们把 README 从“实现清单式描述”重写成“项目说明文档”，并强调：

- 这个项目是什么
- 当前真实能力是什么
- 当前不是什么
- 如何快速启动
- 如何给 OpenClaw 这类 agent 接入
- 当前限制有哪些

之后，又按你的要求把说明文档拆成：

- `README.md`：完整中文
- `README-EN.md`：完整英文

避免同段中英混排带来的阅读负担。

### 8.2 新增可执行演示脚本

为了让 OpenClaw / 外部 agent 接入不只停留在文字层面，我们新增了：

- `scripts/openclaw_demo.sh`

它会自动执行：

`manifest -> context -> intake -> delegation profile -> apply`

并且从 intake 结果里动态提取推荐的 `operation_ids`，而不是把这些 id 写死在文档里。

这件事非常重要，因为它把“文档示例”升级成了“真正可执行的演示”。

## 9. 我们在这 24 小时里反复确认的几个方法论

在这轮构建过程中，有几条方法论被反复证明是正确的。

### 9.1 Runnable-first

不要一开始追求最完美的治理层，而要先让主链真的跑起来。

所以我们优先顺序一直是：

- 先让 SOP 能进系统
- 再让 Skill / MCP 缺口能识别
- 再让 Task / Run / Reflection 能形成闭环
- 再让人类和 agent 都能真正操作系统
- 最后再补细粒度治理、日志、回滚、巡检等增强能力

### 9.2 Markdown-first

不要过早扩展格式种类。

如果 Markdown 主链还不够稳，就没有必要急着承诺 PDF / Docx / 图片等复杂格式。先把最稳定的一条链做深，比表面上支持很多格式更有价值。

### 9.3 Agent-first interface

外部 agent 不应该直接推断内部 API，而应该：

`manifest -> context -> intake -> apply`

这不仅更稳，也更利于审计、授权和托管。

### 9.4 文档必须服从真实实现

我们中途多次停下来审 README、审交互、审文案，其实是在做一件很重要的事：

> 不让文档跑在代码前面。

这能显著减少用户误判，也能让后续迭代更可控。

## 10. 当前还没有完成的部分

到这一步，系统已经是一个可运行的 MVP，但仍然有不少明确缺口：

- 多格式 SOP 与多附件解析
- 完整 MCP runtime / credential / tool execution
- 更细粒度 agent identity 与 delegation policy
- `agent apply` 的事务回滚与更强治理
- 更完整的错误日志闭环与 issue 快捷提交
- 更深入的自动迭代与托管巡检机制
- 更细的对象详情页、跨页联动与 URL 分享态

这些内容并没有被忘记，而是已经被记录进：

- `docs/mvp-plan.md`
- `docs/agent-operator.md`
- `docs/records/iteration-memory.md`
- `docs/records/progress.md`

也就是说，这个系统已经从“一个想法”变成了“一条跑得通、还能继续长的工程主线”。

## 11. 最后的总结

如果要用一句话总结这次搭建过程，那就是：

> 我们并不是先设计一个完美系统，再去实现；而是围绕一条最有价值的主链，一边跑通，一边收敛，一边把系统从 demo 推进成控制面。

在这大约 `24h`、`2235` 次请求、`432M` Token 的连续迭代里，Codex 与 GPT-5.4 的角色并不是“自动生成一堆代码”，而更像是一个高频协作的工程搭档：

- 帮我们快速探索实现路径
- 持续重审产品策略
- 在文档、代码、前端、API 之间来回对齐
- 把“想法”尽快落成“可运行主链”

今天的 PlaybookOS 还不是终局，但它已经有了一个很重要的品质：

它不是停留在 PPT、PRD 或单页 demo 上，而是已经开始具备“被人类和 agent 共同使用”的真实工程形态。
