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

- Goal / Playbook / Task / Run / Artifact / Reflection 的领域模型与持久化主链
- 手动导入 Playbook（SOP 的第一版承载）
- 手动创建 Task
- 手动创建 Skill，并可把 Skill 绑定到 Task
- Planner: Playbook -> Task DAG
- Orchestrator: dispatch / complete / waiting_human
- Executor: run 执行、trace、artifact metadata
- Reflection: reflect / evaluate / approve / publish
- 错误文件记录：`data/error_records.jsonl`
- 内置 Dashboard：首页可中英文切换

### 部分实现

- SOP 手动设置：当前以 `Playbook import + compile` 表达，缺少真正可编辑的 SOP 工作台
- AI 参与完善：已有 reflection proposal 与 autopilot 骨架，但还没有针对 Skill / Task / SOP 的专门“AI co-pilot authoring”接口
- 验收：已有 review / human approval / publish gating，但没有独立的 acceptance checklist / sign-off 实体
- 子会话：当前只有 `Run.session_id` 字段和 Task DAG / parent_task_id 能力，还没有显式的 session tree / sub-session orchestration

### 尚未完成

- Skill 版本晋级与回滚流水线
- 专门的 SOP 编辑 / diff / patch 审核界面
- 验收记录、验收人、验收标准的独立模型与 API
- 真正的多子会话执行与汇总
- 真实 OpenAI Agents SDK + MCP 在线执行
- Temporal 真正接入

## 推荐下一优先级

1. Acceptance / Sign-off 模块
2. 子会话 / session tree 模块
3. SOP patch review / diff / publish UI
4. Skill versioning / rollback
5. 真实 executor + MCP 集成
