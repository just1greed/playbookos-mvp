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
- AI 参与完善：已有 reflection proposal、autopilot 与事件链路，但还没有针对 Skill / Task / SOP / 知识库的专门“AI co-pilot authoring”接口
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
