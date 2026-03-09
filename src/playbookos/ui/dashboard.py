from __future__ import annotations

import html
import json


SECTION_ORDER = [
    "goals",
    "playbooks",
    "skills",
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
        "total_resources_desc": "Goals、Playbooks、Skills、Knowledge、Knowledge Updates、Tasks、Sessions、Runs、Acceptances、Artifacts、Reflections、Events 总量",
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
        "quick_resource_peek": "资源速览",
        "quick_resource_peek_subtitle": "从 API 抓取最近的实体样本",
        "loading_resources_title": "等待加载资源",
        "loading_resources_body": "页面会自动抓取 goals / playbooks / skills / knowledge_bases / knowledge_updates / tasks / sessions / runs / acceptances / reflections / artifacts / events。",
        "operating_rhythm": "运行节奏",
        "operating_rhythm_subtitle": "当前 MVP 推荐的执行循环",
        "timeline_1": "用户先配置 Goal / SOP / Skill / Knowledge / Task，系统再把 SOP 规划成可执行任务图。",
        "timeline_2": "主控会话调度子会话执行任务，沉淀 run、artifact 与 event 事件轨迹。",
        "timeline_3": "结果经过人工验收与 AI 复盘，再回写 SOP、技能与知识沉淀。",
        "snapshot_json": "快照 JSON",
        "snapshot_json_subtitle": "适合排查 UI 与数据不一致问题",
        "footer": "PlaybookOS MVP · 单文件控制台 · 无外部前端依赖",
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
        "create_playbook": "新建 SOP",
        "create_skill": "新建 Skill",
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
        "skill_name": "Skill 名称",
        "skill_description": "Skill 说明",
        "skill_required_mcp_servers": "依赖 MCP（每行一条）",
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
        "quick_resource_peek": "Quick Resource Peek",
        "quick_resource_peek_subtitle": "Recent entity samples fetched from the API",
        "loading_resources_title": "Waiting for resources",
        "loading_resources_body": "The page will automatically fetch goals / playbooks / skills / knowledge_bases / knowledge_updates / tasks / sessions / runs / acceptances / reflections / artifacts / events.",
        "operating_rhythm": "Operating Rhythm",
        "operating_rhythm_subtitle": "Recommended workflow loop for the current MVP",
        "timeline_1": "Users configure goals, SOPs, skills, knowledge, and tasks first; the system turns SOPs into executable task graphs.",
        "timeline_2": "A supervisor session spawns worker sessions, executes runs, and records artifacts plus event traces.",
        "timeline_3": "Results go through human acceptance and AI postmortems before SOP, skill, and knowledge updates are published.",
        "snapshot_json": "Snapshot JSON",
        "snapshot_json_subtitle": "Useful for debugging mismatches between UI and data",
        "footer": "PlaybookOS MVP · single-file dashboard · no external frontend dependencies",
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
        "create_playbook": "Create SOP",
        "create_skill": "Create Skill",
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
        "skill_name": "Skill name",
        "skill_description": "Skill description",
        "skill_required_mcp_servers": "Required MCP servers (one per line)",
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
        .hero-meta {{ grid-template-columns: 1fr; }}
        .endpoint-card, .list-card, .activity-card, .form-card, .action-card {{ grid-column: span 12; }}
      }}
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
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

      <section class="section">
        <div class="section-title"><h2 id="control-board-title"></h2><span id="control-board-subtitle"></span></div>
        <div class="grid" id="summary-grid"></div>
      </section>

      <section class="section">
        <div class="section-title"><h2 id="api-entry-title"></h2><span id="api-entry-subtitle"></span></div>
        <div class="grid" id="endpoint-grid"></div>
      </section>

      <section class="section">
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
          </div>
        </article>
      </section>

      <section class="section">
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

      <section class="section">
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

      <section class="section">
        <article class="card workbench-card">
          <div class="section-title"><h2 data-i18n="session_tree_title"></h2><span data-i18n="session_tree_subtitle"></span></div>
          <div class="session-groups" id="session-groups"></div>
        </article>
      </section>

      <section class="section">
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

      <section class="section">
        <div class="section-title"><h2 id="snapshot-json-title"></h2><span id="snapshot-json-subtitle"></span></div>
        <article class="card"><pre id="snapshot-json"></pre></article>
      </section>

      <div class="footer" id="footer-text"></div>
    </main>

    <script>
      const apiBase = {api_base_json};
      const sectionOrder = {section_order_json};
      const resourceSingular = {resource_singular_json};
      const resourcePaths = {resource_paths_json};
      const translations = {translations_json};
      let currentSnapshot = {snapshot_json};
      let latestResources = {{}};
      const editableSections = ['goals', 'playbooks', 'skills', 'knowledge_bases', 'tasks'];
      let currentLanguage = localStorage.getItem('playbookos-language') || 'zh';

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

      function setActionStatus(message, state = 'idle') {{
        const node = document.getElementById('action-status');
        if (!node) return;
        node.dataset.state = state;
        node.textContent = message;
        node.style.color = state === 'error' ? '#fca5a5' : state === 'success' ? '#86efac' : 'var(--muted)';
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
        document.getElementById('footer-text').textContent = t('footer');
        document.getElementById('lang-zh').classList.toggle('active', currentLanguage === 'zh');
        document.getElementById('lang-en').classList.toggle('active', currentLanguage === 'en');
        document.querySelectorAll('[data-i18n]').forEach((node) => {{ node.textContent = t(node.dataset.i18n); }});
        document.querySelectorAll('[data-i18n-placeholder]').forEach((node) => {{ node.placeholder = t(node.dataset.i18nPlaceholder); }});
        if (!document.getElementById('workbench-status').dataset.state) {{
          setWorkbenchStatus(t('workbench_status_ready'));
        }}
        if (!document.getElementById('action-status').dataset.state) {{
          setActionStatus(t('action_status_ready'));
        }}
        renderSummary(currentSnapshot);
        renderEndpointCards();
        renderWorkbenchOptions();
        renderActionCenter();
        renderSessionTree();
        if (!document.getElementById('editor-status').dataset.state) {{
          document.getElementById('editor-status').dataset.state = 'idle';
          document.getElementById('editor-status').textContent = t('editor_status_ready');
        }}
        refreshEditorResourceOptions();
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

      function renderActionCenter() {{
        renderGoalActions();
        renderReviewActions();
        renderLearningActions();
      }}

      function sessionTitleLine(session) {{
        return `${{session.title || session.id}}`;
      }}

      function sessionDetailLines(session) {{
        const lines = [
          `${{t('session_kind_label')}}: ${{session.kind || ''}}`,
          `${{t('session_status_label')}}: ${{session.status || ''}}`,
        ];
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
        if (actionKind === 'goal') {{
          await postJson(`goals/${{actionTarget}}/${{actionName}}`, body);
          return;
        }}
        if (actionKind === 'run') {{
          await postJson(`runs/${{actionTarget}}/${{actionName}}`, body);
          return;
        }}
        if (actionKind === 'reflection') {{
          await postJson(`reflections/${{actionTarget}}/${{actionName}}`, body);
          return;
        }}
        if (actionKind === 'knowledge') {{
          await postJson(`knowledge-updates/${{actionTarget}}/${{actionName}}`, body);
          return;
        }}
        if (actionKind === 'task' && actionName === 'accept') {{
          const accepted = Boolean(payload && payload.accepted);
          const task = (latestResources.tasks || []).find((item) => item.id === actionTarget);
          await postJson(`tasks/${{actionTarget}}/accept`, {{
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

      function renderResourceRows(payloads) {{
        latestResources = payloads;
        const rows = [];
        for (const resourceName of sectionOrder) {{
          const label = sectionLabel(resourceName);
          const singular = resourceSingular[resourceName] || label;
          const items = Array.isArray(payloads[resourceName]) ? payloads[resourceName].slice(0, 2) : [];
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
        const board = await fetchJson('board');
        const resourcePairs = await Promise.all(sectionOrder.map(async (section) => [section, await fetchJson(resourcePath(section))]));
        const payloads = Object.fromEntries(resourcePairs);
        renderSummary(board);
        renderResourceRows(payloads);
        renderWorkbenchOptions();
        refreshEditorResourceOptions();
        renderActionCenter();
        renderSessionTree();
        clearBootError();
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
      document.getElementById('knowledge-form').addEventListener('submit', (event) => handleWorkbenchSubmit(handleKnowledgeSubmit, event));
      document.getElementById('task-form').addEventListener('submit', (event) => handleWorkbenchSubmit(handleTaskSubmit, event));
      document.addEventListener('click', async (event) => {{
        const button = event.target.closest('[data-action-kind]');
        if (!button) return;
        try {{
          const payload = button.dataset.payload ? JSON.parse(button.dataset.payload) : null;
          setActionStatus(t('action_status_running'));
          button.disabled = true;
          await runAction(button.dataset.actionKind, button.dataset.actionTarget, button.dataset.actionName, payload);
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
      document.getElementById('resource-rows').innerHTML = `<div class="row"><div><strong>${{escapeHtml(t('loading_resources_title'))}}</strong><small>${{escapeHtml(t('loading_resources_body'))}}</small></div><span class="state">${{escapeHtml(t('booting'))}}</span></div>`;
      refresh().catch((error) => {{
        showBootError(error);
        document.getElementById('resource-rows').innerHTML = `<div class="row"><div><strong>${{escapeHtml(t('api_unavailable_title'))}}</strong><small>${{escapeHtml(error.message)}}</small></div><span class="state">${{escapeHtml(t('offline'))}}</span></div>`;
      }});
    </script>
  </body>
</html>
"""
