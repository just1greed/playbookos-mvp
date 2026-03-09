# PlaybookOS 迭代记忆

## 用户最初目标（长期北极星）

构建一个真正可工作的 AI Work OS，至少包括：

- 手动设置 SOP / Playbook
- 手动设置 Skill
- 手动设置 Task
- 全流程由 AI 参与辅助完善
- 能拆出子会话 / 子执行单元完成任务
- 有验收机制
- 有事后复盘
- 能反向优化 SOP / Skill / Playbook

## 当前完成度判断（2026-03-08）

### 已实现

- Goal / Playbook / Skill / Knowledge / Knowledge Update / Task / Session / Run / Acceptance / Artifact / Reflection / Event 的领域模型与持久化主链
- 手动导入 Playbook（SOP 的第一版承载）
- 手动创建 Task
- 手动创建 Skill，并可把 Skill 绑定到 Task
- Planner: Playbook -> Task DAG
- Orchestrator: dispatch / complete / waiting_human
- Supervisor: Goal 主控会话、Run 子会话、事件流、任务验收
- Executor: run 执行、trace、artifact metadata
- Reflection: reflect / evaluate / approve / publish
- 错误文件记录：`data/error_records.jsonl`
- 内置 Dashboard：首页可中英文切换，并可看到 playbooks / knowledge / sessions / acceptances / events
- 页面工作台已支持直接新建 Goal / SOP / Skill / Knowledge / Task
- 页面编辑器已支持查看并修改既有 Goal / SOP / Skill / Knowledge / Task
- 页面操作中心已支持 Goal 规划 / 派发 / 自动执行、Run 审批 / 执行、Task 验收、Knowledge Update apply/reject、Reflection evaluate/approve/reject/publish
- 页面已新增主控 / 子会话树，可按 Goal 看到 supervisor 与 worker 层级结构；当前可视化已支持递归树展示，但实际编排深度仍主要是一层 worker

### 部分实现

- SOP 手动设置：已具备页面内新建、基础编辑，以及专门的 patch review / publish 可视界面，但还缺少更细粒度 diff、逐条审阅和版本审批工作流
- AI 参与完善：已有 reflection proposal、autopilot、SOP ingestion、Skill suggestion 和第一版 Skill authoring wizard；但还没有覆盖 Task / SOP patch / 知识库的完整 AI co-pilot authoring 接口
- 验收：已有独立的 acceptance 实体、API 和页面内操作入口，但还没有更细的 checklist 模板、评分和批量验收 UI
- 知识库：已有 `KnowledgeBase` 实体、任务绑定、执行读取，以及 `KnowledgeUpdate` AI 回写提案链路和页面内 apply/reject，但还没有检索排序和版本化能力
- 子会话：当前已有 supervisor / worker session，可见且可追踪，但还没有更深层的 session tree / parallel sub-session orchestration

### 尚未完成

- Skill 版本晋级与回滚：已具备页面内专门版本中心和 create-version / activate / deprecate / rollback 动作，但还缺少更细粒度的评测门禁、审批策略和发布时间线
- 专门的 SOP 编辑 / diff / patch 审核界面
- 知识库检索排序与版本化能力
- 真正的多层子会话执行、并行汇总与主进程仲裁：已具备 dispatch wave 并行批次会话、worker 多层子会话和 supervisor arbitration 可视化摘要，但仍缺少更强的真实并发执行、跨波次资源竞争仲裁与真实在线 agent 执行器
- 真实 OpenAI Agents SDK 在线执行：已具备按当前环境配置发起 `responses` / `chat.completions` 请求的适配层与可见 request/response 检查器，但还缺少真实 MCP tool runtime 与更完整的在线评测
- Temporal 真正接入

## 推荐下一优先级

1. 多层子会话 / session tree / 并行汇总
2. SOP patch review / diff / publish UI
3. Skill versioning / rollback
4. 知识库检索排序 / 版本化
5. 真实 executor + MCP 集成

## 2026-03-09 设计回顾结论

- 当前系统已经具备“手工建模后的执行与反思闭环”，即手工创建 Goal / Playbook / Skill / Task 后，可以完成规划、调度、执行、验收与 reflection。
- 当前系统还不具备完整的“任意格式 SOP 上传 -> 自动解析成对象 -> 主动引导配置 Skill”前置建模链路。
- 缺的核心不是后半段执行，而是前半段的 `ingestion + compiler + skill recommendation + authoring wizard`。
- 因此后续实现顺序调整为：先补原始 SOP 接入与解析，再补 Skill 引导，再补原件/附件治理和更完整的 authoring workflow。
- 现在第一版原件治理也已补上：原始 SOP 文本会落入本地对象存储，并可从导入引导区直接回看原文。
- 当前最主要未完成项变为：Markdown SOP 之外的多格式与多附件解析、自动派生更多对象（Knowledge / Task template / checklist）、以及更强的问答式 Skill authoring 与发布门禁。
- 当前前置建模链的重点已经收敛到“提示词质量”：要先把从 SOP 识别工具、反推出 MCP、再引导用户上传 Skill 的 prompt 设计打磨稳定。
- 现在已补上 MCPServer 控制面注册表、CRUD 与从 SOP 缺口一键生成 draft MCP；当前前置建模链的下一个重点会从“有没有 MCP”转向“如何把 MCP 做成可校验、可连通、可治理的真实运行时能力”。
- 因此新的缺口排序变为：`MCP runtime / credential / health` > `Markdown 之外的多格式与附件解析` > `ingestion 自动物化更多对象` > `更强的引导式 authoring 与发布门禁`。

- 新的前端方向已经明确：默认首页改为全局看板，现有超长单页会被拆成左侧导航 + 页面级工作台；短期先做壳层和 IA，不急着继续堆功能卡片。
- 工作台一级节点已定为：目标、SOP、Skill、MCP、知识库、任务、会话、自动迭代、审批流、提示词；设置页定为：模型设置、全局设置、会话管理。

- 前端重构现在已从“只有全局壳层”进入“页面级工作台摘要”阶段：SOP / Skill / 审批流 / 提示词 已有 route focus 和按页资源过滤，但各工作台的专属列表、详情区和动作编排还没完全拆开。
- 当前前端还缺的核心板块主要是：全局看板上的阻塞区/推荐动作区、MCP/知识库/任务/会话/自动迭代/设置页的专属页面内容，以及更细的跨对象筛选与治理入口。

- 前端重构已进一步把工作台页面做出差异化：除了 `SOP / Skill / 审批流 / 提示词` 的 focus 摘要外，`MCP / 知识库 / 任务` 现在也有专属双栏内容区，页面不再只是共享表单与编辑器。
- 当前最主要未完成的前端板块，已经收敛到：全局看板上的阻塞区/推荐动作区、会话/自动迭代/设置页的专属页面内容，以及更细的跨对象筛选与联动。

- 全局看板已不再只是摘要卡 + 流程带：现在还具备面向运营的阻塞区和推荐动作区，能更直接地把用户引到审批、MCP、Skill、学习和任务处理节点。
- 当前前端剩余缺口进一步集中到：进行中任务区、自动迭代动态区、会话/自动迭代/设置页的专属内容，以及更细的全局筛选和跨对象联动。

- 前端工作台已经覆盖到会话、学习和设置页的第一版专属内容；当前页面还比较偏摘要和治理视角，但已经从“纯目录壳”进入“按页可读、可导航、可定位问题”的阶段。
- 现在最主要剩余缺口是：首页的进行中任务区与自动迭代动态区、更强的设置编辑能力，以及跨 Goal / SOP / 状态的筛选联动。

- 全局看板第一版信息架构已经基本闭合：不只是系统摘要和导航壳，还能直接看到阻塞、建议动作、进行中任务和学习动态。
- 当前前端剩余的主要缺口已经更偏交互增强：跨对象筛选联动、设置页可编辑能力、以及更细的页面内跳转/定位体验。

- 顶部范围栏现在已经开始承担真实的“全局筛选”职责，而不只是展示位；后续若继续增强，可以在这个基础上叠加 URL 状态、跨页记忆和更细粒度的组合筛选。
- 当前前端剩余缺口进一步收敛到：设置页可编辑能力、筛选结果的 URL/分享态、以及更细的对象详情跳转和页内联动体验。

- 设置页可编辑能力已经开始落地，而不再只是摘要展示：模型配置现在有独立运行时设置层，可由 UI 修改并立即影响 preview / API 的执行适配器。
- 当前前端剩余缺口因此进一步收敛到：`全局设置` 与 `会话管理` 的真实治理动作、设置页更细的连接测试/预设管理，以及筛选状态的 URL/分享态。

- 设置页现在不只是模型参数可配了：`全局设置` 已经开始控制 Dashboard 的默认语言、默认路由、默认筛选与自动刷新节奏。
- `会话管理` 也从纯摘要进入可治理阶段：当前已经能按 Goal / Run 检索并直接更新单个 session 的状态与摘要；下一阶段会转向批量治理动作。

- 模型设置已经从“能保存参数”推进到“能切 preset、能做连通性测试”的阶段；这意味着后续多环境 / 多网关切换会自然落在同一套设置框架里。
- 当前设置页剩余的模型侧缺口，已经更集中到：配置历史、多环境切换、以及针对常见 provider 的更细 preset 模板。

- 模型设置现在已经具备“当前配置 + provider preset + 命名环境 + 最近成功 probe”的四层状态，后续多环境治理基本可以沿着这条线继续长出来。
- 全局设置也开始承担“环境标识”职责，后续若做对象落盘策略、错误日志策略或环境级开关，会更自然地挂在这里。

- 设置页这轮已经从“可编辑”继续推进到“可治理”：模型设置不只是存参数，还能保存命名环境、切换环境，并保留最近一次成功探测结果作为回滚参考。
- 全局设置目前除了默认语言/路由/刷新外，也开始承载环境级元数据（`environment_label`）；后续如果扩展对象落盘、错误日志、feature flag，会自然继续挂在这里。
- 当前设置侧下一批更自然的缺口已经变成：profile 删除/导入导出、最近成功配置一键恢复、以及更细的 provider 模板与敏感信息治理。

- 这轮回顾后确认：之前 `README` 和部分 ingest 交互对外表达得比当前产品策略更宽，容易让用户误判“多格式 SOP 已正式支持”。现在已统一收敛到 Markdown-first。
- 当前更合理的演进方式不是继续扩展格式种类，而是先把 Markdown SOP 的“工具识别 -> MCP 缺口 -> Skill 上传/复用 -> 步骤绑定”这条引导链做得更稳定、更可操作。
- 因此本轮优化重点放在提示词与动作顺序：先复用已有 MCP/Skill，再补缺口，再做绑定和 authoring，而不是一上来默认新建所有对象。
