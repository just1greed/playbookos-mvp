from __future__ import annotations

import html
import json


SECTION_ORDER = [
    "goals",
    "playbooks",
    "skills",
    "mcp_servers",
    "knowledge_bases",
    "knowledge_updates",
    "tasks",
    "sessions",
    "runs",
    "acceptances",
    "artifacts",
    "reflections",
    "events",
]

TRANSLATIONS = {
    "zh": {
        "html_lang": "zh-CN",
        "page_title": "PlaybookOS 控制台",
        "badge": "✦ PlaybookOS · AI 工作操作系统",
        "hero_title": "用一个可视化控制台，追踪 SOP / Skill / Knowledge / Task / Session / Acceptance / Reflection 的闭环。",
        "hero_body": "这个页面直接消费 PlaybookOS 控制面 API，展示 SOP、技能、知识库、任务、子会话、验收、反思与事件流，让用户看见 AI 工作系统的完整主链路。",
        "refresh_board": "刷新看板",
        "view_board_json": "查看原始 Board JSON",
        "live_data_source": "实时数据源",
        "total_resources": "总资源数",
        "total_resources_desc": "Goals、Playbooks、Skills、MCP Servers、Knowledge、Knowledge Updates、Tasks、Sessions、Runs、Acceptances、Artifacts、Reflections、Events 总量",
        "blocked_signals": "阻塞信号",
        "blocked_signals_desc": "Blocked goals + waiting human runs",
        "learning_signals": "学习信号",
        "learning_signals_desc": "Acceptances、Reflections 与已发布优化路径",
        "control_board": "控制看板",
        "control_board_subtitle": "来自 /api/board 的实时状态分布",
        "api_entry_points": "API 入口",
        "api_entry_subtitle": "适合手动巡检，也适合自动化编排接入",
        "action_center": "操作中心",
        "action_center_subtitle": "把规划、审批、验收、复盘与知识回写直接放到用户可见界面中",
        "action_status_ready": "操作中心已就绪。",
        "goal_ops_title": "目标编排",
        "goal_ops_empty": "还没有可操作的 Goal。",
        "review_ops_title": "人工审批 / 验收",
        "review_ops_empty": "当前没有待审批或待验收项。",
        "learning_ops_title": "复盘 / 知识更新",
        "learning_ops_empty": "当前没有待处理的知识更新或反思提案。",
        "session_tree_title": "主控 / 子会话树",
        "session_tree_subtitle": "按 Goal 展示 supervisor 与 worker 的层级结构，帮助你看见主进程如何调度子会话",
        "session_tree_empty": "当前还没有会话树数据。",
        "session_goal_summary": "目标会话概览",
        "session_children_count": "子会话数",
        "session_kind_label": "会话类型",
        "session_status_label": "状态",
        "session_task_label": "任务",
        "session_run_label": "运行",
        "session_summary_label": "摘要",
        "session_role_label": "会话角色",
        "supervisor_center_title": "主控聚合中心",
        "supervisor_center_subtitle": "主进程按 Goal 汇总子会话、Run、验收、复盘、知识更新与事件，帮助你看见编排是否闭环",
        "supervisor_center_empty": "当前还没有主控聚合数据。",
        "supervisor_center_sessions": "会话链路",
        "supervisor_center_runs": "运行结果",
        "supervisor_center_learning": "学习闭环",
        "supervisor_center_events": "最新事件",
        "supervisor_center_arbitration": "主控仲裁",
        "supervisor_center_recommendations": "建议动作",
        "supervisor_center_waves": "并行波次",
        "supervisor_center_waiting": "待人工",
        "supervisor_center_closed_tasks": "已关闭任务",
        "patch_review_title": "SOP 补丁审阅",
        "patch_review_subtitle": "集中查看反思提案、变更操作、评测结果与发布状态，专门服务 SOP 优化闭环",
        "patch_review_empty": "当前还没有 SOP 补丁提案。",
        "patch_review_source_run": "来源 Run",
        "patch_review_target_playbook": "目标 SOP",
        "patch_review_target_version": "目标版本",
        "patch_review_score": "评测分数",
        "patch_review_replay_count": "回放样本数",
        "patch_review_changes": "变更清单",
        "patch_review_no_changes": "当前提案没有结构化变更项。",
        "skill_version_title": "技能版本中心",
        "skill_version_subtitle": "集中展示 Skill 版本链、激活版本、回滚目标与发布动作，补齐技能迭代闭环",
        "skill_version_empty": "当前还没有 Skill 版本链。",
        "skill_version_family": "技能家族",
        "skill_version_current": "当前版本",
        "skill_version_rollback": "回滚目标",
        "skill_version_servers": "依赖 MCP",
        "action_create_skill_version": "创建新版本",
        "action_apply_authoring_pack": "应用配置建议",
        "action_open_editor": "打开编辑器",
        "action_activate_skill": "激活版本",
        "action_deprecate_skill": "废弃版本",
        "action_rollback_skill": "回滚版本",
        "action_plan": "规划",
        "action_dispatch": "派发",
        "action_autopilot": "自动执行",
        "action_execute": "执行 Run",
        "action_approve_run": "批准 Run",
        "action_reject_run": "拒绝 Run",
        "action_accept_task": "通过验收",
        "action_reject_task": "打回任务",
        "action_apply_knowledge": "应用知识",
        "action_reject_knowledge": "拒绝知识",
        "action_evaluate_reflection": "评测提案",
        "action_approve_reflection": "批准提案",
        "action_reject_reflection": "拒绝提案",
        "action_publish_reflection": "发布 SOP",
        "action_status_running": "操作执行中…",
        "action_status_success": "操作完成，已刷新全局状态。",
        "action_status_error": "操作失败",
        "action_kind_goal": "目标",
        "action_kind_run": "运行",
        "action_kind_task": "任务",
        "action_kind_knowledge": "知识更新",
        "action_kind_reflection": "反思",
        "workbench_title": "配置工作台",
        "workbench_subtitle": "直接在页面中手动配置 Goal、SOP、Skill、Knowledge 和 Task。",
        "workbench_status_ready": "工作台就绪，可直接提交。",
        "workbench_status_success": "创建成功，已刷新资源。",
        "workbench_status_error": "提交失败",
        "authoring_wizard_title": "Skill Authoring Wizard",
        "authoring_wizard_subtitle": "为 draft Skill 快速补齐 schema、审批策略与评测策略。",
        "authoring_wizard_empty": "当前没有待完善的 draft Skill。",
        "authoring_wizard_checklist": "推荐检查清单",
        "authoring_wizard_signals": "风险信号",
        "authoring_wizard_notes": "建议说明",
        "authoring_wizard_playbook": "关联 SOP",
        "execution_inspector_title": "执行检查器",
        "execution_inspector_subtitle": "展示 Run 的真实 API 请求格式、工具调用记录、配置摘要与返回结果，方便你审计 AI 执行细节",
        "execution_inspector_empty": "当前还没有可检查的执行记录。",
        "execution_inspector_calls": "调用记录",
        "execution_inspector_request": "请求载荷",
        "execution_inspector_response": "执行结果",
        "quick_resource_peek": "资源速览",
        "quick_resource_peek_subtitle": "从 API 抓取最近的实体样本",
        "loading_resources_title": "等待加载资源",
        "loading_resources_body": "页面会自动抓取 goals / playbooks / skills / mcp_servers / knowledge_bases / knowledge_updates / tasks / sessions / runs / acceptances / reflections / artifacts / events。",
        "operating_rhythm": "运行节奏",
        "operating_rhythm_subtitle": "当前 MVP 推荐的执行循环",
        "timeline_1": "用户先配置 Goal / SOP / Skill / Knowledge / Task，系统再把 SOP 规划成可执行任务图。",
        "timeline_2": "主控会话调度子会话执行任务，沉淀 run、artifact 与 event 事件轨迹。",
        "timeline_3": "结果经过人工验收与 AI 复盘，再回写 SOP、技能与知识沉淀。",
        "snapshot_json": "快照 JSON",
        "snapshot_json_subtitle": "适合排查 UI 与数据不一致问题",
        "footer": "PlaybookOS MVP · 单文件控制台 · 无外部前端依赖",
        "nav_group_overview": "总览",
        "nav_group_workbench": "工作台",
        "nav_group_settings": "设置",
        "nav_group_system": "系统",
        "nav_dashboard": "全局看板",
        "nav_goals": "目标",
        "nav_playbooks": "SOP",
        "nav_skills": "Skill",
        "nav_mcp": "MCP",
        "nav_knowledge": "知识库",
        "nav_tasks": "任务",
        "nav_sessions": "会话",
        "nav_learning": "自动迭代",
        "nav_approvals": "审批流",
        "nav_prompts": "提示词",
        "nav_model_settings": "模型设置",
        "nav_global_settings": "全局设置",
        "nav_session_admin": "会话管理",
        "nav_api_health": "API 健康",
        "nav_errors": "错误记录",
        "nav_versions": "版本信息",
        "page_dashboard_title": "全局看板",
        "page_dashboard_subtitle": "先看系统健康度、流程进度和阻塞点，再进入具体工作台处理对象。",
        "page_goals_title": "目标工作台",
        "page_goals_subtitle": "管理业务目标、推进节奏和目标级执行闭环。",
        "page_playbooks_title": "SOP 工作台",
        "page_playbooks_subtitle": "从 Markdown SOP 到 Playbook、工具识别、补丁审阅与执行入口。",
        "page_skills_title": "Skill 工作台",
        "page_skills_subtitle": "管理技能草稿、版本演进、依赖 MCP 与发布策略。",
        "page_mcp_title": "MCP 工作台",
        "page_mcp_subtitle": "管理 MCP 注册表、草稿接入、依赖关系和后续运行时治理。",
        "page_knowledge_title": "知识库工作台",
        "page_knowledge_subtitle": "管理知识沉淀、更新提案与任务执行上下文。",
        "page_tasks_title": "任务工作台",
        "page_tasks_subtitle": "查看任务图、执行状态、阻塞依赖和任务级动作。",
        "page_sessions_title": "会话工作台",
        "page_sessions_subtitle": "追踪主控会话、子会话树和执行上下文流转。",
        "page_learning_title": "自动迭代工作台",
        "page_learning_subtitle": "管理反思提案、知识回写、补丁发布和学习闭环。",
        "page_approvals_title": "审批流工作台",
        "page_approvals_subtitle": "集中处理等待人工确认、验收、批准与拒绝的关键节点。",
        "page_prompts_title": "提示词工作台",
        "page_prompts_subtitle": "查看系统关键提示词、用途、输入上下文和后续调优入口。",
        "page_model_settings_title": "模型设置",
        "page_model_settings_subtitle": "管理当前 AI 模型、接口格式和调用参数。",
        "page_global_settings_title": "全局设置",
        "page_global_settings_subtitle": "管理控制台默认行为、显示偏好和系统级参数。",
        "page_session_admin_title": "会话管理",
        "page_session_admin_subtitle": "查看会话资源、异常状态和后续治理入口。",
        "page_system_title": "系统信息",
        "page_system_subtitle": "查看 API 健康、错误记录和版本信息。",
        "topbar_scope_label": "全局范围",
        "topbar_scope_all": "全部 Goal",
        "topbar_scope_goal": "按 Goal",
        "topbar_scope_playbook": "按 SOP",
        "topbar_scope_status": "按状态",
        "global_flow_title": "任务流程总览",
        "global_flow_subtitle": "从 Goal 到 Knowledge 的全局链路状态，一眼看清哪里在推进、哪里在阻塞。",
        "route_focus_title": "重点摘要",
        "route_focus_subtitle": "围绕当前工作台节点，先看最重要的对象状态、缺口和待处理项。",
        "focus_total": "总量",
        "focus_pending": "待处理",
        "focus_issues": "问题",
        "focus_latest": "最新",
        "focus_missing_mcp": "缺失 MCP",
        "focus_suggested_skills": "建议 Skill",
        "focus_draft": "草稿",
        "focus_active": "激活",
        "focus_dependencies": "依赖",
        "focus_waiting": "等待人工",
        "focus_proposed": "待批准",
        "focus_review": "待复核",
        "route_placeholder_title": "该页面正在迁移",
        "route_placeholder_body": "这一页的导航壳和信息架构已经就位，下一阶段会把现有模块逐步迁移到这里。",
        "settings_model_card": "模型配置会集中展示 provider、model、base url、timeout 和输出参数。",
        "settings_global_card": "全局设置会管理语言、刷新频率、对象存储路径和实验性开关。",
        "settings_session_card": "会话管理会展示 supervisor / worker session 总量、异常状态与治理动作。",
        "tracked_items": "个跟踪对象",
        "overview_suffix": "概览",
        "last_updated": "最近刷新",
        "api_prefix": "接口",
        "api_card_body": "可直接打开这个资源接口，也可以把它接入你的自动化工具与操作流。",
        "idle": "空闲",
        "booting": "启动中",
        "error": "错误",
        "offline": "离线",
        "loading_failed_title": "加载失败",
        "api_unavailable_title": "API 暂不可达",
        "resource_empty_suffix": "暂无记录",
        "resource_empty_body": "接口当前返回空列表。",
        "resource_id_fallback": "无 ID",
        "create_goal": "新建 Goal",
        "ingest_playbook": "导入原始 SOP",
        "create_playbook": "新建 SOP",
        "create_skill": "新建 Skill",
        "create_mcp_server": "新建 MCP",
        "create_knowledge": "新建 Knowledge",
        "create_task": "新建 Task",
        "goal_title": "目标标题",
        "goal_objective": "目标说明",
        "goal_constraints": "约束（每行一条）",
        "goal_definition_of_done": "完成定义（每行一条）",
        "playbook_name": "SOP 名称",
        "playbook_goal": "关联 Goal",
        "playbook_source_uri": "来源 URI（可选）",
        "playbook_steps": "步骤（每行一步）",
        "playbook_mcp_servers": "MCP 服务器（每行一条）",
        "ingest_source_text": "SOP 原文",
        "ingest_source_file": "文本文件（可选）",
        "ingest_source_kind": "原始格式",
        "ingest_guidance_title": "Skill 配置引导",
        "ingest_guidance_empty": "导入 SOP 后，这里会显示推荐 Skill 与解析摘要。",
        "ingest_source_saved": "原始 SOP 已保存",
        "ingest_source_view": "查看原文",
        "ingest_tooling_summary": "工具与上传引导",
        "ingest_tooling_required_mcp": "需要补齐的 MCP",
        "ingest_tooling_existing_skills": "可复用 Skill",
        "ingest_tooling_existing_mcp": "已登记 MCP",
        "action_create_mcp_draft": "创建 MCP Draft",
        "ingest_tooling_actions": "下一步动作",
        "ingest_tooling_prompts": "推荐提示词",
        "action_ingest_playbook": "解析并导入",
        "action_create_skill_draft": "创建 Draft Skill",
        "action_create_bound_skill_draft": "创建并绑定步骤",
        "action_kind_playbook": "SOP",
        "skill_name": "Skill 名称",
        "skill_description": "Skill 说明",
        "skill_required_mcp_servers": "依赖 MCP（每行一条）",
        "mcp_server_name": "MCP 名称",
        "mcp_server_transport": "传输方式",
        "mcp_server_endpoint": "服务端点",
        "mcp_server_scopes": "权限范围（每行一条）",
        "knowledge_name": "知识条目名称",
        "knowledge_description": "知识摘要",
        "knowledge_content": "知识正文",
        "knowledge_tags": "标签（每行一条）",
        "knowledge_goal": "关联 Goal",
        "task_name": "任务名称",
        "task_description": "任务说明",
        "task_goal": "所属 Goal",
        "task_playbook": "所属 SOP",
        "task_skill": "执行 Skill（可选）",
        "task_knowledge": "关联知识库 ID（每行一条，可选）",
        "task_queue": "队列名",
        "task_priority": "优先级",
        "task_approval_required": "需要人工审批",
        "task_depends_on_ids": "依赖 Task ID（每行一条，可选）",
        "submit_create": "创建",
        "optional_none": "无",
        "input_placeholder_uri": "例如 file:///workspace/sop.md",
        "editor_title": "实体详情 / 编辑器",
        "editor_subtitle": "选择已有 Goal、SOP、Skill、Knowledge 或 Task，查看详情并直接编辑。",
        "editor_status_ready": "编辑器已就绪。",
        "editor_resource_type": "资源类型",
        "editor_resource_id": "实体",
        "editor_payload": "可编辑 JSON",
        "editor_meta": "实体详情",
        "editor_load": "载入",
        "editor_save": "保存修改",
        "editor_reset": "重置",
        "boot_error_title": "前端启动失败",
        "boot_error_body": "页面脚本发生错误，详情如下。",
        "section_labels": {
            "goals": "目标",
            "playbooks": "SOP",
            "skills": "技能",
            "mcp_servers": "MCP",
            "knowledge_bases": "知识库",
            "knowledge_updates": "知识更新",
            "tasks": "任务",
            "sessions": "会话",
            "runs": "运行",
            "acceptances": "验收",
            "artifacts": "产物",
            "reflections": "反思",
            "events": "事件",
        },
    },
    "en": {
        "html_lang": "en",
        "page_title": "PlaybookOS Console",
        "badge": "✦ PlaybookOS · AI Work Operating System",
        "hero_title": "Track the full SOP / Skill / Knowledge / Task / Session / Acceptance / Reflection loop in one visual console.",
        "hero_body": "This page reads directly from the PlaybookOS control-plane API and exposes SOPs, skills, knowledge bases, tasks, child sessions, acceptances, reflections, and event streams so the full AI work system stays visible to the user.",
        "refresh_board": "Refresh Board",
        "view_board_json": "Open Raw Board JSON",
        "live_data_source": "Live Data Source",
        "total_resources": "Total Resources",
        "total_resources_desc": "Total goals, playbooks, skills, knowledge bases, knowledge updates, tasks, sessions, runs, acceptances, artifacts, reflections, and events",
        "blocked_signals": "Blocked Signals",
        "blocked_signals_desc": "Blocked goals + waiting human runs",
        "learning_signals": "Learning Signals",
        "learning_signals_desc": "Acceptances, reflections, and published improvement paths",
        "control_board": "Control Board",
        "control_board_subtitle": "Live status distribution from /api/board",
        "api_entry_points": "API Entry Points",
        "api_entry_subtitle": "Useful for manual inspection and automation workflows",
        "action_center": "Action Center",
        "action_center_subtitle": "Put planning, approvals, acceptance, postmortems, and knowledge updates into a visible user-facing loop",
        "action_status_ready": "Action center is ready.",
        "goal_ops_title": "Goal Orchestration",
        "goal_ops_empty": "No actionable goals yet.",
        "review_ops_title": "Human Review / Acceptance",
        "review_ops_empty": "No pending approval or acceptance items.",
        "learning_ops_title": "Postmortem / Knowledge Updates",
        "learning_ops_empty": "No pending knowledge updates or reflection proposals.",
        "session_tree_title": "Supervisor / Worker Tree",
        "session_tree_subtitle": "Show supervisor and worker session hierarchy by goal so the main process stays visible",
        "session_tree_empty": "No session tree data yet.",
        "session_goal_summary": "Goal session overview",
        "session_children_count": "Child sessions",
        "session_kind_label": "Session kind",
        "session_status_label": "Status",
        "session_task_label": "Task",
        "session_run_label": "Run",
        "session_summary_label": "Summary",
        "session_role_label": "Session role",
        "supervisor_center_title": "Supervisor Aggregation Center",
        "supervisor_center_subtitle": "The main process aggregates child sessions, runs, acceptance, reflection, knowledge updates, and events by goal so orchestration stays visible.",
        "supervisor_center_empty": "No supervisor aggregation data yet.",
        "supervisor_center_sessions": "Session Flow",
        "supervisor_center_runs": "Run Outcomes",
        "supervisor_center_learning": "Learning Loop",
        "supervisor_center_events": "Latest Events",
        "supervisor_center_arbitration": "Supervisor Arbitration",
        "supervisor_center_recommendations": "Recommended Actions",
        "supervisor_center_waves": "Parallel Waves",
        "supervisor_center_waiting": "Waiting Human",
        "supervisor_center_closed_tasks": "Closed Tasks",
        "patch_review_title": "SOP Patch Review",
        "patch_review_subtitle": "Review reflection proposals, structured changes, evaluation results, and publish status in one dedicated SOP optimization surface",
        "patch_review_empty": "No SOP patch proposals yet.",
        "patch_review_source_run": "Source run",
        "patch_review_target_playbook": "Target SOP",
        "patch_review_target_version": "Target version",
        "patch_review_score": "Evaluation score",
        "patch_review_replay_count": "Replay samples",
        "patch_review_changes": "Change list",
        "patch_review_no_changes": "No structured changes in this proposal yet.",
        "skill_version_title": "Skill Version Center",
        "skill_version_subtitle": "Show Skill version chains, active releases, rollback targets, and lifecycle actions in one visible surface",
        "skill_version_empty": "No skill version chains yet.",
        "skill_version_family": "Skill family",
        "skill_version_current": "Current version",
        "skill_version_rollback": "Rollback target",
        "skill_version_servers": "Required MCP",
        "action_create_skill_version": "Create Version",
        "action_apply_authoring_pack": "Apply Pack",
        "action_open_editor": "Open Editor",
        "action_activate_skill": "Activate",
        "action_deprecate_skill": "Deprecate",
        "action_rollback_skill": "Rollback",
        "action_plan": "Plan",
        "action_dispatch": "Dispatch",
        "action_autopilot": "Autopilot",
        "action_execute": "Execute Run",
        "action_approve_run": "Approve Run",
        "action_reject_run": "Reject Run",
        "action_accept_task": "Accept Task",
        "action_reject_task": "Reject Task",
        "action_apply_knowledge": "Apply Knowledge",
        "action_reject_knowledge": "Reject Knowledge",
        "action_evaluate_reflection": "Evaluate",
        "action_approve_reflection": "Approve",
        "action_reject_reflection": "Reject",
        "action_publish_reflection": "Publish SOP",
        "action_status_running": "Running action…",
        "action_status_success": "Action completed and state refreshed.",
        "action_status_error": "Action failed",
        "action_kind_goal": "Goal",
        "action_kind_run": "Run",
        "action_kind_task": "Task",
        "action_kind_knowledge": "Knowledge Update",
        "action_kind_reflection": "Reflection",
        "workbench_title": "Workbench",
        "workbench_subtitle": "Configure goals, SOPs, skills, knowledge, and tasks directly in the page.",
        "workbench_status_ready": "Workbench is ready for input.",
        "workbench_status_success": "Created successfully and refreshed.",
        "workbench_status_error": "Submit failed",
        "authoring_wizard_title": "Skill Authoring Wizard",
        "authoring_wizard_subtitle": "Fill draft skills with schemas, approval defaults, and evaluation guidance in one step.",
        "authoring_wizard_empty": "There are no draft skills waiting for authoring guidance.",
        "authoring_wizard_checklist": "Recommended Checklist",
        "authoring_wizard_signals": "Risk Signals",
        "authoring_wizard_notes": "Guidance Notes",
        "authoring_wizard_playbook": "Linked SOP",
        "execution_inspector_title": "Execution Inspector",
        "execution_inspector_subtitle": "Show real API request formats, tool call records, config summaries, and response payloads for each run.",
        "execution_inspector_empty": "No execution records to inspect yet.",
        "execution_inspector_calls": "Call Records",
        "execution_inspector_request": "Request Payload",
        "execution_inspector_response": "Execution Result",
        "quick_resource_peek": "Quick Resource Peek",
        "quick_resource_peek_subtitle": "Recent entity samples fetched from the API",
        "loading_resources_title": "Waiting for resources",
        "loading_resources_body": "The page will automatically fetch goals / playbooks / skills / mcp_servers / knowledge_bases / knowledge_updates / tasks / sessions / runs / acceptances / reflections / artifacts / events.",
        "operating_rhythm": "Operating Rhythm",
        "operating_rhythm_subtitle": "Recommended workflow loop for the current MVP",
        "timeline_1": "Users configure goals, SOPs, skills, knowledge, and tasks first; the system turns SOPs into executable task graphs.",
        "timeline_2": "A supervisor session spawns worker sessions, executes runs, and records artifacts plus event traces.",
        "timeline_3": "Results go through human acceptance and AI postmortems before SOP, skill, and knowledge updates are published.",
        "snapshot_json": "Snapshot JSON",
        "snapshot_json_subtitle": "Useful for debugging mismatches between UI and data",
        "footer": "PlaybookOS MVP · single-file dashboard · no external frontend dependencies",
        "nav_group_overview": "Overview",
        "nav_group_workbench": "Workbenches",
        "nav_group_settings": "Settings",
        "nav_group_system": "System",
        "nav_dashboard": "Global Board",
        "nav_goals": "Goals",
        "nav_playbooks": "SOP",
        "nav_skills": "Skills",
        "nav_mcp": "MCP",
        "nav_knowledge": "Knowledge",
        "nav_tasks": "Tasks",
        "nav_sessions": "Sessions",
        "nav_learning": "Autopilot",
        "nav_approvals": "Approvals",
        "nav_prompts": "Prompts",
        "nav_model_settings": "Model Settings",
        "nav_global_settings": "Global Settings",
        "nav_session_admin": "Session Admin",
        "nav_api_health": "API Health",
        "nav_errors": "Error Log",
        "nav_versions": "Version Info",
        "page_dashboard_title": "Global Board",
        "page_dashboard_subtitle": "See system health, flow progress, and blockers first, then jump into the right workbench.",
        "page_goals_title": "Goals Workbench",
        "page_goals_subtitle": "Manage business goals, delivery rhythm, and goal-level execution loops.",
        "page_playbooks_title": "SOP Workbench",
        "page_playbooks_subtitle": "From Markdown SOP to Playbook, tool discovery, patch review, and execution entrypoints.",
        "page_skills_title": "Skills Workbench",
        "page_skills_subtitle": "Manage draft skills, version evolution, MCP dependencies, and release strategy.",
        "page_mcp_title": "MCP Workbench",
        "page_mcp_subtitle": "Manage the MCP registry, draft onboarding, dependencies, and future runtime governance.",
        "page_knowledge_title": "Knowledge Workbench",
        "page_knowledge_subtitle": "Manage knowledge entries, update proposals, and execution context.",
        "page_tasks_title": "Tasks Workbench",
        "page_tasks_subtitle": "Inspect task graphs, execution states, blockers, and task-level actions.",
        "page_sessions_title": "Sessions Workbench",
        "page_sessions_subtitle": "Trace supervisor sessions, worker trees, and execution context flow.",
        "page_learning_title": "Autopilot Workbench",
        "page_learning_subtitle": "Manage reflections, knowledge write-backs, patch releases, and the learning loop.",
        "page_approvals_title": "Approvals Workbench",
        "page_approvals_subtitle": "Handle waiting human approvals, acceptance, and critical review gates in one place.",
        "page_prompts_title": "Prompts Workbench",
        "page_prompts_subtitle": "Inspect key system prompts, their purpose, input context, and future tuning entrypoints.",
        "page_model_settings_title": "Model Settings",
        "page_model_settings_subtitle": "Manage the current AI model, API format, and invocation parameters.",
        "page_global_settings_title": "Global Settings",
        "page_global_settings_subtitle": "Manage console defaults, display preferences, and system-level parameters.",
        "page_session_admin_title": "Session Admin",
        "page_session_admin_subtitle": "Inspect session resources, abnormal states, and follow-up governance actions.",
        "page_system_title": "System",
        "page_system_subtitle": "Inspect API health, error logs, and version metadata.",
        "topbar_scope_label": "Global Scope",
        "topbar_scope_all": "All Goals",
        "topbar_scope_goal": "By Goal",
        "topbar_scope_playbook": "By SOP",
        "topbar_scope_status": "By Status",
        "global_flow_title": "Flow Overview",
        "global_flow_subtitle": "A global chain from Goal to Knowledge so you can instantly see what is moving and what is blocked.",
        "route_focus_title": "Key Highlights",
        "route_focus_subtitle": "See the most important states, gaps, and pending work for the current workbench first.",
        "focus_total": "Total",
        "focus_pending": "Pending",
        "focus_issues": "Issues",
        "focus_latest": "Latest",
        "focus_missing_mcp": "Missing MCP",
        "focus_suggested_skills": "Suggested Skills",
        "focus_draft": "Draft",
        "focus_active": "Active",
        "focus_dependencies": "Dependencies",
        "focus_waiting": "Waiting Human",
        "focus_proposed": "Proposed",
        "focus_review": "In Review",
        "route_placeholder_title": "This page is being migrated",
        "route_placeholder_body": "The navigation shell and information architecture are ready; existing modules will move here step by step in the next phase.",
        "settings_model_card": "Model settings will surface provider, model, base URL, timeout, and output parameters.",
        "settings_global_card": "Global settings will manage language, refresh cadence, object-store paths, and experimental toggles.",
        "settings_session_card": "Session admin will show supervisor / worker totals, abnormal states, and governance actions.",
        "tracked_items": "tracked items",
        "overview_suffix": "overview",
        "last_updated": "Last updated",
        "api_prefix": "API",
        "api_card_body": "Open the resource endpoint directly or connect it to your automation workflow.",
        "idle": "Idle",
        "booting": "Booting",
        "error": "Error",
        "offline": "Offline",
        "loading_failed_title": "Loading failed",
        "api_unavailable_title": "API unavailable",
        "resource_empty_suffix": "no records",
        "resource_empty_body": "The endpoint currently returns an empty list.",
        "resource_id_fallback": "No ID",
        "create_goal": "Create Goal",
        "ingest_playbook": "Ingest Raw SOP",
        "create_playbook": "Create SOP",
        "create_skill": "Create Skill",
        "create_mcp_server": "Create MCP",
        "create_knowledge": "Create Knowledge",
        "create_task": "Create Task",
        "goal_title": "Goal title",
        "goal_objective": "Goal objective",
        "goal_constraints": "Constraints (one per line)",
        "goal_definition_of_done": "Definition of done (one per line)",
        "playbook_name": "SOP name",
        "playbook_goal": "Linked goal",
        "playbook_source_uri": "Source URI (optional)",
        "playbook_steps": "Steps (one per line)",
        "playbook_mcp_servers": "MCP servers (one per line)",
        "ingest_source_text": "Raw SOP text",
        "ingest_source_file": "Text file (optional)",
        "ingest_source_kind": "Source format",
        "ingest_guidance_title": "Skill setup guidance",
        "ingest_guidance_empty": "After ingesting an SOP, recommended skills and parsing notes appear here.",
        "ingest_source_saved": "Raw SOP saved",
        "ingest_source_view": "View source",
        "ingest_tooling_summary": "Tooling and upload guidance",
        "ingest_tooling_required_mcp": "Required MCP",
        "ingest_tooling_existing_skills": "Reusable Skills",
        "ingest_tooling_existing_mcp": "Registered MCP",
        "action_create_mcp_draft": "Create MCP Draft",
        "ingest_tooling_actions": "Next actions",
        "ingest_tooling_prompts": "Recommended prompts",
        "action_ingest_playbook": "Parse and ingest",
        "action_create_skill_draft": "Create Draft Skill",
        "action_create_bound_skill_draft": "Create + Bind Steps",
        "action_kind_playbook": "SOP",
        "skill_name": "Skill name",
        "skill_description": "Skill description",
        "skill_required_mcp_servers": "Required MCP servers (one per line)",
        "mcp_server_name": "MCP name",
        "mcp_server_transport": "Transport",
        "mcp_server_endpoint": "Endpoint",
        "mcp_server_scopes": "Scopes (one per line)",
        "knowledge_name": "Knowledge item name",
        "knowledge_description": "Knowledge summary",
        "knowledge_content": "Knowledge content",
        "knowledge_tags": "Tags (one per line)",
        "knowledge_goal": "Linked goal",
        "task_name": "Task name",
        "task_description": "Task description",
        "task_goal": "Goal",
        "task_playbook": "SOP",
        "task_skill": "Skill (optional)",
        "task_knowledge": "Knowledge base IDs (one per line, optional)",
        "task_queue": "Queue name",
        "task_priority": "Priority",
        "task_approval_required": "Requires human approval",
        "task_depends_on_ids": "Depends on task IDs (one per line, optional)",
        "submit_create": "Create",
        "optional_none": "None",
        "input_placeholder_uri": "For example file:///workspace/sop.md",
        "editor_title": "Entity Detail / Editor",
        "editor_subtitle": "Choose an existing goal, SOP, skill, knowledge item, or task to inspect and edit.",
        "editor_status_ready": "Editor is ready.",
        "editor_resource_type": "Resource type",
        "editor_resource_id": "Entity",
        "editor_payload": "Editable JSON",
        "editor_meta": "Entity details",
        "editor_load": "Load",
        "editor_save": "Save changes",
        "editor_reset": "Reset",
        "boot_error_title": "Frontend boot failed",
        "boot_error_body": "The page script hit an error. Details are shown below.",
        "section_labels": {
            "goals": "Goals",
            "playbooks": "SOPs",
            "skills": "Skills",
            "mcp_servers": "MCP",
            "knowledge_bases": "Knowledge",
            "knowledge_updates": "Knowledge Updates",
            "tasks": "Tasks",
            "sessions": "Sessions",
            "runs": "Runs",
            "acceptances": "Acceptances",
            "artifacts": "Artifacts",
            "reflections": "Reflections",
            "events": "Events",
        },
    },
}

RESOURCE_SINGULAR = {
    "goals": "Goal",
    "playbooks": "SOP",
    "skills": "Skill",
    "mcp_servers": "MCP",
    "knowledge_bases": "Knowledge",
    "knowledge_updates": "Knowledge Update",
    "tasks": "Task",
    "sessions": "Session",
    "runs": "Run",
    "acceptances": "Acceptance",
    "artifacts": "Artifact",
    "reflections": "Reflection",
    "events": "Event",
}

RESOURCE_PATHS = {
    "goals": "goals",
    "playbooks": "playbooks",
    "skills": "skills",
    "mcp_servers": "mcp-servers",
    "knowledge_bases": "knowledge-bases",
    "knowledge_updates": "knowledge-updates",
    "tasks": "tasks",
    "sessions": "sessions",
    "runs": "runs",
    "acceptances": "acceptances",
    "artifacts": "artifacts",
    "reflections": "reflections",
    "events": "events",
}


def build_dashboard_html(board_snapshot: dict[str, dict[str, int]] | None = None, *, api_base: str = "/api") -> str:
    snapshot = board_snapshot or {section: {} for section in SECTION_ORDER}
    snapshot_json = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
    api_base_json = json.dumps(api_base)
    section_order_json = json.dumps(SECTION_ORDER)
    resource_singular_json = json.dumps(RESOURCE_SINGULAR, ensure_ascii=False)
    resource_paths_json = json.dumps(RESOURCE_PATHS, ensure_ascii=False)
    translations_json = json.dumps(TRANSLATIONS, ensure_ascii=False)
    default_lang = "zh"

    return f"""<!DOCTYPE html>
<html lang="{TRANSLATIONS[default_lang]['html_lang']}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{html.escape(TRANSLATIONS[default_lang]['page_title'])}</title>
    <style>
      :root {{
        color-scheme: dark;
        --bg: #07111f;
        --panel: rgba(9, 18, 33, 0.78);
        --panel-strong: rgba(16, 29, 53, 0.96);
        --panel-soft: rgba(99, 102, 241, 0.12);
        --text: #eef2ff;
        --muted: #94a3b8;
        --border: rgba(148, 163, 184, 0.16);
        --accent: #7c3aed;
        --accent-2: #06b6d4;
        --shadow: 0 24px 80px rgba(2, 8, 23, 0.45);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        min-height: 100vh;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--text);
        background:
          radial-gradient(circle at top left, rgba(124, 58, 237, 0.35), transparent 30%),
          radial-gradient(circle at top right, rgba(6, 182, 212, 0.22), transparent 28%),
          linear-gradient(180deg, #020617 0%, var(--bg) 100%);
      }}
      .app-shell {{ width: min(1480px, calc(100vw - 32px)); margin: 24px auto 48px; display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 24px; align-items: start; }}
      .sidebar {{ position: sticky; top: 24px; padding: 20px; border: 1px solid var(--border); border-radius: 28px; background: linear-gradient(180deg, rgba(15, 23, 42, 0.94), rgba(9, 18, 33, 0.88)); box-shadow: var(--shadow); backdrop-filter: blur(18px); }}
      .sidebar-head {{ display: grid; gap: 8px; margin-bottom: 18px; }}
      .sidebar-title {{ font-size: 16px; font-weight: 700; }}
      .sidebar-copy {{ color: var(--muted); font-size: 13px; line-height: 1.6; }}
      .sidebar-group {{ margin-top: 18px; display: grid; gap: 8px; }}
      .sidebar-group-title {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; padding: 0 8px; }}
      .nav-button {{ width: 100%; border: 0; cursor: pointer; display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 11px 12px; border-radius: 14px; color: var(--text); background: transparent; text-align: left; font: inherit; }}
      .nav-button:hover {{ background: rgba(99, 102, 241, 0.12); }}
      .nav-button.active {{ background: linear-gradient(135deg, rgba(124, 58, 237, 0.24), rgba(79, 70, 229, 0.22)); border: 1px solid rgba(196, 181, 253, 0.18); }}
      .nav-button-label {{ display: inline-flex; align-items: center; gap: 10px; }}
      .nav-badge {{ min-width: 24px; height: 24px; border-radius: 999px; display: inline-flex; align-items: center; justify-content: center; background: rgba(15, 23, 42, 0.9); border: 1px solid var(--border); color: var(--muted); font-size: 12px; padding: 0 8px; }}
      .shell {{ width: auto; margin: 0; }}
      .topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 18px 22px; border: 1px solid var(--border); border-radius: 24px; background: rgba(15, 23, 42, 0.72); box-shadow: var(--shadow); backdrop-filter: blur(14px); }}
      .topbar-title strong {{ display: block; font-size: 24px; line-height: 1.2; }}
      .topbar-title span {{ display: block; margin-top: 6px; color: var(--muted); font-size: 14px; line-height: 1.6; max-width: 720px; }}
      .topbar-controls {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }}
      .scope-card {{ display: grid; gap: 6px; min-width: 200px; }}
      .scope-card label {{ color: var(--muted); font-size: 12px; }}
      .scope-card select {{ width: 100%; border-radius: 14px; border: 1px solid rgba(148, 163, 184, 0.16); background: rgba(2, 6, 23, 0.74); color: var(--text); padding: 11px 12px; font: inherit; }}
      .view-page[hidden] {{ display: none !important; }}
      .route-placeholder-grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }}
      .placeholder-card {{ grid-column: span 4; padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.62); border: 1px solid rgba(148, 163, 184, 0.12); }}
      .placeholder-card h3 {{ margin: 0 0 8px; font-size: 18px; }}
      .placeholder-card p {{ margin: 0; color: var(--muted); line-height: 1.7; }}
      .flow-grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }}
      .flow-card {{ grid-column: span 3; padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.62); border: 1px solid rgba(148, 163, 184, 0.12); }}
      .flow-card strong {{ display: block; font-size: 18px; margin-bottom: 6px; }}
      .flow-card small {{ display: block; color: var(--muted); line-height: 1.6; }}
      .flow-card .pill-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
      .flow-link {{ display: inline-flex; margin-top: 14px; color: #c4b5fd; cursor: pointer; text-decoration: none; }}
      .flow-link:hover {{ color: #ddd6fe; }}
      .focus-grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }}
      .focus-card {{ grid-column: span 3; padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.62); border: 1px solid rgba(148, 163, 184, 0.12); }}
      .focus-card strong {{ display: block; font-size: 18px; margin-bottom: 8px; }}
      .focus-card small {{ display: block; color: var(--muted); line-height: 1.7; }}
      .focus-meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
      .shell {{ width: min(1180px, calc(100vw - 32px)); margin: 24px auto 48px; }}
      .hero {{
        padding: 32px;
        border: 1px solid var(--border);
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(17, 24, 39, 0.78));
        box-shadow: var(--shadow);
        backdrop-filter: blur(18px);
      }}
      .hero-top {{ display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; flex-wrap: wrap; }}
      .badge {{
        display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 999px;
        background: rgba(124, 58, 237, 0.16); color: #ddd6fe; font-size: 13px; border: 1px solid rgba(196, 181, 253, 0.15);
      }}
      .hero-controls {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }}
      .lang-toggle {{ display: inline-flex; gap: 6px; padding: 6px; background: rgba(15, 23, 42, 0.65); border: 1px solid var(--border); border-radius: 999px; }}
      .lang-toggle button {{ border: 0; background: transparent; color: var(--muted); border-radius: 999px; padding: 8px 12px; cursor: pointer; font-weight: 700; }}
      .lang-toggle button.active {{ background: linear-gradient(135deg, var(--accent), #4f46e5); color: var(--text); }}
      h1 {{ margin: 14px 0 10px; font-size: clamp(32px, 5vw, 54px); line-height: 1.04; }}
      .hero p {{ margin: 0; max-width: 760px; color: var(--muted); font-size: 16px; line-height: 1.7; }}
      .hero-actions {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 24px; }}
      .button {{ border: 0; border-radius: 14px; padding: 12px 16px; font-weight: 600; cursor: pointer; text-decoration: none; color: var(--text); background: linear-gradient(135deg, var(--accent), #4f46e5); box-shadow: 0 12px 32px rgba(79, 70, 229, 0.35); }}
      .button.secondary {{ background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border); box-shadow: none; }}
      .hero-meta {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 28px; }}
      .meta-card {{ padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.65); border: 1px solid var(--border); }}
      .meta-card strong {{ display: block; font-size: 24px; margin-top: 8px; }}
      .section {{ margin-top: 24px; }}
      .section-title {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }}
      .section-title h2 {{ margin: 0; font-size: 20px; }}
      .section-title span {{ color: var(--muted); font-size: 14px; }}
      .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }}
      .card {{ grid-column: span 12; padding: 22px; border-radius: 24px; border: 1px solid var(--border); background: var(--panel); box-shadow: var(--shadow); backdrop-filter: blur(14px); }}
      .summary-card {{ grid-column: span 12; position: relative; overflow: hidden; }}
      .summary-card::after {{ content: ""; position: absolute; inset: auto -30px -40px auto; width: 140px; height: 140px; border-radius: 999px; background: radial-gradient(circle, rgba(6, 182, 212, 0.22), transparent 70%); }}
      .summary-card h3, .endpoint-card h3, .form-card h3 {{ margin: 0 0 8px; font-size: 18px; }}
      .eyebrow {{ color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; }}
      .metric {{ display: flex; align-items: baseline; gap: 10px; margin-top: 10px; }}
      .metric strong {{ font-size: 38px; line-height: 1; }}
      .metric span {{ color: var(--muted); }}
      .pills {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }}
      .pill {{ border-radius: 999px; padding: 8px 10px; background: var(--panel-soft); color: #dbeafe; border: 1px solid rgba(125, 211, 252, 0.12); font-size: 13px; }}
      .chart {{ height: 10px; margin-top: 18px; border-radius: 999px; background: rgba(30, 41, 59, 0.88); overflow: hidden; }}
      .chart > span {{ display: block; height: 100%; width: 0%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); transition: width 0.35s ease; }}
      .endpoint-card {{ grid-column: span 4; background: var(--panel-strong); }}
      .endpoint-link {{ display: inline-flex; margin-top: 14px; color: #c4b5fd; text-decoration: none; }}
      .endpoint-link:hover {{ color: #ddd6fe; }}
      .workbench-card {{ grid-column: span 12; }}
      .workbench-status {{ margin-top: 12px; padding: 12px 14px; border-radius: 14px; background: rgba(15, 23, 42, 0.65); border: 1px solid var(--border); color: var(--muted); }}
      .workbench-grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; margin-top: 16px; }}
      .form-card {{ grid-column: span 6; padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.62); border: 1px solid rgba(148, 163, 184, 0.12); }}
      .field-grid {{ display: grid; gap: 12px; }}
      .field {{ display: grid; gap: 6px; }}
      .field label {{ font-size: 13px; color: var(--muted); }}
      .field input, .field textarea, .field select {{ width: 100%; border-radius: 14px; border: 1px solid rgba(148, 163, 184, 0.16); background: rgba(2, 6, 23, 0.74); color: var(--text); padding: 11px 12px; font: inherit; }}
      .field textarea {{ min-height: 96px; resize: vertical; }}
      .inline-checkbox {{ display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: 14px; }}
      .inline-checkbox input {{ width: auto; }}
      .form-actions {{ margin-top: 14px; display: flex; justify-content: flex-end; }}
      .action-grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }}
      .action-card {{ grid-column: span 4; padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.62); border: 1px solid rgba(148, 163, 184, 0.12); }}
      .action-card h3 {{ margin: 0 0 10px; font-size: 18px; }}
      .action-status {{ margin-top: 12px; padding: 12px 14px; border-radius: 14px; background: rgba(15, 23, 42, 0.65); border: 1px solid var(--border); color: var(--muted); }}
      .action-rows {{ display: grid; gap: 12px; }}
      .action-row {{ padding: 14px; border-radius: 16px; background: rgba(2, 6, 23, 0.58); border: 1px solid rgba(148, 163, 184, 0.08); }}
      .action-row strong {{ display: block; font-size: 14px; }}
      .action-row small {{ display: block; color: var(--muted); margin-top: 6px; line-height: 1.6; white-space: pre-wrap; }}
      .action-buttons {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }}
      .action-buttons .button {{ padding: 9px 12px; border-radius: 12px; box-shadow: none; }}
      .action-buttons .button.secondary {{ background: rgba(15, 23, 42, 0.82); }}
      .session-groups {{ display: grid; gap: 16px; }}
      .session-group {{ padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.62); border: 1px solid rgba(148, 163, 184, 0.12); }}
      .session-group-header {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 14px; }}
      .session-group-header strong {{ font-size: 16px; display: block; }}
      .session-group-header span {{ color: var(--muted); font-size: 13px; }}
      .session-tree {{ display: grid; gap: 12px; }}
      .session-node {{ position: relative; padding: 14px 16px; border-radius: 16px; background: rgba(2, 6, 23, 0.58); border: 1px solid rgba(148, 163, 184, 0.08); }}
      .session-node::before {{ content: ""; position: absolute; left: -10px; top: 18px; width: 10px; height: 1px; background: rgba(148, 163, 184, 0.25); }}
      .session-node.depth-0::before {{ display: none; }}
      .session-node-title {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; flex-wrap: wrap; }}
      .session-node-title strong {{ font-size: 14px; }}
      .session-node-meta {{ margin-top: 8px; color: var(--muted); font-size: 13px; line-height: 1.6; white-space: pre-wrap; }}
      .session-node-children {{ display: grid; gap: 10px; margin-top: 10px; padding-left: 18px; border-left: 1px dashed rgba(148, 163, 184, 0.18); }}
      .patch-review-grid {{ display: grid; gap: 16px; }}
      .patch-review-card {{ padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.62); border: 1px solid rgba(148, 163, 184, 0.12); }}
      .patch-review-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; flex-wrap: wrap; }}
      .patch-review-head strong {{ font-size: 16px; display: block; }}
      .patch-review-head small {{ display: block; color: var(--muted); margin-top: 6px; line-height: 1.6; }}
      .patch-meta {{ display: grid; gap: 6px; margin-top: 12px; color: var(--muted); font-size: 13px; }}
      .patch-changes {{ display: grid; gap: 10px; margin-top: 14px; }}
      .patch-change {{ padding: 12px 14px; border-radius: 14px; background: rgba(2, 6, 23, 0.7); border: 1px solid rgba(148, 163, 184, 0.08); }}
      .patch-change code {{ color: #c4b5fd; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
      .patch-change span {{ display: block; color: var(--muted); margin-top: 6px; line-height: 1.6; }}
      .skill-version-grid {{ display: grid; gap: 16px; }}
      .skill-family-card {{ padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.62); border: 1px solid rgba(148, 163, 184, 0.12); }}
      .skill-version-list {{ display: grid; gap: 10px; margin-top: 12px; }}
      .skill-version-item {{ padding: 12px 14px; border-radius: 14px; background: rgba(2, 6, 23, 0.7); border: 1px solid rgba(148, 163, 184, 0.08); }}
      .skill-version-item strong {{ display: block; font-size: 14px; }}
      .skill-version-item small {{ display: block; color: var(--muted); margin-top: 6px; line-height: 1.6; white-space: pre-wrap; }}
      .list-card {{ grid-column: span 8; }}
      .activity-card {{ grid-column: span 4; }}
      .rows {{ display: grid; gap: 10px; margin-top: 14px; }}
      .row {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 14px 16px; border-radius: 16px; background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(148, 163, 184, 0.08); }}
      .row strong {{ font-size: 14px; }}
      .row small {{ color: var(--muted); display: block; margin-top: 4px; }}
      .state {{ color: #bfdbfe; background: rgba(59, 130, 246, 0.14); padding: 6px 9px; border-radius: 999px; font-size: 12px; }}
      .timeline {{ display: grid; gap: 14px; margin-top: 10px; }}
      .timeline-item {{ position: relative; padding-left: 18px; color: var(--muted); line-height: 1.6; }}
      .timeline-item::before {{ content: ""; position: absolute; left: 0; top: 10px; width: 8px; height: 8px; border-radius: 999px; background: linear-gradient(135deg, var(--accent), var(--accent-2)); box-shadow: 0 0 18px rgba(99, 102, 241, 0.55); }}
      pre {{ margin: 0; padding: 18px; border-radius: 18px; overflow: auto; font-size: 13px; color: #cbd5e1; background: rgba(2, 6, 23, 0.74); border: 1px solid rgba(148, 163, 184, 0.08); }}
      .footer {{ margin-top: 20px; color: var(--muted); font-size: 13px; text-align: center; }}
      .editor-meta {{ margin-top: 12px; padding: 14px; border-radius: 14px; background: rgba(2, 6, 23, 0.74); border: 1px solid rgba(148, 163, 184, 0.12); color: var(--muted); font-size: 13px; line-height: 1.7; white-space: pre-wrap; }}
      .boot-error {{ display: none; margin-top: 16px; padding: 16px 18px; border-radius: 18px; background: rgba(127, 29, 29, 0.28); border: 1px solid rgba(248, 113, 113, 0.28); color: #fecaca; box-shadow: var(--shadow); }}
      .boot-error.visible {{ display: block; }}
      .boot-error strong {{ display: block; font-size: 15px; margin-bottom: 6px; }}
      .boot-error small {{ display: block; color: #fecaca; opacity: 0.9; }}
      .boot-error-detail {{ margin-top: 12px; white-space: pre-wrap; word-break: break-word; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; line-height: 1.6; }}
      @media (max-width: 980px) {{
        .app-shell {{ grid-template-columns: 1fr; }}
        .sidebar {{ position: static; }}
        .topbar {{ flex-direction: column; align-items: stretch; }}
        .hero-meta {{ grid-template-columns: 1fr; }}
        .endpoint-card, .list-card, .activity-card, .form-card, .action-card, .placeholder-card, .flow-card, .focus-card {{ grid-column: span 12; }}
      }}
    </style>
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar">
        <div class="sidebar-head">
          <div class="sidebar-title" id="sidebar-title">PlaybookOS</div>
          <div class="sidebar-copy" id="sidebar-copy">AI Work OS control plane</div>
        </div>
        <nav id="sidebar-nav"></nav>
      </aside>
      <main class="shell">
        <section class="topbar">
          <div class="topbar-title">
            <strong id="page-title"></strong>
            <span id="page-subtitle"></span>
          </div>
          <div class="topbar-controls">
            <div class="scope-card">
              <label id="topbar-scope-label"></label>
              <select id="global-scope-select">
                <option value="all"></option>
                <option value="goal"></option>
                <option value="playbook"></option>
                <option value="status"></option>
              </select>
            </div>
          </div>
        </section>

        <section class="section" id="route-focus-section" data-route-section hidden>
          <div class="section-title"><h2 id="route-focus-title"></h2><span id="route-focus-subtitle"></span></div>
          <div class="focus-grid" id="route-focus-rows"></div>
        </section>

        <section class="hero" id="dashboard-hero" data-route-section>

        <div class="hero-top">
          <div>
            <span class="badge" id="hero-badge"></span>
            <h1 id="hero-title"></h1>
            <p id="hero-body"></p>
            <div class="hero-actions">
              <button class="button" id="refresh-board" type="button"></button>
              <a class="button secondary" id="board-json-link" href="{html.escape(api_base)}/board" target="_blank" rel="noreferrer"></a>
            </div>
          </div>
          <div class="hero-controls">
            <div class="lang-toggle" aria-label="Language toggle">
              <button id="lang-zh" type="button">中文</button>
              <button id="lang-en" type="button">EN</button>
            </div>
            <div class="meta-card" style="min-width: 240px;">
              <div class="eyebrow" id="live-data-source-label"></div>
              <strong>{html.escape(api_base)}</strong>
              <span id="last-updated" style="display:block;margin-top:10px;color:var(--muted);"></span>
            </div>
          </div>
        </div>
        <div class="hero-meta">
          <div class="meta-card"><div class="eyebrow" id="total-resources-label"></div><strong id="resource-total">0</strong><span id="total-resources-desc"></span></div>
          <div class="meta-card"><div class="eyebrow" id="blocked-signals-label"></div><strong id="blocked-total">0</strong><span id="blocked-signals-desc"></span></div>
          <div class="meta-card"><div class="eyebrow" id="learning-signals-label"></div><strong id="learning-total">0</strong><span id="learning-signals-desc"></span></div>
        </div>
        <div class="boot-error" id="boot-error">
          <strong id="boot-error-title"></strong>
          <small id="boot-error-body"></small>
          <div class="boot-error-detail" id="boot-error-detail"></div>
        </div>
      </section>

      <section class="section" id="dashboard-summary-section" data-route-section>
        <div class="section-title"><h2 id="control-board-title"></h2><span id="control-board-subtitle"></span></div>
        <div class="grid" id="summary-grid"></div>
      </section>

      <section class="section" id="dashboard-api-section" data-route-section>
        <div class="section-title"><h2 id="api-entry-title"></h2><span id="api-entry-subtitle"></span></div>
        <div class="grid" id="endpoint-grid"></div>
      </section>

      <section class="section" id="workbench-section" data-route-section>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="workbench_title"></h2><span data-i18n="workbench_subtitle"></span></div>
          <div class="workbench-status" id="workbench-status"></div>
          <div class="workbench-grid">
            <form class="form-card" id="goal-form">
              <h3 data-i18n="create_goal"></h3>
              <div class="field-grid">
                <div class="field"><label data-i18n="goal_title"></label><input id="goal-title-input" required /></div>
                <div class="field"><label data-i18n="goal_objective"></label><textarea id="goal-objective-input" required></textarea></div>
                <div class="field"><label data-i18n="goal_constraints"></label><textarea id="goal-constraints-input"></textarea></div>
                <div class="field"><label data-i18n="goal_definition_of_done"></label><textarea id="goal-dod-input"></textarea></div>
              </div>
              <div class="form-actions"><button class="button" type="submit" data-i18n="submit_create"></button></div>
            </form>

            <form class="form-card" id="sop-ingest-form">
              <h3 data-i18n="ingest_playbook"></h3>
              <div class="field-grid">
                <div class="field"><label data-i18n="playbook_name"></label><input id="ingest-playbook-name-input" required /></div>
                <div class="field"><label data-i18n="playbook_goal"></label><select id="ingest-playbook-goal-input"></select></div>
                <div class="field"><label data-i18n="playbook_source_uri"></label><input id="ingest-playbook-source-uri-input" data-i18n-placeholder="input_placeholder_uri" /></div>
                <div class="field"><label data-i18n="ingest_source_kind"></label><input id="ingest-playbook-kind-input" value="markdown" /></div>
                <div class="field"><label data-i18n="ingest_source_file"></label><input id="ingest-playbook-file-input" type="file" accept=".md,.txt,.json,.csv" /></div>
                <div class="field"><label data-i18n="ingest_source_text"></label><textarea id="ingest-playbook-source-input" required></textarea></div>
              </div>
              <div class="form-actions"><button class="button" type="submit" data-i18n="action_ingest_playbook"></button></div>
            </form>

            <form class="form-card" id="playbook-form">
              <h3 data-i18n="create_playbook"></h3>
              <div class="field-grid">
                <div class="field"><label data-i18n="playbook_name"></label><input id="playbook-name-input" required /></div>
                <div class="field"><label data-i18n="playbook_goal"></label><select id="playbook-goal-input"></select></div>
                <div class="field"><label data-i18n="playbook_source_uri"></label><input id="playbook-source-uri-input" data-i18n-placeholder="input_placeholder_uri" /></div>
                <div class="field"><label data-i18n="playbook_steps"></label><textarea id="playbook-steps-input" required></textarea></div>
                <div class="field"><label data-i18n="playbook_mcp_servers"></label><textarea id="playbook-mcp-input"></textarea></div>
              </div>
              <div class="form-actions"><button class="button" type="submit" data-i18n="submit_create"></button></div>
            </form>

            <form class="form-card" id="skill-form">
              <h3 data-i18n="create_skill"></h3>
              <div class="field-grid">
                <div class="field"><label data-i18n="skill_name"></label><input id="skill-name-input" required /></div>
                <div class="field"><label data-i18n="skill_description"></label><textarea id="skill-description-input" required></textarea></div>
                <div class="field"><label data-i18n="skill_required_mcp_servers"></label><textarea id="skill-mcp-input"></textarea></div>
              </div>
              <div class="form-actions"><button class="button" type="submit" data-i18n="submit_create"></button></div>
            </form>

            <form class="form-card" id="mcp-server-form">
              <h3 data-i18n="create_mcp_server"></h3>
              <div class="field-grid">
                <div class="field"><label data-i18n="mcp_server_name"></label><input id="mcp-server-name-input" required /></div>
                <div class="field"><label data-i18n="mcp_server_transport"></label><input id="mcp-server-transport-input" value="streamable_http" required /></div>
                <div class="field"><label data-i18n="mcp_server_endpoint"></label><input id="mcp-server-endpoint-input" required /></div>
                <div class="field"><label data-i18n="mcp_server_scopes"></label><textarea id="mcp-server-scopes-input"></textarea></div>
              </div>
              <div class="form-actions"><button class="button" type="submit" data-i18n="submit_create"></button></div>
            </form>

            <form class="form-card" id="knowledge-form">
              <h3 data-i18n="create_knowledge"></h3>
              <div class="field-grid">
                <div class="field"><label data-i18n="knowledge_name"></label><input id="knowledge-name-input" required /></div>
                <div class="field"><label data-i18n="knowledge_goal"></label><select id="knowledge-goal-input"></select></div>
                <div class="field"><label data-i18n="knowledge_description"></label><textarea id="knowledge-description-input"></textarea></div>
                <div class="field"><label data-i18n="knowledge_content"></label><textarea id="knowledge-content-input" required></textarea></div>
                <div class="field"><label data-i18n="knowledge_tags"></label><textarea id="knowledge-tags-input"></textarea></div>
              </div>
              <div class="form-actions"><button class="button" type="submit" data-i18n="submit_create"></button></div>
            </form>

            <form class="form-card" id="task-form">
              <h3 data-i18n="create_task"></h3>
              <div class="field-grid">
                <div class="field"><label data-i18n="task_name"></label><input id="task-name-input" required /></div>
                <div class="field"><label data-i18n="task_description"></label><textarea id="task-description-input" required></textarea></div>
                <div class="field"><label data-i18n="task_goal"></label><select id="task-goal-input" required></select></div>
                <div class="field"><label data-i18n="task_playbook"></label><select id="task-playbook-input" required></select></div>
                <div class="field"><label data-i18n="task_skill"></label><select id="task-skill-input"></select></div>
                <div class="field"><label data-i18n="task_knowledge"></label><textarea id="task-knowledge-input"></textarea></div>
                <div class="field"><label data-i18n="task_queue"></label><input id="task-queue-input" value="default" /></div>
                <div class="field"><label data-i18n="task_priority"></label><input id="task-priority-input" type="number" value="0" /></div>
                <div class="field"><label data-i18n="task_depends_on_ids"></label><textarea id="task-depends-on-input"></textarea></div>
                <label class="inline-checkbox"><input id="task-approval-input" type="checkbox" /><span data-i18n="task_approval_required"></span></label>
              </div>
              <div class="form-actions"><button class="button" type="submit" data-i18n="submit_create"></button></div>
            </form>

            <article class="form-card">
              <h3 data-i18n="ingest_guidance_title"></h3>
              <div class="workbench-status" id="ingest-guidance"></div>
            </article>
          </div>
        </article>
      </section>

      <section class="section" id="authoring-section" data-route-section>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="authoring_wizard_title"></h2><span data-i18n="authoring_wizard_subtitle"></span></div>
          <div class="patch-review-grid" id="authoring-wizard-rows"></div>
        </article>
      </section>

      <section class="section" id="editor-section" data-route-section>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="editor_title"></h2><span data-i18n="editor_subtitle"></span></div>
          <div class="workbench-status" id="editor-status"></div>
          <div class="workbench-grid">
            <div class="form-card">
              <h3 data-i18n="editor_title"></h3>
              <div class="field-grid">
                <div class="field"><label data-i18n="editor_resource_type"></label><select id="editor-resource-type"></select></div>
                <div class="field"><label data-i18n="editor_resource_id"></label><select id="editor-resource-id"></select></div>
                <div class="field"><label data-i18n="editor_payload"></label><textarea id="editor-payload-input" style="min-height: 280px;"></textarea></div>
              </div>
              <div class="form-actions" style="justify-content: space-between; gap: 12px;">
                <button class="button secondary" id="editor-reset-button" type="button" data-i18n="editor_reset"></button>
                <div style="display:flex; gap:12px;">
                  <button class="button secondary" id="editor-load-button" type="button" data-i18n="editor_load"></button>
                  <button class="button" id="editor-save-button" type="button" data-i18n="editor_save"></button>
                </div>
              </div>
            </div>
            <div class="form-card">
              <h3 data-i18n="editor_meta"></h3>
              <div class="editor-meta" id="editor-meta"></div>
            </div>
          </div>
        </article>
      </section>

      <section class="section" id="action-center-section" data-route-section>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="action_center"></h2><span data-i18n="action_center_subtitle"></span></div>
          <div class="action-status" id="action-status"></div>
          <div class="action-grid" style="margin-top:16px;">
            <div class="action-card">
              <h3 data-i18n="goal_ops_title"></h3>
              <div class="action-rows" id="goal-action-rows"></div>
            </div>
            <div class="action-card">
              <h3 data-i18n="review_ops_title"></h3>
              <div class="action-rows" id="review-action-rows"></div>
            </div>
            <div class="action-card">
              <h3 data-i18n="learning_ops_title"></h3>
              <div class="action-rows" id="learning-action-rows"></div>
            </div>
          </div>
        </article>
      </section>

      <section class="section" id="supervisor-section" data-route-section>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="supervisor_center_title"></h2><span data-i18n="supervisor_center_subtitle"></span></div>
          <div class="patch-review-grid" id="supervisor-summary-rows"></div>
        </article>
      </section>

      <section class="section" id="skill-version-section" data-route-section>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="skill_version_title"></h2><span data-i18n="skill_version_subtitle"></span></div>
          <div class="skill-version-grid" id="skill-version-rows"></div>
        </article>
      </section>

      <section class="section" id="patch-review-section" data-route-section>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="patch_review_title"></h2><span data-i18n="patch_review_subtitle"></span></div>
          <div class="patch-review-grid" id="patch-review-rows"></div>
        </article>
      </section>

      <section class="section" id="session-tree-section" data-route-section>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="session_tree_title"></h2><span data-i18n="session_tree_subtitle"></span></div>
          <div class="session-groups" id="session-groups"></div>
        </article>
      </section>

      <section class="section" id="execution-inspector-section" data-route-section>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="execution_inspector_title"></h2><span data-i18n="execution_inspector_subtitle"></span></div>
          <div class="patch-review-grid" id="execution-inspector-rows"></div>
        </article>
      </section>

      <section class="section" id="resource-peek-section" data-route-section>
        <div class="grid">
          <article class="card list-card">
            <div class="section-title"><h2 id="resource-peek-title"></h2><span id="resource-peek-subtitle"></span></div>
            <div class="rows" id="resource-rows"></div>
          </article>
          <article class="card activity-card">
            <div class="section-title"><h2 id="operating-rhythm-title"></h2><span id="operating-rhythm-subtitle"></span></div>
            <div class="timeline">
              <div class="timeline-item" id="timeline-1"></div>
              <div class="timeline-item" id="timeline-2"></div>
              <div class="timeline-item" id="timeline-3"></div>
            </div>
          </article>
        </div>
      </section>

      <section class="section" id="snapshot-section" data-route-section>
        <div class="section-title"><h2 id="snapshot-json-title"></h2><span id="snapshot-json-subtitle"></span></div>
        <article class="card"><pre id="snapshot-json"></pre></article>
      </section>

      <section class="section" id="dashboard-flow-section" data-route-section>
        <div class="section-title"><h2 id="global-flow-title"></h2><span id="global-flow-subtitle"></span></div>
        <div class="flow-grid" id="global-flow-rows"></div>
      </section>

      <section class="section" id="settings-placeholder-section" data-route-section hidden>
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="route_placeholder_title"></h2><span data-i18n="route_placeholder_body"></span></div>
          <div class="route-placeholder-grid">
            <div class="placeholder-card" id="model-settings-panel" data-settings-panel="model-settings">
              <h3 data-i18n="nav_model_settings"></h3>
              <p data-i18n="settings_model_card"></p>
            </div>
            <div class="placeholder-card" id="global-settings-panel" data-settings-panel="global-settings">
              <h3 data-i18n="nav_global_settings"></h3>
              <p data-i18n="settings_global_card"></p>
            </div>
            <div class="placeholder-card" id="session-admin-panel" data-settings-panel="session-admin">
              <h3 data-i18n="nav_session_admin"></h3>
              <p data-i18n="settings_session_card"></p>
            </div>
          </div>
        </article>
      </section>

      <div class="footer" id="footer-text"></div>
      </main>
    </div>

    <script>
      const apiBase = {api_base_json};
      const sectionOrder = {section_order_json};
      const resourceSingular = {resource_singular_json};
      const resourcePaths = {resource_paths_json};
      const translations = {translations_json};
      let currentSnapshot = {snapshot_json};
      let latestResources = {{}};
      let latestIngestionResult = null;
      let latestAuthoringPacks = {{}};
      const editableSections = ['goals', 'playbooks', 'skills', 'mcp_servers', 'knowledge_bases', 'tasks'];
      let currentLanguage = localStorage.getItem('playbookos-language') || 'zh';
      let currentRoute = (window.location.hash || '#dashboard').replace(/^#/, '') || 'dashboard';
      const navGroups = [
        {{ titleKey: 'nav_group_overview', routes: ['dashboard'] }},
        {{ titleKey: 'nav_group_workbench', routes: ['goals', 'playbooks', 'skills', 'mcp', 'knowledge', 'tasks', 'sessions', 'learning', 'approvals', 'prompts'] }},
        {{ titleKey: 'nav_group_settings', routes: ['model-settings', 'global-settings', 'session-admin'] }},
        {{ titleKey: 'nav_group_system', routes: ['system'] }},
      ];
      const routeConfigs = {{
        dashboard: {{ navKey: 'nav_dashboard', titleKey: 'page_dashboard_title', subtitleKey: 'page_dashboard_subtitle' }},
        goals: {{ navKey: 'nav_goals', titleKey: 'page_goals_title', subtitleKey: 'page_goals_subtitle' }},
        playbooks: {{ navKey: 'nav_playbooks', titleKey: 'page_playbooks_title', subtitleKey: 'page_playbooks_subtitle' }},
        skills: {{ navKey: 'nav_skills', titleKey: 'page_skills_title', subtitleKey: 'page_skills_subtitle' }},
        mcp: {{ navKey: 'nav_mcp', titleKey: 'page_mcp_title', subtitleKey: 'page_mcp_subtitle' }},
        knowledge: {{ navKey: 'nav_knowledge', titleKey: 'page_knowledge_title', subtitleKey: 'page_knowledge_subtitle' }},
        tasks: {{ navKey: 'nav_tasks', titleKey: 'page_tasks_title', subtitleKey: 'page_tasks_subtitle' }},
        sessions: {{ navKey: 'nav_sessions', titleKey: 'page_sessions_title', subtitleKey: 'page_sessions_subtitle' }},
        learning: {{ navKey: 'nav_learning', titleKey: 'page_learning_title', subtitleKey: 'page_learning_subtitle' }},
        approvals: {{ navKey: 'nav_approvals', titleKey: 'page_approvals_title', subtitleKey: 'page_approvals_subtitle' }},
        prompts: {{ navKey: 'nav_prompts', titleKey: 'page_prompts_title', subtitleKey: 'page_prompts_subtitle' }},
        'model-settings': {{ navKey: 'nav_model_settings', titleKey: 'page_model_settings_title', subtitleKey: 'page_model_settings_subtitle' }},
        'global-settings': {{ navKey: 'nav_global_settings', titleKey: 'page_global_settings_title', subtitleKey: 'page_global_settings_subtitle' }},
        'session-admin': {{ navKey: 'nav_session_admin', titleKey: 'page_session_admin_title', subtitleKey: 'page_session_admin_subtitle' }},
        system: {{ navKey: 'nav_versions', titleKey: 'page_system_title', subtitleKey: 'page_system_subtitle' }},
      }};
      const routeSections = {{
        dashboard: ['dashboard-hero', 'dashboard-summary-section', 'dashboard-flow-section', 'dashboard-api-section', 'action-center-section', 'supervisor-section', 'resource-peek-section', 'snapshot-section'],
        goals: ['route-focus-section', 'workbench-section', 'editor-section', 'action-center-section'],
        playbooks: ['route-focus-section', 'workbench-section', 'patch-review-section', 'editor-section'],
        skills: ['route-focus-section', 'workbench-section', 'authoring-section', 'skill-version-section', 'editor-section'],
        mcp: ['route-focus-section', 'workbench-section', 'editor-section'],
        knowledge: ['route-focus-section', 'workbench-section', 'editor-section'],
        tasks: ['route-focus-section', 'workbench-section', 'editor-section', 'action-center-section'],
        sessions: ['route-focus-section', 'session-tree-section', 'execution-inspector-section', 'supervisor-section'],
        learning: ['route-focus-section', 'patch-review-section', 'skill-version-section', 'supervisor-section'],
        approvals: ['route-focus-section', 'action-center-section'],
        prompts: ['route-focus-section', 'workbench-section'],
        'model-settings': ['settings-placeholder-section'],
        'global-settings': ['settings-placeholder-section'],
        'session-admin': ['settings-placeholder-section', 'session-tree-section'],
        system: ['route-focus-section', 'dashboard-api-section', 'snapshot-section'],
      }};
      const workbenchRouteForms = {{
        goals: ['goal-form'],
        playbooks: ['sop-ingest-form', 'playbook-form', 'ingest-guidance'],
        skills: ['skill-form'],
        mcp: ['mcp-server-form'],
        knowledge: ['knowledge-form'],
        tasks: ['task-form'],
        prompts: ['ingest-guidance'],
      }};

      function t(key) {{
        return translations[currentLanguage][key];
      }}

      function resourcePath(section) {{
        return resourcePaths[section] || section;
      }}

      function sectionLabel(section) {{
        return translations[currentLanguage].section_labels[section] || section;
      }}

      function sumValues(record) {{
        return Object.values(record || {{}}).reduce((total, value) => total + Number(value || 0), 0);
      }}

      function formatStateLabel(value) {{
        return String(value).replaceAll('_', ' ');
      }}

      function escapeHtml(value) {{
        return String(value)
          .replaceAll('&', '&amp;')
          .replaceAll('<', '&lt;')
          .replaceAll('>', '&gt;')
          .replaceAll('"', '&quot;')
          .replaceAll("'", '&#39;');
      }}

      function splitLines(value) {{
        return String(value || '').split(/\\n|,/).map((item) => item.trim()).filter(Boolean);
      }}

      function bootText(key, fallback) {{
        return (translations[currentLanguage] && translations[currentLanguage][key]) || (translations.zh && translations.zh[key]) || fallback;
      }}

      function clearBootError() {{
        const panel = document.getElementById('boot-error');
        if (!panel) return;
        panel.classList.remove('visible');
        document.getElementById('boot-error-title').textContent = '';
        document.getElementById('boot-error-body').textContent = '';
        document.getElementById('boot-error-detail').textContent = '';
      }}

      function showBootError(error) {{
        const panel = document.getElementById('boot-error');
        if (!panel) return;
        panel.classList.add('visible');
        document.getElementById('boot-error-title').textContent = bootText('boot_error_title', 'Frontend boot failed');
        document.getElementById('boot-error-body').textContent = bootText('boot_error_body', 'The page script hit an error. Details are shown below.');
        const detail = error && error.stack ? error.stack : error && error.message ? error.message : String(error || 'Unknown error');
        document.getElementById('boot-error-detail').textContent = detail;
      }}

      function buildManualUri(kind, name) {{
        const slug = String(name || 'manual').trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'manual';
        return `playbookos://manual/${{kind}}/${{slug}}-${{Date.now()}}`;
      }}

      function setWorkbenchStatus(message, state = 'idle') {{
        const node = document.getElementById('workbench-status');
        node.dataset.state = state;
        node.textContent = message;
        node.style.color = state === 'error' ? '#fca5a5' : state === 'success' ? '#86efac' : 'var(--muted)';
      }}

      function setIngestionGuidance(html) {{
        const node = document.getElementById('ingest-guidance');
        if (!node) return;
        node.innerHTML = html;
      }}

      function setActionStatus(message, state = 'idle') {{
        const node = document.getElementById('action-status');
        if (!node) return;
        node.dataset.state = state;
        node.textContent = message;
        node.style.color = state === 'error' ? '#fca5a5' : state === 'success' ? '#86efac' : 'var(--muted)';
      }}

      function routeCount(route) {{
        if (route === 'dashboard') return sectionOrder.reduce((total, section) => total + sumValues(currentSnapshot[section] || {{}}), 0);
        if (route === 'goals') return sumValues(currentSnapshot.goals || {{}});
        if (route === 'playbooks') return sumValues(currentSnapshot.playbooks || {{}});
        if (route === 'skills') return sumValues(currentSnapshot.skills || {{}});
        if (route === 'mcp') return sumValues(currentSnapshot.mcp_servers || {{}});
        if (route === 'knowledge') return sumValues(currentSnapshot.knowledge_bases || {{}}) + sumValues(currentSnapshot.knowledge_updates || {{}});
        if (route === 'tasks') return sumValues(currentSnapshot.tasks || {{}});
        if (route === 'sessions') return sumValues(currentSnapshot.sessions || {{}});
        if (route === 'learning') return sumValues(currentSnapshot.reflections || {{}}) + sumValues(currentSnapshot.knowledge_updates || {{}});
        if (route === 'approvals') return Number((currentSnapshot.runs || {{}}).waiting_human || 0) + Number((currentSnapshot.tasks || {{}}).review || 0);
        if (route === 'prompts') return latestIngestionResult && latestIngestionResult.tooling_guidance ? (latestIngestionResult.tooling_guidance.prompt_blocks || []).length : 0;
        return 0;
      }}

      function renderSidebarNav() {{
        const nav = document.getElementById('sidebar-nav');
        nav.innerHTML = navGroups.map((group) => `
          <div class="sidebar-group">
            <div class="sidebar-group-title">${{escapeHtml(t(group.titleKey))}}</div>
            ${{group.routes.map((route) => {{
              const config = routeConfigs[route];
              const active = currentRoute === route ? 'active' : '';
              const count = routeCount(route);
              return `
                <button class="nav-button ${{active}}" type="button" data-route="${{route}}">
                  <span class="nav-button-label">${{escapeHtml(t(config.navKey))}}</span>
                  <span class="nav-badge">${{count}}</span>
                </button>
              `;
            }}).join('')}}
          </div>
        `).join('');
      }}

      function renderGlobalFlow() {{
        const items = [
          {{ route: 'goals', label: t('nav_goals'), total: sumValues(currentSnapshot.goals || {{}}), pending: Number((currentSnapshot.goals || {{}}).running || 0) + Number((currentSnapshot.goals || {{}}).blocked || 0), errors: Number((currentSnapshot.goals || {{}}).blocked || 0) }},
          {{ route: 'playbooks', label: t('nav_playbooks'), total: sumValues(currentSnapshot.playbooks || {{}}), pending: Number((currentSnapshot.playbooks || {{}}).draft || 0), errors: Number((currentSnapshot.playbooks || {{}}).deprecated || 0) }},
          {{ route: 'skills', label: `${{t('nav_skills')}} / ${{t('nav_mcp')}}`, total: sumValues(currentSnapshot.skills || {{}}) + sumValues(currentSnapshot.mcp_servers || {{}}), pending: Number((currentSnapshot.skills || {{}}).draft || 0) + Number((currentSnapshot.mcp_servers || {{}}).inactive || 0), errors: Number((currentSnapshot.mcp_servers || {{}}).error || 0) }},
          {{ route: 'tasks', label: t('nav_tasks'), total: sumValues(currentSnapshot.tasks || {{}}), pending: Number((currentSnapshot.tasks || {{}}).ready || 0) + Number((currentSnapshot.tasks || {{}}).running || 0) + Number((currentSnapshot.tasks || {{}}).waiting_human || 0), errors: Number((currentSnapshot.tasks || {{}}).blocked || 0) + Number((currentSnapshot.tasks || {{}}).failed || 0) }},
          {{ route: 'sessions', label: `${{t('nav_sessions')}} / Run`, total: sumValues(currentSnapshot.sessions || {{}}) + sumValues(currentSnapshot.runs || {{}}), pending: Number((currentSnapshot.runs || {{}}).running || 0) + Number((currentSnapshot.runs || {{}}).waiting_human || 0), errors: Number((currentSnapshot.runs || {{}}).failed || 0) + Number((currentSnapshot.runs || {{}}).timed_out || 0) }},
          {{ route: 'approvals', label: 'Acceptance / Reflection', total: sumValues(currentSnapshot.acceptances || {{}}) + sumValues(currentSnapshot.reflections || {{}}), pending: Number((currentSnapshot.runs || {{}}).waiting_human || 0) + Number((currentSnapshot.reflections || {{}}).proposed || 0), errors: Number((currentSnapshot.reflections || {{}}).rejected || 0) }},
          {{ route: 'learning', label: `${{t('nav_learning')}} / Knowledge`, total: sumValues(currentSnapshot.knowledge_updates || {{}}) + sumValues(currentSnapshot.knowledge_bases || {{}}), pending: Number((currentSnapshot.knowledge_updates || {{}}).proposed || 0), errors: Number((currentSnapshot.knowledge_updates || {{}}).rejected || 0) }},
        ];
        const container = document.getElementById('global-flow-rows');
        if (!container) return;
        container.innerHTML = items.map((item) => `
          <article class="flow-card">
            <strong>${{escapeHtml(item.label)}}</strong>
            <small>${{escapeHtml(`${{item.total}} total · ${{item.pending}} pending · ${{item.errors}} issues`)}}</small>
            <div class="pill-row">
              <span class="pill">total · ${{item.total}}</span>
              <span class="pill">pending · ${{item.pending}}</span>
              <span class="pill">issues · ${{item.errors}}</span>
            </div>
            <a class="flow-link" href="#${{item.route}}">${{escapeHtml(t(routeConfigs[item.route].navKey))}} →</a>
          </article>
        `).join('');
      }}

      function updatePageHeader() {{
        const config = routeConfigs[currentRoute] || routeConfigs.dashboard;
        document.getElementById('page-title').textContent = t(config.titleKey);
        document.getElementById('page-subtitle').textContent = t(config.subtitleKey);
        document.getElementById('topbar-scope-label').textContent = t('topbar_scope_label');
        const scopeSelect = document.getElementById('global-scope-select');
        scopeSelect.options[0].text = t('topbar_scope_all');
        scopeSelect.options[1].text = t('topbar_scope_goal');
        scopeSelect.options[2].text = t('topbar_scope_playbook');
        scopeSelect.options[3].text = t('topbar_scope_status');
      }}

      function setWorkbenchMode(route) {{
        const visibleIds = new Set(workbenchRouteForms[route] || []);
        [
          'goal-form', 'sop-ingest-form', 'playbook-form', 'skill-form', 'mcp-server-form', 'knowledge-form', 'task-form', 'ingest-guidance'
        ].forEach((id) => {{
          const node = document.getElementById(id);
          if (!node) return;
          const card = node.closest('.form-card') || node;
          card.hidden = visibleIds.size ? !visibleIds.has(id) : false;
        }});
      }}

      function setSettingsMode(route) {{
        document.querySelectorAll('[data-settings-panel]').forEach((node) => {{
          node.hidden = route !== 'model-settings' && route !== 'global-settings' && route !== 'session-admin'
            ? false
            : node.dataset.settingsPanel !== route;
        }});
      }}

      function applyRoute(route, updateHash = false) {{
        currentRoute = routeConfigs[route] ? route : 'dashboard';
        if (updateHash) {{
          window.location.hash = currentRoute;
          return;
        }}
        const visibleSections = new Set(routeSections[currentRoute] || routeSections.dashboard);
        document.querySelectorAll('[data-route-section]').forEach((section) => {{
          section.hidden = !visibleSections.has(section.id);
        }});
        setWorkbenchMode(currentRoute);
        setSettingsMode(currentRoute);
        updatePageHeader();
        renderSidebarNav();
        renderRouteFocus();
      }}

      function applyLanguage(language) {{
        currentLanguage = translations[language] ? language : 'zh';
        localStorage.setItem('playbookos-language', currentLanguage);
        document.documentElement.lang = t('html_lang');
        document.title = t('page_title');
        document.getElementById('boot-error-title').textContent = bootText('boot_error_title', 'Frontend boot failed');
        document.getElementById('boot-error-body').textContent = bootText('boot_error_body', 'The page script hit an error. Details are shown below.');
        document.getElementById('hero-badge').textContent = t('badge');
        document.getElementById('hero-title').textContent = t('hero_title');
        document.getElementById('hero-body').textContent = t('hero_body');
        document.getElementById('refresh-board').textContent = t('refresh_board');
        document.getElementById('board-json-link').textContent = t('view_board_json');
        document.getElementById('live-data-source-label').textContent = t('live_data_source');
        document.getElementById('total-resources-label').textContent = t('total_resources');
        document.getElementById('total-resources-desc').textContent = t('total_resources_desc');
        document.getElementById('blocked-signals-label').textContent = t('blocked_signals');
        document.getElementById('blocked-signals-desc').textContent = t('blocked_signals_desc');
        document.getElementById('learning-signals-label').textContent = t('learning_signals');
        document.getElementById('learning-signals-desc').textContent = t('learning_signals_desc');
        document.getElementById('control-board-title').textContent = t('control_board');
        document.getElementById('control-board-subtitle').textContent = t('control_board_subtitle');
        document.getElementById('api-entry-title').textContent = t('api_entry_points');
        document.getElementById('api-entry-subtitle').textContent = t('api_entry_subtitle');
        document.getElementById('resource-peek-title').textContent = t('quick_resource_peek');
        document.getElementById('resource-peek-subtitle').textContent = t('quick_resource_peek_subtitle');
        document.getElementById('operating-rhythm-title').textContent = t('operating_rhythm');
        document.getElementById('operating-rhythm-subtitle').textContent = t('operating_rhythm_subtitle');
        document.getElementById('timeline-1').textContent = t('timeline_1');
        document.getElementById('timeline-2').textContent = t('timeline_2');
        document.getElementById('timeline-3').textContent = t('timeline_3');
        document.getElementById('snapshot-json-title').textContent = t('snapshot_json');
        document.getElementById('snapshot-json-subtitle').textContent = t('snapshot_json_subtitle');
        document.getElementById('global-flow-title').textContent = t('global_flow_title');
        document.getElementById('global-flow-subtitle').textContent = t('global_flow_subtitle');
        document.getElementById('footer-text').textContent = t('footer');
        document.getElementById('lang-zh').classList.toggle('active', currentLanguage === 'zh');
        document.getElementById('lang-en').classList.toggle('active', currentLanguage === 'en');
        document.querySelectorAll('[data-i18n]').forEach((node) => {{ node.textContent = t(node.dataset.i18n); }});
        document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {{ node.placeholder = t(node.dataset.i18nPlaceholder); }});
        if (!document.getElementById('workbench-status').dataset.state) {{
          setWorkbenchStatus(t('workbench_status_ready'));
        }}
        if (!latestIngestionResult) {{
          setIngestionGuidance(`<small>${{escapeHtml(t('ingest_guidance_empty'))}}</small>`);
        }} else {{
          renderIngestionGuidance();
        }}
        if (!document.getElementById('action-status').dataset.state) {{
          setActionStatus(t('action_status_ready'));
        }}
        renderSummary(currentSnapshot);
        renderRouteFocus();
        renderGlobalFlow();
        renderEndpointCards();
        renderWorkbenchOptions();
        renderSidebarNav();
        updatePageHeader();
        renderActionCenter();
        renderSkillVersions();
        renderPatchReviews();
        renderSessionTree();
        if (!document.getElementById('editor-status').dataset.state) {{
          document.getElementById('editor-status').dataset.state = 'idle';
          document.getElementById('editor-status').textContent = t('editor_status_ready');
        }}
        refreshEditorResourceOptions();
        applyRoute(currentRoute);
      }}

      function renderSummary(snapshot) {{
        currentSnapshot = snapshot || {{}};
        document.getElementById('summary-grid').innerHTML = sectionOrder.map((section) => createSummaryCard(section, snapshot[section] || {{}})).join('');
        const resourceTotal = sectionOrder.reduce((total, section) => total + sumValues(snapshot[section] || {{}}), 0);
        const blockedTotal = Number((snapshot.goals || {{}}).blocked || 0) + Number((snapshot.runs || {{}}).waiting_human || 0);
        const learningTotal = Number(sumValues(snapshot.reflections || {{}})) + Number(sumValues(snapshot.acceptances || {{}}));
        document.getElementById('resource-total').textContent = String(resourceTotal);
        document.getElementById('blocked-total').textContent = String(blockedTotal);
        document.getElementById('learning-total').textContent = String(learningTotal);
        document.getElementById('snapshot-json').textContent = JSON.stringify(snapshot, null, 2);
        document.getElementById('last-updated').textContent = `${{t('last_updated')}}: ${{new Date().toLocaleString()}}`;
      }}

      function createSummaryCard(section, stats) {{
        const total = sumValues(stats);
        const topEntries = Object.entries(stats).sort((left, right) => Number(right[1]) - Number(left[1]));
        const dominant = topEntries[0] || ['empty', 0];
        const dominantShare = total > 0 ? Math.max(8, Math.round((Number(dominant[1]) / total) * 100)) : 8;
        const pills = (topEntries.length ? topEntries : [['empty', 0]])
          .slice(0, 4)
          .map(([name, value]) => `<span class="pill">${{escapeHtml(formatStateLabel(name))}} · ${{value}}</span>`)
          .join('');
        return `
          <article class="card summary-card">
            <div class="eyebrow">${{escapeHtml(sectionLabel(section))}}</div>
            <h3>${{escapeHtml(sectionLabel(section))}} ${{escapeHtml(t('overview_suffix'))}}</h3>
            <div class="metric"><strong>${{total}}</strong><span>${{escapeHtml(t('tracked_items'))}}</span></div>
            <div class="pills">${{pills}}</div>
            <div class="chart"><span style="width:${{dominantShare}}%"></span></div>
          </article>
        `;
      }}

      function renderEndpointCards() {{
        document.getElementById('endpoint-grid').innerHTML = sectionOrder.map((section) => createEndpointCard(section)).join('');
      }}

      function createEndpointCard(section) {{
        const endpoint = `${{apiBase}}/${{resourcePath(section)}}`;
        return `
          <article class="card endpoint-card">
            <div class="eyebrow">${{escapeHtml(t('api_prefix'))}}</div>
            <h3>${{escapeHtml(sectionLabel(section))}}</h3>
            <p style="color:var(--muted);margin:0;line-height:1.7;">${{escapeHtml(t('api_card_body'))}}</p>
            <a class="endpoint-link" href="${{escapeHtml(endpoint)}}" target="_blank" rel="noreferrer">${{escapeHtml(endpoint)}} →</a>
          </article>
        `;
      }}

      function inferSourceKindFromFile(fileName) {{
        const lower = String(fileName || '').toLowerCase();
        if (lower.endsWith('.json')) return 'json';
        if (lower.endsWith('.txt')) return 'text';
        if (lower.endsWith('.csv')) return 'csv';
        return 'markdown';
      }}

      function applySkillSuggestion(suggestion) {{
        if (!suggestion) return;
        document.getElementById('skill-name-input').value = suggestion.name || '';
        document.getElementById('skill-description-input').value = suggestion.description || '';
        document.getElementById('skill-mcp-input').value = (suggestion.required_mcp_servers || []).join('\\n');
      }}

      function markMaterializedSkill(result) {{
        if (!latestIngestionResult || !result) return;
        const suggestions = latestIngestionResult.suggested_skills || [];
        const suggestion = suggestions[result.suggestion_index];
        if (!suggestion) return;
        suggestion.created_skill_id = result.skill && result.skill.id ? result.skill.id : null;
        suggestion.created_skill_name = result.skill && result.skill.name ? result.skill.name : suggestion.name;
        suggestion.bound_step_count = result.bound_step_count || 0;
      }}

      function markMaterializedMcp(result) {{
        if (!latestIngestionResult || !result || !result.mcp_server) return;
        const tooling = latestIngestionResult.tooling_guidance || null;
        if (!tooling) return;
        const serverName = String(result.tool_name || result.mcp_server.name || '').trim().toLowerCase();
        if (!serverName) return;
        const label = result.mcp_server.name || serverName;
        const existing = Array.isArray(tooling.existing_mcp_candidates) ? tooling.existing_mcp_candidates.slice() : [];
        if (!existing.some((item) => String(item || '').split(' (')[0].trim().toLowerCase() === label.toLowerCase())) {{
          existing.push(label);
        }}
        tooling.existing_mcp_candidates = existing;
        tooling.missing_mcp_servers = (tooling.missing_mcp_servers || []).filter((item) => String(item || '').trim().toLowerCase() !== serverName);
      }}

      function renderIngestionGuidance() {{
        const result = latestIngestionResult;
        if (!result) {{
          setIngestionGuidance(`<small>${{escapeHtml(t('ingest_guidance_empty'))}}</small>`);
          return;
        }}
        const notes = (result.parsing_notes || []).map((item) => `<li>${{escapeHtml(item)}}</li>`).join('');
        const tooling = result.tooling_guidance || null;
        const sourceObject = result.source_object || null;
        const sourceObjectHtml = sourceObject && sourceObject.id
          ? `
            <div class="patch-changes">
              <strong>${{escapeHtml(t('ingest_source_saved'))}}</strong>
              <div class="patch-change"><code>${{escapeHtml(sourceObject.id)}}</code><a href="${{escapeHtml(`${{apiBase}}/objects/${{sourceObject.id}}/content`)}}" target="_blank" rel="noreferrer">${{escapeHtml(t('ingest_source_view'))}}</a></div>
              <div class="patch-change"><span>${{escapeHtml(sourceObject.mime_type || 'application/octet-stream')}}</span><span>${{escapeHtml(String(sourceObject.size_bytes || 0))}} bytes</span></div>
            </div>
          `
          : '';
        const toolingHtml = tooling
          ? `
            <div class="patch-review-card">
              <div class="patch-review-head"><div><strong>${{escapeHtml(t('ingest_tooling_summary'))}}</strong><small>${{escapeHtml(tooling.summary || '')}}</small></div></div>
              <div class="patch-changes"><strong>${{escapeHtml(t('ingest_tooling_required_mcp'))}}</strong>${{(tooling.required_mcp_servers || []).map((item) => `<div class="patch-change"><code>${{escapeHtml(item)}}</code><span>MCP</span></div>`).join('') || `<div class="patch-change"><span>n/a</span><span>manual confirm</span></div>`}}</div>
              <div class="patch-changes"><strong>${{escapeHtml(t('ingest_tooling_existing_skills'))}}</strong>${{(tooling.existing_skill_candidates || []).map((item) => `<div class="patch-change"><span>${{escapeHtml(item)}}</span><span>candidate</span></div>`).join('') || `<div class="patch-change"><span>n/a</span><span>new upload recommended</span></div>`}}</div>
              <div class="patch-changes"><strong>${{escapeHtml(t('ingest_tooling_existing_mcp'))}}</strong>${{(tooling.existing_mcp_candidates || []).map((item) => `<div class="patch-change"><span>${{escapeHtml(item)}}</span><span>registered</span></div>`).join('') || `<div class="patch-change"><span>n/a</span><span>draft recommended</span></div>`}}</div>
              <div class="patch-changes"><strong>${{escapeHtml(t('ingest_tooling_actions'))}}</strong>${{(tooling.action_items || []).map((item) => `<div class="patch-change"><span>${{escapeHtml(item)}}</span><span>action</span></div>`).join('')}}</div>
            </div>
            ${{(tooling.tool_requirements || []).map((item) => `
              <div class="patch-review-card">
                <div class="patch-review-head"><div><strong>${{escapeHtml(item.tool_name || 'tool')}}</strong><small>${{escapeHtml(item.purpose || '')}}</small></div></div>
                <div class="patch-changes"><strong>Why</strong><div class="patch-change"><span>${{escapeHtml(item.rationale || '')}}</span><span>${{escapeHtml(item.suggested_skill_name || 'n/a')}}</span></div></div>
                <div class="patch-changes"><strong>Steps</strong>${{(item.related_steps || []).map((step) => `<div class="patch-change"><span>${{escapeHtml(step)}}</span><span>${{escapeHtml(item.suggested_mcp_server || item.tool_name || '')}}</span></div>`).join('')}}</div>
                <div class="action-buttons" style="margin-top:12px;">${{actionButton('action_create_mcp_draft', 'playbook', result.playbook.id, 'materialize-mcp', {{ server_name: item.suggested_mcp_server || item.tool_name || '' }}, true)}}</div>
              </div>
            `).join('')}}
            <div class="patch-changes"><strong>${{escapeHtml(t('ingest_tooling_prompts'))}}</strong></div>
            ${{(tooling.prompt_blocks || []).map((item) => `
              <div class="patch-review-card">
                <div class="patch-review-head"><div><strong>${{escapeHtml(item.title || item.key || 'prompt')}}</strong><small>${{escapeHtml(item.objective || '')}}</small></div></div>
                <pre style="white-space:pre-wrap;overflow:auto;margin:0;">${{escapeHtml(item.prompt || '')}}</pre>
              </div>
            `).join('')}}
          `
          : '';
        const skills = (result.suggested_skills || []).map((item, index) => `
          <div class="patch-review-card">
            <div class="patch-review-head"><div><strong>${{escapeHtml(item.name || `Skill ${{index + 1}}`)}}</strong><small>${{escapeHtml(item.rationale || '')}}</small></div></div>
            <div class="patch-changes"><strong>MCP</strong><div class="patch-change"><span>${{escapeHtml((item.required_mcp_servers || []).join(', ') || 'n/a')}}</span></div></div>
            <div class="patch-changes"><strong>Hint</strong><div class="patch-change"><span>${{escapeHtml(item.approval_hint || 'n/a')}}</span></div></div>
            <div class="action-buttons" style="margin-top:12px;">
              ${{item.created_skill_id
                ? `<span class="pill">${{escapeHtml(item.created_skill_name || item.name)}} · ${{escapeHtml(item.created_skill_id.slice(0, 8))}}</span>`
                : `${{actionButton('action_create_skill_draft', 'playbook', result.playbook.id, 'materialize-skill', {{ suggestion_index: index, bind_to_unassigned_steps: false }})}}${{actionButton('action_create_bound_skill_draft', 'playbook', result.playbook.id, 'materialize-skill', {{ suggestion_index: index, bind_to_unassigned_steps: true }}, true)}}`
              }}
            </div>
          </div>
        `).join('');
        setIngestionGuidance(`
          <strong>${{escapeHtml(result.playbook && result.playbook.name ? result.playbook.name : 'Playbook')}}</strong>
          <small>${{escapeHtml(`steps: ${{result.step_count || 0}}, mcp: ${{(result.detected_mcp_servers || []).join(', ') || 'n/a'}}`)}}</small>
          ${{sourceObjectHtml}}
          <ul style="margin:8px 0 12px 18px;">${{notes || `<li>${{escapeHtml(t('ingest_guidance_empty'))}}</li>`}}</ul>
          ${{toolingHtml}}
          ${{skills || `<small>${{escapeHtml(t('ingest_guidance_empty'))}}</small>`}}
        `);
      }}

      async function fetchJson(path) {{
        const response = await fetch(`${{apiBase}}/${{path}}`);
        if (!response.ok) {{
          throw new Error(`Failed to load ${{path}}: ${{response.status}}`);
        }}
        return await response.json();
      }}

      async function postJson(path, payload) {{
        const response = await fetch(`${{apiBase}}/${{path}}`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload),
        }});
        const data = await response.json().catch(() => ({{}}));
        if (!response.ok) {{
          throw new Error(data.detail || `Failed to submit ${{path}}: ${{response.status}}`);
        }}
        return data;
      }}

      async function putJson(path, payload) {{
        const response = await fetch(`${{apiBase}}/${{path}}`, {{
          method: 'PUT',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload),
        }});
        const data = await response.json().catch(() => ({{}}));
        if (!response.ok) {{
          throw new Error(data.detail || `Failed to update ${{path}}: ${{response.status}}`);
        }}
        return data;
      }}

      function actionRow(title, detail, buttons) {{
        return `<div class="action-row"><strong>${{escapeHtml(title)}}</strong><small>${{escapeHtml(detail)}}</small><div class="action-buttons">${{buttons.join('')}}</div></div>`;
      }}

      function actionButton(labelKey, actionKind, actionTarget, actionName, payload = null, secondary = false) {{
        const payloadAttr = payload ? ` data-payload="${{escapeHtml(JSON.stringify(payload))}}"` : '';
        return `<button class="button${{secondary ? ' secondary' : ''}}" type="button" data-action-kind="${{escapeHtml(actionKind)}}" data-action-target="${{escapeHtml(actionTarget)}}" data-action-name="${{escapeHtml(actionName)}}"${{payloadAttr}}>${{escapeHtml(t(labelKey))}}</button>`;
      }}

      function editorActionButton(section, targetId, labelKey) {{
        return `<button class="button secondary" type="button" data-editor-section="${{escapeHtml(section)}}" data-editor-target="${{escapeHtml(targetId)}}">${{escapeHtml(t(labelKey))}}</button>`;
      }}

      function renderActionCenter() {{
        renderGoalActions();
        renderReviewActions();
        renderLearningActions();
      }}

      function countByStatus(items, field = 'status') {{
        return (items || []).reduce((acc, item) => {{
          const key = String(item && item[field] ? item[field] : 'unknown');
          acc[key] = (acc[key] || 0) + 1;
          return acc;
        }}, {{}});
      }}

      function totalFromCounts(counts) {{
        return Object.values(counts || {{}}).reduce((sum, value) => sum + Number(value || 0), 0);
      }}

      function renderAggregateLines(label, entries) {{
        const rows = entries.map(([key, value]) => `<div class="patch-change"><code>${{escapeHtml(String(key))}}</code><span>${{escapeHtml(String(value))}}</span></div>`).join('');
        return `<div class="patch-changes"><strong>${{escapeHtml(label)}}</strong>${{rows}}</div>`;
      }}

      function aggregateForGoal(goal) {{
        const sessions = (latestResources.sessions || []).filter((item) => item.goal_id === goal.id);
        const supervisor = sessions.find((item) => item.kind === 'supervisor') || null;
        const tasks = (latestResources.tasks || []).filter((item) => item.goal_id === goal.id);
        const taskIds = new Set(tasks.map((item) => item.id));
        const runs = (latestResources.runs || []).filter((item) => taskIds.has(item.task_id));
        const runIds = new Set(runs.map((item) => item.id));
        const reflections = (latestResources.reflections || []).filter((item) => runIds.has(item.run_id));
        const knowledgeUpdates = (latestResources.knowledge_updates || []).filter((item) => item.goal_id === goal.id || runIds.has(item.run_id));
        const acceptances = (latestResources.acceptances || []).filter((item) => item.goal_id === goal.id);
        const fallback = {{
          goal_status: goal.status || 'draft',
          tasks: countByStatus(tasks),
          runs: countByStatus(runs),
          acceptances: countByStatus(acceptances),
          reflections: countByStatus(reflections, 'eval_status'),
          knowledge_updates: countByStatus(knowledgeUpdates),
          session_total: sessions.length,
          child_session_total: sessions.filter((item) => item.parent_session_id).length,
          worker_session_total: sessions.filter((item) => item.kind === 'worker').length,
          waiting_human_runs: runs.filter((item) => item.status === 'waiting_human').length,
          review_tasks: tasks.filter((item) => item.status === 'review').length,
          learned_tasks: tasks.filter((item) => item.status === 'learned').length,
        }};
        const aggregate = (supervisor && supervisor.output_context && supervisor.output_context.aggregate) || fallback;
        const latestEvents = (supervisor && supervisor.output_context && supervisor.output_context.latest_events) || [];
        return {{ supervisor, aggregate, latestEvents, tasks, runs, reflections, knowledgeUpdates, acceptances, sessions }};
      }}

      function renderSupervisorCenter() {{
        const container = document.getElementById('supervisor-summary-rows');
        const goals = latestResources.goals || [];
        if (!goals.length) {{
          container.innerHTML = `<div class="patch-review-card"><strong>${{escapeHtml(t('supervisor_center_title'))}}</strong><small>${{escapeHtml(t('supervisor_center_empty'))}}</small></div>`;
          return;
        }}
        const cards = goals.map((goal) => {{
          const bundle = aggregateForGoal(goal);
          const aggregate = bundle.aggregate || {{}};
          const supervisor = bundle.supervisor;
          const statusLabel = (supervisor && supervisor.status) || goal.status || 'draft';
          const headLines = [
            `${{t('session_goal_summary')}} · ${{aggregate.session_total || 0}} sessions`,
            `${{t('session_children_count')}} · ${{aggregate.child_session_total || 0}}`,
            `${{t('supervisor_center_waiting')}} · ${{aggregate.waiting_human_runs || 0}}`,
            `${{t('supervisor_center_closed_tasks')}} · ${{(aggregate.learned_tasks || 0) + Number((aggregate.tasks || {{}}).done || 0)}}`,
          ];
          const eventEntries = (bundle.latestEvents.length ? bundle.latestEvents : ['n/a']).map((item, index) => [`#${{index + 1}}`, item]);
          const sessionEntries = [
            ['total', aggregate.session_total || 0],
            ['child', aggregate.child_session_total || 0],
            ['worker', aggregate.worker_session_total || 0],
            ['review_tasks', aggregate.review_tasks || 0],
          ];
          const runEntries = Object.entries(aggregate.runs || {{}});
          const learningEntries = [
            ['reflections', totalFromCounts(aggregate.reflections || {{}})],
            ['knowledge_updates', totalFromCounts(aggregate.knowledge_updates || {{}})],
            ['acceptances', totalFromCounts(aggregate.acceptances || {{}})],
            ['published_patches', Number((aggregate.reflections || {{}}).published || 0)],
          ];
          return `<div class="patch-review-card"><div class="patch-review-head"><div><strong>${{escapeHtml(goal.title || goal.id)}}</strong><small>${{escapeHtml(headLines.join('\\n'))}}</small></div><span class="state">${{escapeHtml(formatStateLabel(statusLabel))}}</span></div>${{renderAggregateLines(t('supervisor_center_sessions'), sessionEntries)}}${{renderAggregateLines(t('supervisor_center_runs'), runEntries.length ? runEntries : [['none', 0]])}}${{renderAggregateLines(t('supervisor_center_learning'), learningEntries)}}${{renderAggregateLines(t('supervisor_center_events'), eventEntries)}}</div>`;
        }});
        container.innerHTML = cards.join('');
      }}

      function sessionTitleLine(session) {{
        return `${{session.title || session.id}}`;
      }}

      function sessionDetailLines(session) {{
        const lines = [
          `${{t('session_kind_label')}}: ${{session.kind || ''}}`,
          `${{t('session_status_label')}}: ${{session.status || ''}}`,
        ];
        const sessionRole = session.input_context && session.input_context.session_role;
        if (sessionRole) lines.push(`${{t('session_role_label')}}: ${{sessionRole}}`);
        if (session.task_id) lines.push(`${{t('session_task_label')}}: ${{session.task_id}}`);
        if (session.run_id) lines.push(`${{t('session_run_label')}}: ${{session.run_id}}`);
        if (session.summary) lines.push(`${{t('session_summary_label')}}: ${{session.summary}}`);
        return lines.join('\\n');
      }}

      function renderSessionNode(session, childrenByParent, depth = 0) {{
        const children = childrenByParent[session.id] || [];
        const childrenHtml = children.length
          ? `<div class="session-node-children">${{children.map((child) => renderSessionNode(child, childrenByParent, depth + 1)).join('')}}</div>`
          : '';
        return `<div class="session-node depth-${{depth}}" style="margin-left:${{depth * 4}}px;"><div class="session-node-title"><strong>${{escapeHtml(sessionTitleLine(session))}}</strong><span class="state">${{escapeHtml(formatStateLabel(session.status || 'planned'))}}</span></div><div class="session-node-meta">${{escapeHtml(sessionDetailLines(session))}}</div>${{childrenHtml}}</div>`;
      }}

      function renderSessionTree() {{
        const sessions = latestResources.sessions || [];
        const goals = latestResources.goals || [];
        const container = document.getElementById('session-groups');
        if (!sessions.length) {{
          container.innerHTML = `<div class="session-group"><strong>${{escapeHtml(t('session_goal_summary'))}}</strong><span style="display:block;color:var(--muted);margin-top:8px;">${{escapeHtml(t('session_tree_empty'))}}</span></div>`;
          return;
        }}
        const childrenByParent = {{}};
        for (const session of sessions) {{
          const key = session.parent_session_id || '__root__';
          if (!childrenByParent[key]) childrenByParent[key] = [];
          childrenByParent[key].push(session);
        }}
        for (const key of Object.keys(childrenByParent)) {{
          childrenByParent[key].sort((left, right) => String(left.created_at || '').localeCompare(String(right.created_at || '')));
        }}
        const goalsWithSessions = Array.from(new Set(sessions.map((item) => item.goal_id)));
        container.innerHTML = goalsWithSessions.map((goalId) => {{
          const goal = goals.find((item) => item.id === goalId);
          const goalSessions = sessions.filter((item) => item.goal_id === goalId);
          const rootSessions = goalSessions.filter((item) => !item.parent_session_id);
          const childCount = goalSessions.filter((item) => item.parent_session_id).length;
          const treeHtml = rootSessions.map((item) => renderSessionNode(item, childrenByParent, 0)).join('');
          return `<div class="session-group"><div class="session-group-header"><div><strong>${{escapeHtml(goal ? goal.title : goalId)}}</strong><span>${{escapeHtml(t('session_goal_summary'))}} · ${{goalSessions.length}} sessions</span></div><span class="pill">${{escapeHtml(t('session_children_count'))}} · ${{childCount}}</span></div><div class="session-tree">${{treeHtml}}</div></div>`;
        }}).join('');
      }}

      function playbookForReflection(reflection) {{
        const run = (latestResources.runs || []).find((item) => item.id === reflection.run_id);
        if (!run) return null;
        const task = (latestResources.tasks || []).find((item) => item.id === run.task_id);
        if (!task) return null;
        return (latestResources.playbooks || []).find((item) => item.id === task.playbook_id) || null;
      }}

      function taskForReflection(reflection) {{
        const run = (latestResources.runs || []).find((item) => item.id === reflection.run_id);
        if (!run) return null;
        return (latestResources.tasks || []).find((item) => item.id === run.task_id) || null;
      }}

      function renderPatchChange(change) {{
        return `<div class="patch-change"><code>${{escapeHtml(change.op || 'change')}}</code><span>${{escapeHtml(change.description || JSON.stringify(change))}}</span></div>`;
      }}

      function patchReviewButtons(reflection) {{
        const buttons = [];
        if (reflection.eval_status === 'proposed') {{
          buttons.push(actionButton('action_evaluate_reflection', 'reflection', reflection.id, 'evaluate'));
        }}
        if (reflection.eval_status === 'approved' && reflection.approval_status !== 'approved') {{
          buttons.push(actionButton('action_approve_reflection', 'reflection', reflection.id, 'approve'));
        }}
        if (reflection.eval_status !== 'published' && reflection.approval_status !== 'rejected') {{
          buttons.push(actionButton('action_reject_reflection', 'reflection', reflection.id, 'reject', null, true));
        }}
        if (reflection.eval_status === 'approved' && reflection.approval_status === 'approved') {{
          buttons.push(actionButton('action_publish_reflection', 'reflection', reflection.id, 'publish'));
        }}
        return buttons;
      }}

      function renderPatchReviews() {{
        const reflections = (latestResources.reflections || []).filter((item) => item.proposal && item.proposal.proposal_type === 'sop_patch');
        const container = document.getElementById('patch-review-rows');
        if (!reflections.length) {{
          container.innerHTML = `<div class="patch-review-card"><strong>${{escapeHtml(t('patch_review_title'))}}</strong><small>${{escapeHtml(t('patch_review_empty'))}}</small></div>`;
          return;
        }}
        const cards = reflections.map((reflection) => {{
          const playbook = playbookForReflection(reflection);
          const task = taskForReflection(reflection);
          const evaluation = (reflection.proposal && reflection.proposal.evaluation) || {{}};
          const changes = Array.isArray(reflection.proposal && reflection.proposal.changes) ? reflection.proposal.changes : [];
          const changeHtml = changes.length
            ? changes.map((change) => renderPatchChange(change)).join('')
            : `<div class="patch-change"><span>${{escapeHtml(t('patch_review_no_changes'))}}</span></div>`;
          const buttons = patchReviewButtons(reflection);
          const playbookLabel = playbook ? `${{playbook.name}} (${{playbook.version}})` : 'n/a';
          const taskLabel = task ? `${{t('session_task_label')}}: ${{task.name || task.id}}` : '';
          const metaLines = [
            `${{t('patch_review_target_playbook')}}: ${{playbookLabel}}`,
            `${{t('patch_review_source_run')}}: ${{reflection.run_id}}`,
          ];
          if (taskLabel) metaLines.push(taskLabel);
          const targetVersion = reflection.published_target_version || (playbook ? playbook.version : 'n/a');
          const scoreLabel = evaluation.score === undefined || evaluation.score === null ? 'n/a' : String(evaluation.score);
          const replayCount = Array.isArray(evaluation.replay_run_ids) ? evaluation.replay_run_ids.length : 0;
          return `<div class="patch-review-card"><div class="patch-review-head"><div><strong>${{escapeHtml(reflection.summary || reflection.id)}}</strong><small>${{escapeHtml(metaLines.join('\\n'))}}</small></div><span class="state">${{escapeHtml(formatStateLabel(reflection.eval_status || 'proposed'))}} / ${{escapeHtml(reflection.approval_status || 'pending')}}</span></div><div class="patch-meta"><div>${{escapeHtml(t('patch_review_target_version'))}}: ${{escapeHtml(String(targetVersion))}}</div><div>${{escapeHtml(t('patch_review_score'))}}: ${{escapeHtml(scoreLabel)}}</div><div>${{escapeHtml(t('patch_review_replay_count'))}}: ${{escapeHtml(String(replayCount))}}</div></div><div class="patch-changes"><strong>${{escapeHtml(t('patch_review_changes'))}}</strong>${{changeHtml}}</div><div class="action-buttons">${{buttons.join('')}}</div></div>`;
        }});
        container.innerHTML = cards.join('');
      }}

      async function refreshAuthoringPacks(skills) {{
        const draftSkills = (skills || []).filter((item) => item.status === 'draft');
        const results = await Promise.allSettled(draftSkills.map((item) => fetchJson(`skills/${{item.id}}/authoring-pack`)));
        latestAuthoringPacks = {{}};
        results.forEach((result, index) => {{
          if (result.status === 'fulfilled') {{
            latestAuthoringPacks[draftSkills[index].id] = result.value;
          }}
        }});
      }}

      function renderSkillAuthoringWizard() {{
        const container = document.getElementById('authoring-wizard-rows');
        if (!container) return;
        const draftSkills = (latestResources.skills || []).filter((item) => item.status === 'draft');
        if (!draftSkills.length) {{
          container.innerHTML = `<div class="patch-review-card"><strong>${{escapeHtml(t('authoring_wizard_title'))}}</strong><small>${{escapeHtml(t('authoring_wizard_empty'))}}</small></div>`;
          return;
        }}
        container.innerHTML = draftSkills.map((skill) => {{
          const pack = latestAuthoringPacks[skill.id] || null;
          const playbookName = pack && pack.playbook_name ? pack.playbook_name : ((latestResources.playbooks || []).find((item) => item.id === (skill.evaluation_policy || {{}}).playbook_id) || {{}}).name || 'n/a';
          const checklist = pack && pack.checklist && pack.checklist.length ? pack.checklist : (((skill.evaluation_policy || {{}}).sample_task_names) || []);
          const signals = pack && pack.risk_signals && pack.risk_signals.length ? pack.risk_signals : [((skill.approval_policy || {{}}).hint) || 'n/a'];
          const notes = pack && pack.notes && pack.notes.length ? pack.notes : [skill.description || 'n/a'];
          return `<div class="patch-review-card"><div class="patch-review-head"><div><strong>${{escapeHtml(skill.name || skill.id)}}</strong><small>${{escapeHtml(`${{t('authoring_wizard_playbook')}}: ${{playbookName}}
${{t('skill_version_servers')}}: ${{(skill.required_mcp_servers || []).join(', ') || 'n/a'}}`)}}</small></div><span class="state">${{escapeHtml(formatStateLabel(skill.status || 'draft'))}}</span></div>${{renderAggregateLines(t('authoring_wizard_checklist'), checklist.length ? checklist.map((item) => [item, 'step']) : [['none', 'n/a']])}}${{renderAggregateLines(t('authoring_wizard_signals'), signals.length ? signals.map((item) => [item, 'risk']) : [['none', 'n/a']])}}${{renderAggregateLines(t('authoring_wizard_notes'), notes.length ? notes.map((item) => [item, 'note']) : [['none', 'n/a']])}}<div class="action-buttons">${{actionButton('action_apply_authoring_pack', 'skill', skill.id, 'apply-authoring-pack')}}${{editorActionButton('skills', skill.id, 'action_open_editor')}}</div></div>`;
        }}).join('');
      }}

      function renderSkillVersions() {{
        const skills = latestResources.skills || [];
        const container = document.getElementById('skill-version-rows');
        if (!skills.length) {{
          container.innerHTML = `<div class="skill-family-card"><strong>${{escapeHtml(t('skill_version_family'))}}</strong><small>${{escapeHtml(t('skill_version_empty'))}}</small></div>`;
          return;
        }}
        const families = {{}};
        for (const skill of skills) {{
          if (!families[skill.name]) families[skill.name] = [];
          families[skill.name].push(skill);
        }}
        const sortVersion = (left, right) => String(left.version || '').localeCompare(String(right.version || ''), undefined, {{ numeric: true, sensitivity: 'base' }});
        const familyCards = Object.entries(families).sort((left, right) => left[0].localeCompare(right[0])).map(([name, items]) => {{
          items.sort(sortVersion).reverse();
          const active = items.find((item) => item.status === 'active');
          const versionsHtml = items.map((item) => {{
            const detailLines = [
              `${{t('skill_version_current')}}: ${{item.version || 'n/a'}}`,
              `${{t('session_status_label')}}: ${{item.status || ''}}`,
              `${{t('skill_version_rollback')}}: ${{item.rollback_version || 'n/a'}}`,
              `${{t('skill_version_servers')}}: ${{(item.required_mcp_servers || []).join(', ') || 'n/a'}}`,
            ];
            const buttons = [actionButton('action_create_skill_version', 'skill', item.id, 'create-version', null, true)];
            if (item.status !== 'active') buttons.push(actionButton('action_activate_skill', 'skill', item.id, 'activate'));
            if (item.status !== 'deprecated') buttons.push(actionButton('action_deprecate_skill', 'skill', item.id, 'deprecate', null, true));
            if (item.rollback_version || items.some((candidate) => candidate.version < item.version)) buttons.push(actionButton('action_rollback_skill', 'skill', item.id, 'rollback'));
            return `<div class="skill-version-item"><strong>${{escapeHtml(name)}} · v${{escapeHtml(item.version || 'n/a')}}</strong><small>${{escapeHtml(detailLines.join('\\n'))}}</small><div class="action-buttons">${{buttons.join('')}}</div></div>`;
          }}).join('');
          return `<div class="skill-family-card"><div class="patch-review-head"><div><strong>${{escapeHtml(name)}}</strong><small>${{escapeHtml(t('skill_version_family'))}} · ${{items.length}} versions</small></div><span class="pill">${{escapeHtml(t('skill_version_current'))}} · ${{escapeHtml(active ? active.version : 'n/a')}}</span></div><div class="skill-version-list">${{versionsHtml}}</div></div>`;
        }});
        container.innerHTML = familyCards.join('');
      }}

      function renderGoalActions() {{
        const rows = (latestResources.goals || []).slice(0, 6).map((goal) => actionRow(
          goal.title || goal.id,
          `${{t('action_kind_goal')}} · ${{goal.status || ''}} · ${{goal.id}}`,
          [
            actionButton('action_plan', 'goal', goal.id, 'plan', null, true),
            actionButton('action_dispatch', 'goal', goal.id, 'dispatch', null, true),
            actionButton('action_autopilot', 'goal', goal.id, 'autopilot'),
          ],
        ));
        document.getElementById('goal-action-rows').innerHTML = rows.length ? rows.join('') : actionRow(t('goal_ops_title'), t('goal_ops_empty'), []);
      }}

      function renderReviewActions() {{
        const rows = [];
        for (const run of latestResources.runs || []) {{
          const task = (latestResources.tasks || []).find((item) => item.id === run.task_id);
          if (!task) continue;
          if (run.status === 'waiting_human') {{
            rows.push(actionRow(
              task.name || run.id,
              `${{t('action_kind_run')}} · waiting_human · ${{run.id}}`,
              [
                actionButton('action_approve_run', 'run', run.id, 'approve'),
                actionButton('action_reject_run', 'run', run.id, 'reject', null, true),
              ],
            ));
          }} else if (run.status === 'queued') {{
            rows.push(actionRow(
              task.name || run.id,
              `${{t('action_kind_run')}} · queued · ${{run.id}}`,
              [actionButton('action_execute', 'run', run.id, 'execute')],
            ));
          }}
        }}
        for (const task of latestResources.tasks || []) {{
          if (!['review', 'done'].includes(task.status)) continue;
          rows.push(actionRow(
            task.name || task.id,
            `${{t('action_kind_task')}} · ${{task.status}} · ${{task.id}}`,
            [
              actionButton('action_accept_task', 'task', task.id, 'accept', {{ accepted: true }}),
              actionButton('action_reject_task', 'task', task.id, 'accept', {{ accepted: false }}, true),
            ],
          ));
        }}
        document.getElementById('review-action-rows').innerHTML = rows.length ? rows.join('') : actionRow(t('review_ops_title'), t('review_ops_empty'), []);
      }}

      function renderLearningActions() {{
        const rows = [];
        for (const item of latestResources.knowledge_updates || []) {{
          if (item.status !== 'proposed') continue;
          rows.push(actionRow(
            item.title || item.id,
            `${{t('action_kind_knowledge')}} · ${{item.status}} · ${{item.id}}`,
            [
              actionButton('action_apply_knowledge', 'knowledge', item.id, 'apply'),
              actionButton('action_reject_knowledge', 'knowledge', item.id, 'reject', null, true),
            ],
          ));
        }}
        for (const item of latestResources.reflections || []) {{
          const buttons = [];
          if (item.eval_status === 'proposed') {{
            buttons.push(actionButton('action_evaluate_reflection', 'reflection', item.id, 'evaluate'));
          }}
          if (item.eval_status === 'approved' && item.approval_status !== 'approved') {{
            buttons.push(actionButton('action_approve_reflection', 'reflection', item.id, 'approve'));
          }}
          if (item.eval_status !== 'published' && item.approval_status !== 'rejected') {{
            buttons.push(actionButton('action_reject_reflection', 'reflection', item.id, 'reject', null, true));
          }}
          if (item.eval_status === 'approved' && item.approval_status === 'approved') {{
            buttons.push(actionButton('action_publish_reflection', 'reflection', item.id, 'publish'));
          }}
          if (!buttons.length) continue;
          rows.push(actionRow(
            item.summary || item.id,
            `${{t('action_kind_reflection')}} · ${{item.eval_status || ''}} / ${{item.approval_status || ''}} · ${{item.id}}`,
            buttons,
          ));
        }}
        document.getElementById('learning-action-rows').innerHTML = rows.length ? rows.join('') : actionRow(t('learning_ops_title'), t('learning_ops_empty'), []);
      }}

      async function runAction(actionKind, actionTarget, actionName, payload = null) {{
        const body = payload && Object.keys(payload).length ? payload : {{}};
        if (actionKind === 'playbook' && actionName === 'materialize-skill') {{
          return await postJson(`playbooks/${{actionTarget}}/skill-drafts`, body);
        }}
        if (actionKind === 'playbook' && actionName === 'materialize-mcp') {{
          return await postJson(`playbooks/${{actionTarget}}/mcp-drafts`, body);
        }}
        if (actionKind === 'goal') {{
          return await postJson(`goals/${{actionTarget}}/${{actionName}}`, body);
        }}
        if (actionKind === 'run') {{
          return await postJson(`runs/${{actionTarget}}/${{actionName}}`, body);
        }}
        if (actionKind === 'reflection') {{
          return await postJson(`reflections/${{actionTarget}}/${{actionName}}`, body);
        }}
        if (actionKind === 'skill') {{
          return await postJson(`skills/${{actionTarget}}/${{actionName}}`, body);
        }}
        if (actionKind === 'knowledge') {{
          return await postJson(`knowledge-updates/${{actionTarget}}/${{actionName}}`, body);
        }}
        if (actionKind === 'task' && actionName === 'accept') {{
          const accepted = Boolean(payload && payload.accepted);
          const task = (latestResources.tasks || []).find((item) => item.id === actionTarget);
          return await postJson(`tasks/${{actionTarget}}/accept`, {{
            criteria: task ? [task.description || task.name] : [],
            reviewer_id: 'dashboard-reviewer',
            accepted,
            notes: accepted ? 'Accepted in dashboard action center' : 'Rejected in dashboard action center',
            findings: [],
          }});
          return;
        }}
        throw new Error(`Unsupported action: ${{actionKind}}/${{actionName}}`);
      }}

      function summarizeRunToolCalls(run) {{
        const calls = (((run || {{}}).metrics || {{}}).tool_calls) || [];
        return calls.map((item, index) => [
          `#${{index + 1}} · ${{item.tool || 'tool'}}`,
          item.action || item.request_format || 'call',
        ]);
      }}

      function stringifyCompact(value, fallback = 'n/a') {{
        if (value === undefined || value === null) return fallback;
        try {{
          return JSON.stringify(value, null, 2);
        }} catch (error) {{
          return String(value);
        }}
      }}

      function renderExecutionInspector() {{
        const container = document.getElementById('execution-inspector-rows');
        const runs = [...(latestResources.runs || [])]
          .sort((left, right) => String(right.created_at || '').localeCompare(String(left.created_at || '')))
          .filter((run) => run.metrics || run.trace_id)
          .slice(0, 4);
        if (!runs.length) {{
          container.innerHTML = `<div class="patch-review-card"><strong>${{escapeHtml(t('execution_inspector_title'))}}</strong><small>${{escapeHtml(t('execution_inspector_empty'))}}</small></div>`;
          return;
        }}
        const cards = runs.map((run) => {{
          const task = (latestResources.tasks || []).find((item) => item.id === run.task_id);
          const metrics = run.metrics || {{}};
          const config = metrics.openai_config || {{}};
          const toolCalls = summarizeRunToolCalls(run);
          const requestCall = ((metrics.tool_calls || []).find((item) => item.action === 'request_prepared')) || null;
          const responseCall = ((metrics.tool_calls || []).find((item) => item.action === 'response_received')) || null;
          const headLines = [
            `${{t('action_kind_run')}} · ${{run.id}}`,
            `${{t('session_task_label')}}: ${{task ? (task.name || task.id) : run.task_id}}`,
            `mode: ${{metrics.openai_mode || metrics.adapter || 'n/a'}}`,
            `model: ${{config.model || 'n/a'}}`,
          ];
          const requestSummary = requestCall ? stringifyCompact(requestCall.payload, 'n/a').slice(0, 900) : 'n/a';
          const responseSummary = stringifyCompact({{
            output_text: metrics.output_text || '',
            response_id: metrics.openai_response_id || (responseCall && responseCall.response_id) || null,
            usage: metrics.openai_usage || (responseCall && responseCall.usage) || {{}},
            request_format: metrics.openai_request_format || null,
            request_url: metrics.openai_request_url || null,
          }}, 'n/a').slice(0, 900);
          return `<div class="patch-review-card"><div class="patch-review-head"><div><strong>${{escapeHtml(task ? (task.name || run.id) : run.id)}}</strong><small>${{escapeHtml(headLines.join('\\n'))}}</small></div><span class="state">${{escapeHtml(formatStateLabel(run.status || 'queued'))}}</span></div>${{renderAggregateLines(t('execution_inspector_calls'), toolCalls.length ? toolCalls : [['none', 'n/a']])}}<div class="patch-changes"><strong>${{escapeHtml(t('execution_inspector_request'))}}</strong><div class="patch-change"><span><pre style="white-space:pre-wrap;margin:0;">${{escapeHtml(requestSummary)}}</pre></span></div></div><div class="patch-changes"><strong>${{escapeHtml(t('execution_inspector_response'))}}</strong><div class="patch-change"><span><pre style="white-space:pre-wrap;margin:0;">${{escapeHtml(responseSummary)}}</pre></span></div></div></div>`;
        }});
        container.innerHTML = cards.join('');
      }}

      function focusCard(title, lines, pills = []) {{
        return `<article class="focus-card"><strong>${{escapeHtml(title)}}</strong><small>${{escapeHtml(lines.join('\\n'))}}</small><div class="focus-meta">${{pills.map((item) => `<span class="pill">${{escapeHtml(item)}}</span>`).join('')}}</div></article>`;
      }}

      function routeResourceSections(route) {{
        if (route === 'playbooks') return ['playbooks', 'skills', 'mcp_servers', 'reflections'];
        if (route === 'skills') return ['skills', 'mcp_servers', 'playbooks'];
        if (route === 'mcp') return ['mcp_servers', 'skills', 'playbooks'];
        if (route === 'knowledge') return ['knowledge_bases', 'knowledge_updates'];
        if (route === 'tasks') return ['tasks', 'runs', 'acceptances'];
        if (route === 'sessions') return ['sessions', 'runs', 'events'];
        if (route === 'learning') return ['reflections', 'knowledge_updates', 'skills'];
        if (route === 'approvals') return ['runs', 'knowledge_updates', 'reflections', 'tasks'];
        if (route === 'prompts') return ['playbooks', 'skills', 'mcp_servers'];
        if (route === 'goals') return ['goals', 'tasks', 'sessions'];
        return sectionOrder;
      }}

      function renderRouteFocus() {{
        const titleNode = document.getElementById('route-focus-title');
        const subtitleNode = document.getElementById('route-focus-subtitle');
        const container = document.getElementById('route-focus-rows');
        if (!titleNode || !subtitleNode || !container) return;
        titleNode.textContent = t('route_focus_title');
        subtitleNode.textContent = t('route_focus_subtitle');
        const cards = [];
        if (currentRoute === 'playbooks') {{
          const playbooks = latestResources.playbooks || [];
          const latest = latestIngestionResult || null;
          const reflections = (latestResources.reflections || []).filter((item) => item.proposal && item.proposal.proposal_type === 'sop_patch');
          const tooling = latest && latest.tooling_guidance ? latest.tooling_guidance : null;
          cards.push(focusCard(t('nav_playbooks'), [
            `${{t('focus_total')}}: ${{playbooks.length}}`,
            `${{t('focus_draft')}}: ${{playbooks.filter((item) => item.status === 'draft').length}}`,
            `${{t('focus_active')}}: ${{playbooks.filter((item) => item.status === 'compiled' || item.status === 'active').length}}`,
          ], [
            `compiled · ${{playbooks.filter((item) => item.status === 'compiled').length}}`,
            `active · ${{playbooks.filter((item) => item.status === 'active').length}}`,
          ]));
          cards.push(focusCard(t('focus_latest'), latest ? [
            `${{latest.playbook && latest.playbook.name ? latest.playbook.name : 'n/a'}}`,
            `steps: ${{latest.step_count || 0}}`,
            `mcp: ${{(latest.detected_mcp_servers || []).join(', ') || 'n/a'}}`,
          ] : [t('route_placeholder_body')], latest ? [
            `${{t('focus_suggested_skills')}} · ${{(latest.suggested_skills || []).length}}`,
          ] : []));
          cards.push(focusCard(t('focus_missing_mcp'), tooling ? [
            `${{(tooling.missing_mcp_servers || []).join(', ') || 'n/a'}}`,
            `${{t('focus_suggested_skills')}}: ${{(tooling.suggested_skill_names || []).join(', ') || 'n/a'}}`,
          ] : ['n/a'], tooling ? [
            `${{t('focus_missing_mcp')}} · ${{(tooling.missing_mcp_servers || []).length}}`,
          ] : []));
          cards.push(focusCard(t('patch_review_title'), [
            `${{t('focus_proposed')}}: ${{reflections.filter((item) => item.eval_status === 'proposed').length}}`,
            `${{t('focus_issues')}}: ${{reflections.filter((item) => item.eval_status === 'rejected').length}}`,
          ], [
            `published · ${{reflections.filter((item) => item.eval_status === 'published').length}}`,
          ]));
        }} else if (currentRoute === 'skills') {{
          const skills = latestResources.skills || [];
          const draftSkills = skills.filter((item) => item.status === 'draft');
          const activeSkills = skills.filter((item) => item.status === 'active');
          const dependencyCount = new Set(skills.flatMap((item) => item.required_mcp_servers || [])).size;
          cards.push(focusCard(t('nav_skills'), [
            `${{t('focus_total')}}: ${{skills.length}}`,
            `${{t('focus_draft')}}: ${{draftSkills.length}}`,
            `${{t('focus_active')}}: ${{activeSkills.length}}`,
          ], [
            `${{t('focus_dependencies')}} · ${{dependencyCount}}`,
          ]));
          cards.push(focusCard(t('authoring_wizard_title'), [
            `${{t('focus_pending')}}: ${{draftSkills.length}}`,
            `${{t('focus_review')}}: ${{Object.keys(latestAuthoringPacks || {{}}).length}}`,
          ], [
            `packs · ${{Object.keys(latestAuthoringPacks || {{}}).length}}`,
          ]));
          cards.push(focusCard(t('skill_version_title'), [
            `${{t('focus_active')}}: ${{activeSkills.length}}`,
            `${{t('focus_issues')}}: ${{skills.filter((item) => item.status === 'deprecated').length}}`,
          ], [
            `families · ${{new Set(skills.map((item) => item.name)).size}}`,
          ]));
          cards.push(focusCard(t('nav_mcp'), [
            `${{t('focus_dependencies')}}: ${{dependencyCount}}`,
            `${{t('focus_missing_mcp')}}: ${{skills.filter((item) => (item.required_mcp_servers || []).length === 0).length}}`,
          ]));
        }} else if (currentRoute === 'approvals') {{
          const runs = latestResources.runs || [];
          const reflections = latestResources.reflections || [];
          const updates = latestResources.knowledge_updates || [];
          const tasks = latestResources.tasks || [];
          cards.push(focusCard(t('nav_approvals'), [
            `${{t('focus_waiting')}}: ${{runs.filter((item) => item.status === 'waiting_human').length}}`,
            `${{t('focus_review')}}: ${{tasks.filter((item) => item.status === 'review').length}}`,
          ]));
          cards.push(focusCard(t('review_ops_title'), [
            `${{t('focus_waiting')}}: ${{runs.filter((item) => item.status === 'waiting_human').length}}`,
            `${{t('focus_issues')}}: ${{runs.filter((item) => item.status === 'failed').length}}`,
          ]));
          cards.push(focusCard(t('patch_review_title'), [
            `${{t('focus_proposed')}}: ${{reflections.filter((item) => item.eval_status === 'proposed').length}}`,
            `${{t('focus_review')}}: ${{reflections.filter((item) => item.eval_status === 'approved' && item.approval_status !== 'approved').length}}`,
          ]));
          cards.push(focusCard(t('learning_ops_title'), [
            `${{t('focus_proposed')}}: ${{updates.filter((item) => item.status === 'proposed').length}}`,
            `${{t('focus_issues')}}: ${{updates.filter((item) => item.status === 'rejected').length}}`,
          ]));
        }} else if (currentRoute === 'prompts') {{
          const blocks = (latestIngestionResult && latestIngestionResult.tooling_guidance && latestIngestionResult.tooling_guidance.prompt_blocks) || [];
          cards.push(focusCard(t('nav_prompts'), [
            `${{t('focus_total')}}: ${{blocks.length}}`,
            `${{t('focus_latest')}}: ${{latestIngestionResult && latestIngestionResult.playbook ? latestIngestionResult.playbook.name : 'n/a'}}`,
          ]));
        }} else {{
          const sectionMap = routeResourceSections(currentRoute);
          cards.push(...sectionMap.slice(0, 4).map((section) => focusCard(sectionLabel(section), [
            `${{t('focus_total')}}: ${{sumValues(currentSnapshot[section] || {{}})}}`,
            `${{t('focus_issues')}}: ${{Object.entries(currentSnapshot[section] || {{}}).filter(([key]) => ['blocked', 'failed', 'error', 'rejected'].includes(String(key))).reduce((sum, [, value]) => sum + Number(value || 0), 0)}}`,
          ], Object.entries(currentSnapshot[section] || {{}}).slice(0, 2).map(([key, value]) => `${{key}} · ${{value}}`))));
        }}
        container.innerHTML = cards.join('');
      }}


      function renderResourceRows(payloads) {{
        latestResources = payloads;
        const rows = [];
        const sectionNames = currentRoute === 'dashboard'
          ? sectionOrder
          : routeResourceSections(currentRoute).filter((section, index, list) => list.indexOf(section) === index);
        for (const resourceName of sectionNames) {{
          const label = sectionLabel(resourceName);
          const singular = resourceSingular[resourceName] || label;
          const items = Array.isArray(payloads[resourceName]) ? payloads[resourceName].slice(0, 3) : [];
          if (!items.length) {{
            rows.push(`<div class="row"><div><strong>${{escapeHtml(label)}} · ${{escapeHtml(t('resource_empty_suffix'))}}</strong><small>${{escapeHtml(resourceName)}} ${{escapeHtml(t('resource_empty_body'))}}</small></div><span class="state">${{escapeHtml(t('idle'))}}</span></div>`);
            continue;
          }}
          for (const item of items) {{
            const title = item.title || item.name || item.summary || item.id || t('resource_id_fallback');
            const state = item.status || item.eval_status || item.kind || t('idle');
            rows.push(`<div class="row"><div><strong>${{escapeHtml(title)}}</strong><small>${{escapeHtml(singular)}} · ${{escapeHtml(item.id || t('resource_id_fallback'))}}</small></div><span class="state">${{escapeHtml(formatStateLabel(state))}}</span></div>`);
          }}
        }}
        document.getElementById('resource-rows').innerHTML = rows.join('');
      }}

      function populateSelect(elementId, items, labelBuilder, options = {{}}) {{
        const element = document.getElementById(elementId);
        if (!element) return;
        const includeBlank = options.includeBlank !== false;
        const blankLabel = options.blankLabel || t('optional_none');
        const current = element.value;
        const values = [];
        if (includeBlank) {{
          values.push(`<option value="">${{escapeHtml(blankLabel)}}</option>`);
        }}
        for (const item of items || []) {{
          values.push(`<option value="${{escapeHtml(item.id)}}">${{escapeHtml(labelBuilder(item))}}</option>`);
        }}
        element.innerHTML = values.join('');
        if ([...element.options].some((option) => option.value === current)) {{
          element.value = current;
        }}
      }}

      function renderWorkbenchOptions() {{
        populateSelect('playbook-goal-input', latestResources.goals || [], (item) => `${{item.title}} · ${{item.id.slice(0, 8)}}`);
        populateSelect('ingest-playbook-goal-input', latestResources.goals || [], (item) => `${{item.title}} · ${{item.id.slice(0, 8)}}`);
        populateSelect('knowledge-goal-input', latestResources.goals || [], (item) => `${{item.title}} · ${{item.id.slice(0, 8)}}`);
        populateSelect('task-goal-input', latestResources.goals || [], (item) => `${{item.title}} · ${{item.id.slice(0, 8)}}`, {{ includeBlank: false }});
        populateSelect('task-playbook-input', latestResources.playbooks || [], (item) => `${{item.name}} · ${{item.id.slice(0, 8)}}`, {{ includeBlank: false }});
        populateSelect('task-skill-input', latestResources.skills || [], (item) => `${{item.name}} · ${{item.id.slice(0, 8)}}`);
      }}

      function currentEditorSection() {{
        return document.getElementById('editor-resource-type').value || editableSections[0];
      }}

      function currentEditorItem() {{
        const section = currentEditorSection();
        const itemId = document.getElementById('editor-resource-id').value;
        return (latestResources[section] || []).find((item) => item.id === itemId) || null;
      }}

      function sanitizeEditableItem(section, item) {{
        if (!item) return {{}};
        if (section === 'goals') {{
          return {{
            title: item.title,
            objective: item.objective,
            constraints: item.constraints || [],
            definition_of_done: item.definition_of_done || [],
            risk_level: item.risk_level,
            budget_amount: item.budget_amount,
            budget_currency: item.budget_currency,
            due_at: item.due_at,
            owner_id: item.owner_id,
          }};
        }}
        if (section === 'playbooks') {{
          return {{
            name: item.name,
            source_kind: item.source_kind,
            source_uri: item.source_uri,
            goal_id: item.goal_id,
            compiled_spec: item.compiled_spec || {{}},
          }};
        }}
        if (section === 'skills') {{
          return {{
            name: item.name,
            description: item.description,
            input_schema: item.input_schema || {{}},
            output_schema: item.output_schema || {{}},
            required_mcp_servers: item.required_mcp_servers || [],
            approval_policy: item.approval_policy || {{}},
            evaluation_policy: item.evaluation_policy || {{}},
            rollback_version: item.rollback_version,
            version: item.version,
            status: item.status,
          }};
        }}
        if (section === 'mcp_servers') {{
          return {{
            name: item.name,
            transport: item.transport,
            endpoint: item.endpoint,
            scopes: item.scopes || [],
            auth_config: item.auth_config || {{}},
            status: item.status,
          }};
        }}
        if (section === 'knowledge_bases') {{
          return {{
            name: item.name,
            description: item.description,
            content: item.content,
            tags: item.tags || [],
            source_uri: item.source_uri,
            goal_id: item.goal_id,
            status: item.status,
          }};
        }}
        return {{
          goal_id: item.goal_id,
          playbook_id: item.playbook_id,
          name: item.name,
          description: item.description,
          depends_on: item.depends_on || [],
          knowledge_base_ids: item.knowledge_base_ids || [],
          assigned_skill_id: item.assigned_skill_id,
          approval_required: item.approval_required,
          queue_name: item.queue_name,
          priority: item.priority,
          parent_task_id: item.parent_task_id,
        }};
      }}

      function renderEditorMeta(item) {{
        const meta = document.getElementById('editor-meta');
        if (!item) {{
          meta.textContent = t('editor_status_ready');
          return;
        }}
        meta.textContent = [
          `id: ${{item.id}}`,
          `created_at: ${{item.created_at || ''}}`,
          `updated_at: ${{item.updated_at || ''}}`,
          `status: ${{item.status || item.eval_status || item.kind || ''}}`,
        ].join('\\n');
      }}

      function refreshEditorResourceOptions() {{
        populateSelect('editor-resource-type', editableSections.map((section) => ({{ id: section, label: sectionLabel(section) }})), (item) => item.label, {{ includeBlank: false }});
        const section = currentEditorSection();
        populateSelect('editor-resource-id', latestResources[section] || [], (item) => `${{item.title || item.name || item.id}} · ${{item.id.slice(0, 8)}}`, {{ includeBlank: false }});
        loadEditorSelection(false);
      }}

      function loadEditorSelection(updateStatus = true) {{
        const item = currentEditorItem();
        document.getElementById('editor-payload-input').value = JSON.stringify(sanitizeEditableItem(currentEditorSection(), item), null, 2);
        renderEditorMeta(item);
        if (updateStatus) {{
          document.getElementById('editor-status').textContent = t('editor_status_ready');
        }}
      }}

      async function saveEditorSelection() {{
        const section = currentEditorSection();
        const item = currentEditorItem();
        if (!item) {{
          throw new Error(currentLanguage === 'zh' ? '没有可编辑实体' : 'No editable entity selected');
        }}
        const payload = JSON.parse(document.getElementById('editor-payload-input').value || '{{}}');
        await putJson(`${{resourcePath(section)}}/${{item.id}}`, payload);
      }}

      async function refresh() {{
        let board = currentSnapshot || {{}};
        try {{
          board = await fetchJson('board');
        }} catch (error) {{
          showBootError(new Error(`Failed to load board: ${{error.message}}`));
        }}
        const resourceResults = await Promise.allSettled(sectionOrder.map((section) => fetchJson(resourcePath(section))));
        const payloads = {{ ...latestResources }};
        const failures = [];
        resourceResults.forEach((result, index) => {{
          const section = sectionOrder[index];
          if (result.status === 'fulfilled') {{
            payloads[section] = result.value;
          }} else {{
            payloads[section] = payloads[section] || [];
            failures.push(`${{section}}: ${{result.reason && result.reason.message ? result.reason.message : String(result.reason)}}`);
          }}
        }});
        renderSummary(board);
        renderResourceRows(payloads);
        renderWorkbenchOptions();
        refreshEditorResourceOptions();
        renderActionCenter();
        renderSupervisorCenter();
        renderSkillVersions();
        renderPatchReviews();
        renderSessionTree();
        renderSkillAuthoringWizard();
        renderExecutionInspector();
        if (failures.length) {{
          showBootError(new Error(`Partial API load failure: ${{failures.join('; ')}}`));
        }} else {{
          clearBootError();
        }}
      }}

      async function handleGoalSubmit(event) {{
        event.preventDefault();
        await postJson('goals', {{
          title: document.getElementById('goal-title-input').value.trim(),
          objective: document.getElementById('goal-objective-input').value.trim(),
          constraints: splitLines(document.getElementById('goal-constraints-input').value),
          definition_of_done: splitLines(document.getElementById('goal-dod-input').value),
        }});
        event.target.reset();
      }}

      async function handlePlaybookSubmit(event) {{
        event.preventDefault();
        const name = document.getElementById('playbook-name-input').value.trim();
        await postJson('playbooks/import', {{
          name,
          source_kind: 'markdown',
          source_uri: document.getElementById('playbook-source-uri-input').value.trim() || buildManualUri('playbook', name),
          goal_id: document.getElementById('playbook-goal-input').value || null,
          compiled_spec: {{
            steps: splitLines(document.getElementById('playbook-steps-input').value),
            mcp_servers: splitLines(document.getElementById('playbook-mcp-input').value),
          }},
        }});
        event.target.reset();
      }}

      async function handlePlaybookIngestSubmit(event) {{
        event.preventDefault();
        const name = document.getElementById('ingest-playbook-name-input').value.trim();
        const result = await postJson('playbooks/ingest', {{
          name,
          goal_id: document.getElementById('ingest-playbook-goal-input').value || null,
          source_uri: document.getElementById('ingest-playbook-source-uri-input').value.trim() || buildManualUri('ingested-playbook', name),
          source_kind: document.getElementById('ingest-playbook-kind-input').value.trim() || 'markdown',
          source_text: document.getElementById('ingest-playbook-source-input').value.trim(),
        }});
        latestIngestionResult = result;
        renderIngestionGuidance();
        if ((result.suggested_skills || []).length) {{
          applySkillSuggestion(result.suggested_skills[0]);
        }}
        event.target.reset();
        document.getElementById('ingest-playbook-kind-input').value = 'markdown';
        if ((result.suggested_skills || []).length) {{
          const firstSkill = result.suggested_skills[0];
          setWorkbenchStatus(currentLanguage === 'zh'
            ? `已解析 SOP，并为你预填 Skill：${{firstSkill.name}}`
            : `SOP parsed and Skill form prefilled with: ${{firstSkill.name}}`, 'success');
        }}
      }}

      async function handleSkillSubmit(event) {{
        event.preventDefault();
        await postJson('skills', {{
          name: document.getElementById('skill-name-input').value.trim(),
          description: document.getElementById('skill-description-input').value.trim(),
          required_mcp_servers: splitLines(document.getElementById('skill-mcp-input').value),
          input_schema: {{}},
          output_schema: {{}},
          approval_policy: {{}},
          evaluation_policy: {{}},
        }});
        event.target.reset();
      }}

      async function handleMcpServerSubmit(event) {{
        event.preventDefault();
        const name = document.getElementById('mcp-server-name-input').value.trim();
        await postJson('mcp-servers', {{
          name,
          transport: document.getElementById('mcp-server-transport-input').value.trim() || 'streamable_http',
          endpoint: document.getElementById('mcp-server-endpoint-input').value.trim() || `https://example.com/mcp/${{name}}`,
          scopes: splitLines(document.getElementById('mcp-server-scopes-input').value),
          auth_config: {{ mode: 'manual_setup' }},
          status: 'inactive',
        }});
        event.target.reset();
        document.getElementById('mcp-server-transport-input').value = 'streamable_http';
      }}

      async function handleKnowledgeSubmit(event) {{
        event.preventDefault();
        const name = document.getElementById('knowledge-name-input').value.trim();
        await postJson('knowledge-bases', {{
          name,
          description: document.getElementById('knowledge-description-input').value.trim(),
          content: document.getElementById('knowledge-content-input').value.trim(),
          tags: splitLines(document.getElementById('knowledge-tags-input').value),
          goal_id: document.getElementById('knowledge-goal-input').value || null,
          source_uri: buildManualUri('knowledge', name),
        }});
        event.target.reset();
      }}

      async function handleTaskSubmit(event) {{
        event.preventDefault();
        await postJson('tasks', {{
          goal_id: document.getElementById('task-goal-input').value,
          playbook_id: document.getElementById('task-playbook-input').value,
          assigned_skill_id: document.getElementById('task-skill-input').value || null,
          knowledge_base_ids: splitLines(document.getElementById('task-knowledge-input').value),
          name: document.getElementById('task-name-input').value.trim(),
          description: document.getElementById('task-description-input').value.trim(),
          queue_name: document.getElementById('task-queue-input').value.trim() || 'default',
          priority: Number(document.getElementById('task-priority-input').value || 0),
          approval_required: document.getElementById('task-approval-input').checked,
          depends_on: splitLines(document.getElementById('task-depends-on-input').value),
        }});
        event.target.reset();
        document.getElementById('task-queue-input').value = 'default';
        document.getElementById('task-priority-input').value = '0';
        document.getElementById('task-knowledge-input').value = '';
      }}

      async function handleWorkbenchSubmit(handler, event) {{
        try {{
          setWorkbenchStatus(currentLanguage === 'zh' ? '提交中…' : 'Submitting…');
          await handler(event);
          await refresh();
          setWorkbenchStatus(t('workbench_status_success'), 'success');
        }} catch (error) {{
          setWorkbenchStatus(`${{t('workbench_status_error')}}: ${{error.message}}`, 'error');
        }}
      }}

      document.getElementById('lang-zh').addEventListener('click', () => applyLanguage('zh'));
      document.getElementById('lang-en').addEventListener('click', () => applyLanguage('en'));
      document.getElementById('goal-form').addEventListener('submit', (event) => handleWorkbenchSubmit(handleGoalSubmit, event));
      document.getElementById('sop-ingest-form').addEventListener('submit', (event) => handleWorkbenchSubmit(handlePlaybookIngestSubmit, event));
      document.getElementById('editor-resource-type').addEventListener('change', () => refreshEditorResourceOptions());
      document.getElementById('editor-resource-id').addEventListener('change', () => loadEditorSelection());
      document.getElementById('editor-load-button').addEventListener('click', () => loadEditorSelection());
      document.getElementById('editor-reset-button').addEventListener('click', () => loadEditorSelection());
      document.getElementById('editor-save-button').addEventListener('click', async () => {{
        try {{
          document.getElementById('editor-status').textContent = currentLanguage === 'zh' ? '保存中…' : 'Saving…';
          await saveEditorSelection();
          await refresh();
          document.getElementById('editor-status').textContent = t('workbench_status_success');
        }} catch (error) {{
          document.getElementById('editor-status').textContent = `${{t('workbench_status_error')}}: ${{error.message}}`;
        }}
      }});
      document.getElementById('playbook-form').addEventListener('submit', (event) => handleWorkbenchSubmit(handlePlaybookSubmit, event));
      document.getElementById('skill-form').addEventListener('submit', (event) => handleWorkbenchSubmit(handleSkillSubmit, event));
      document.getElementById('mcp-server-form').addEventListener('submit', (event) => handleWorkbenchSubmit(handleMcpServerSubmit, event));
      document.getElementById('knowledge-form').addEventListener('submit', (event) => handleWorkbenchSubmit(handleKnowledgeSubmit, event));
      document.getElementById('task-form').addEventListener('submit', (event) => handleWorkbenchSubmit(handleTaskSubmit, event));
      document.getElementById('ingest-playbook-file-input').addEventListener('change', async (event) => {{
        const file = event.target.files && event.target.files[0];
        if (!file) return;
        const text = await file.text();
        document.getElementById('ingest-playbook-source-input').value = text;
        document.getElementById('ingest-playbook-kind-input').value = inferSourceKindFromFile(file.name);
        if (!document.getElementById('ingest-playbook-name-input').value.trim()) {{
          document.getElementById('ingest-playbook-name-input').value = file.name.replace(/\\.[^.]+$/, '');
        }}
      }});
      document.addEventListener('click', async (event) => {{
        const editorButton = event.target.closest('[data-editor-section]');
        if (editorButton) {{
          document.getElementById('editor-resource-type').value = editorButton.dataset.editorSection;
          refreshEditorResourceOptions();
          document.getElementById('editor-resource-id').value = editorButton.dataset.editorTarget;
          loadEditorSelection();
          document.getElementById('editor-status').textContent = currentLanguage === 'zh' ? '已载入编辑器。' : 'Loaded into editor.';
          return;
        }}
        const button = event.target.closest('[data-action-kind]');
        if (!button) return;
        try {{
          const payload = button.dataset.payload ? JSON.parse(button.dataset.payload) : null;
          setActionStatus(t('action_status_running'));
          button.disabled = true;
          const result = await runAction(button.dataset.actionKind, button.dataset.actionTarget, button.dataset.actionName, payload);
          if (button.dataset.actionKind === 'playbook' && button.dataset.actionName === 'materialize-skill') {{
            markMaterializedSkill(result);
            if (result && result.skill) {{
              applySkillSuggestion(result.skill);
              setWorkbenchStatus(currentLanguage === 'zh'
                ? `已创建 Skill draft：${{result.skill.name}}`
                : `Created draft skill: ${{result.skill.name}}`, 'success');
            }}
          }}
          if (button.dataset.actionKind === 'playbook' && button.dataset.actionName === 'materialize-mcp') {{
            markMaterializedMcp(result);
            if (result && result.mcp_server) {{
              setWorkbenchStatus(currentLanguage === 'zh'
                ? `已创建 MCP draft：${{result.mcp_server.name}}`
                : `Created draft MCP: ${{result.mcp_server.name}}`, 'success');
            }}
          }}
          if (button.dataset.actionKind === 'skill' && button.dataset.actionName === 'apply-authoring-pack' && result && result.skill) {{
            setWorkbenchStatus(currentLanguage === 'zh'
              ? `已应用 Skill 配置建议：${{result.skill.name}}`
              : `Applied authoring pack for: ${{result.skill.name}}`, 'success');
          }}
          await refresh();
          setActionStatus(t('action_status_success'), 'success');
        }} catch (error) {{
          setActionStatus(`${{t('action_status_error')}}: ${{error.message}}`, 'error');
        }} finally {{
          button.disabled = false;
        }}
      }});

      window.addEventListener('error', (event) => {{
        showBootError(event.error || event.message);
      }});

      window.addEventListener('unhandledrejection', (event) => {{
        showBootError(event.reason);
      }});

      window.addEventListener('hashchange', () => {{
        applyRoute((window.location.hash || '#dashboard').replace(/^#/, '') || 'dashboard');
      }});

      document.getElementById('sidebar-nav').addEventListener('click', (event) => {{
        const button = event.target.closest('[data-route]');
        if (!button) return;
        applyRoute(button.dataset.route, true);
      }});

      document.getElementById('refresh-board').addEventListener('click', async () => {{
        const button = document.getElementById('refresh-board');
        button.textContent = currentLanguage === 'zh' ? '刷新中…' : 'Refreshing…';
        button.disabled = true;
        try {{
          await refresh();
        }} catch (error) {{
          document.getElementById('resource-rows').innerHTML = `<div class="row"><div><strong>${{escapeHtml(t('loading_failed_title'))}}</strong><small>${{escapeHtml(error.message)}}</small></div><span class="state">${{escapeHtml(t('error'))}}</span></div>`;
        }} finally {{
          button.disabled = false;
          button.textContent = t('refresh_board');
        }}
      }});

      applyLanguage(currentLanguage);
      applyRoute(currentRoute);
      document.getElementById('resource-rows').innerHTML = `<div class="row"><div><strong>${{escapeHtml(t('loading_resources_title'))}}</strong><small>${{escapeHtml(t('loading_resources_body'))}}</small></div><span class="state">${{escapeHtml(t('booting'))}}</span></div>`;
      refresh().catch((error) => {{
        showBootError(error);
        document.getElementById('resource-rows').innerHTML = `<div class="row"><div><strong>${{escapeHtml(t('api_unavailable_title'))}}</strong><small>${{escapeHtml(error.message)}}</small></div><span class="state">${{escapeHtml(t('offline'))}}</span></div>`;
      }});
    </script>
  </body>
</html>
"""
