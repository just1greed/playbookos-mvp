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

### 部分实现

- SOP 手动设置：已具备页面内新建与基础编辑，但还缺少 diff / patch / 版本审批 UI
- AI 参与完善：已有 reflection proposal、autopilot 与事件链路，但还没有针对 Skill / Task / SOP / 知识库的专门“AI co-pilot authoring”接口
- 验收：已有独立的 acceptance 实体、API 和页面内操作入口，但还没有更细的 checklist 模板、评分和批量验收 UI
- 知识库：已有 `KnowledgeBase` 实体、任务绑定、执行读取，以及 `KnowledgeUpdate` AI 回写提案链路和页面内 apply/reject，但还没有检索排序和版本化能力
- 子会话：当前已有 supervisor / worker session，可见且可追踪，但还没有更深层的 session tree / parallel sub-session orchestration

### 尚未完成

- Skill 版本晋级与回滚流水线
- 专门的 SOP 编辑 / diff / patch 审核界面
- 知识库检索排序与版本化能力
- 真正的多层子会话执行、并行汇总与主进程仲裁
- 真实 OpenAI Agents SDK + MCP 在线执行
- Temporal 真正接入

## 推荐下一优先级

1. 多层子会话 / session tree / 并行汇总
2. SOP patch review / diff / publish UI
3. Skill versioning / rollback
4. 知识库检索排序 / 版本化
5. 真实 executor + MCP 集成
