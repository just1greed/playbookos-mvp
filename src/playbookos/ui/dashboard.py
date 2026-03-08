from __future__ import annotations

import html
import json


SECTION_ORDER = ["goals", "skills", "tasks", "sessions", "runs", "acceptances", "artifacts", "reflections", "events"]

TRANSLATIONS = {
    "zh": {
        "html_lang": "zh-CN",
        "page_title": "PlaybookOS 控制台",
        "badge": "✦ PlaybookOS · AI 工作操作系统",
        "hero_title": "用一个可视化控制台，追踪 SOP / Skill / Task / Session / Acceptance / Reflection 的闭环。",
        "hero_body": "这个页面直接消费 PlaybookOS 控制面 API，展示 SOP、技能、任务、子会话、验收、反思与事件流，让用户看见 AI 工作系统的完整主链路。",
        "refresh_board": "刷新看板",
        "view_board_json": "查看原始 Board JSON",
        "live_data_source": "实时数据源",
        "waiting_refresh": "等待刷新…",
        "total_resources": "总资源数",
        "total_resources_desc": "Goals、Skills、Tasks、Sessions、Runs、Acceptances、Artifacts、Reflections、Events 总量",
        "blocked_signals": "阻塞信号",
        "blocked_signals_desc": "Blocked goals + waiting human runs",
        "learning_signals": "学习信号",
        "learning_signals_desc": "Acceptances、Reflections 与已发布优化路径",
        "control_board": "控制看板",
        "control_board_subtitle": "来自 /api/board 的实时状态分布",
        "api_entry_points": "API 入口",
        "api_entry_subtitle": "适合手动巡检，也适合自动化编排接入",
        "quick_resource_peek": "资源速览",
        "quick_resource_peek_subtitle": "从 API 抓取最近的实体样本",
        "loading_resources_title": "等待加载资源",
        "loading_resources_body": "页面会自动抓取 goals / skills / tasks / sessions / runs / acceptances / reflections / artifacts / events。",
        "operating_rhythm": "运行节奏",
        "operating_rhythm_subtitle": "当前 MVP 推荐的执行循环",
        "timeline_1": "用户先配置 SOP / Skill / Task，系统再把 SOP 规划成可执行任务图。",
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
        "route_not_found": "未找到路由",
        "loading_failed_title": "加载失败",
        "api_unavailable_title": "API 暂不可达",
        "resource_empty_suffix": "暂无记录",
        "resource_empty_body": "接口当前返回空列表。",
        "resource_id_fallback": "无 ID",
        "section_labels": {
            "goals": "目标",
            "skills": "技能",
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
        "hero_title": "Track the full SOP / Skill / Task / Session / Acceptance / Reflection loop in one visual console.",
        "hero_body": "This page reads directly from the PlaybookOS control-plane API and exposes SOPs, skills, tasks, child sessions, acceptances, reflections, and event streams so the full AI work system stays visible to the user.",
        "refresh_board": "Refresh Board",
        "view_board_json": "Open Raw Board JSON",
        "live_data_source": "Live Data Source",
        "waiting_refresh": "Waiting for refresh…",
        "total_resources": "Total Resources",
        "total_resources_desc": "Total goals, skills, tasks, sessions, runs, acceptances, artifacts, reflections, and events",
        "blocked_signals": "Blocked Signals",
        "blocked_signals_desc": "Blocked goals + waiting human runs",
        "learning_signals": "Learning Signals",
        "learning_signals_desc": "Acceptances, reflections, and published improvement paths",
        "control_board": "Control Board",
        "control_board_subtitle": "Live status distribution from /api/board",
        "api_entry_points": "API Entry Points",
        "api_entry_subtitle": "Useful for manual inspection and automation workflows",
        "quick_resource_peek": "Quick Resource Peek",
        "quick_resource_peek_subtitle": "Recent entity samples fetched from the API",
        "loading_resources_title": "Waiting for resources",
        "loading_resources_body": "The page will automatically fetch goals / skills / tasks / sessions / runs / acceptances / reflections / artifacts / events.",
        "operating_rhythm": "Operating Rhythm",
        "operating_rhythm_subtitle": "Recommended workflow loop for the current MVP",
        "timeline_1": "Users configure SOPs, skills, and tasks first; the system turns SOPs into executable task graphs.",
        "timeline_2": "A supervisor session spawns worker sessions, executes runs, and records artifacts plus event traces.",
        "timeline_3": "Results go through human acceptance and AI postmortems before SOP, skill, and knowledge updates are published.",
        "snapshot_json": "Snapshot JSON",
        "snapshot_json_subtitle": "Useful for debugging mismatches between UI and data",
        "footer": "PlaybookOS MVP · single-file dashboard · no external frontend dependencies",
        "tracked_items": "tracked items",
        "overview_suffix": "overview",
        "last_updated": "Last updated",
        "api_prefix": "API",
        "api_card_body": "Open this resource directly, or plug it into your automation tools and operating flows.",
        "idle": "idle",
        "booting": "booting",
        "error": "error",
        "offline": "offline",
        "route_not_found": "Route not found",
        "loading_failed_title": "Loading failed",
        "api_unavailable_title": "API unavailable",
        "resource_empty_suffix": "not found yet",
        "resource_empty_body": "This endpoint currently returns an empty list.",
        "resource_id_fallback": "No ID",
        "section_labels": {
            "goals": "Goals",
            "skills": "Skills",
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
    "skills": "Skill",
    "tasks": "Task",
    "sessions": "Session",
    "runs": "Run",
    "acceptances": "Acceptance",
    "artifacts": "Artifact",
    "reflections": "Reflection",
    "events": "Event",
}


def build_dashboard_html(board_snapshot: dict[str, dict[str, int]] | None = None, *, api_base: str = "/api") -> str:
    snapshot = board_snapshot or {section: {} for section in SECTION_ORDER}
    snapshot_json = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
    api_base_json = json.dumps(api_base)
    translations_json = json.dumps(TRANSLATIONS, ensure_ascii=False)
    section_order_json = json.dumps(SECTION_ORDER)
    resource_singular_json = json.dumps(RESOURCE_SINGULAR, ensure_ascii=False)
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
        padding: 32px; border: 1px solid var(--border); border-radius: 28px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(17, 24, 39, 0.78));
        box-shadow: var(--shadow); backdrop-filter: blur(18px);
      }}
      .hero-top {{ display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; flex-wrap: wrap; }}
      .badge {{
        display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 999px;
        background: rgba(124, 58, 237, 0.16); color: #ddd6fe; font-size: 13px; border: 1px solid rgba(196, 181, 253, 0.15);
      }}
      .hero-controls {{ display: flex; gap: 12px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }}
      .lang-toggle {{ display: inline-flex; gap: 6px; padding: 6px; background: rgba(15, 23, 42, 0.65); border: 1px solid var(--border); border-radius: 999px; }}
      .lang-toggle button {{
        border: 0; background: transparent; color: var(--muted); border-radius: 999px; padding: 8px 12px; cursor: pointer; font-weight: 700;
      }}
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
      .summary-card h3, .endpoint-card h3 {{ margin: 0 0 8px; font-size: 18px; }}
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
      @media (max-width: 980px) {{ .hero-meta {{ grid-template-columns: 1fr; }} .endpoint-card, .list-card, .activity-card {{ grid-column: span 12; }} }}
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
              <strong id="api-base-label">{html.escape(api_base)}</strong>
              <span id="last-updated" style="display:block;margin-top:10px;color:var(--muted);"></span>
            </div>
          </div>
        </div>
        <div class="hero-meta">
          <div class="meta-card"><div class="eyebrow" id="total-resources-label"></div><strong id="resource-total">0</strong><span id="total-resources-desc"></span></div>
          <div class="meta-card"><div class="eyebrow" id="blocked-signals-label"></div><strong id="blocked-total">0</strong><span id="blocked-signals-desc"></span></div>
          <div class="meta-card"><div class="eyebrow" id="learning-signals-label"></div><strong id="learning-total">0</strong><span id="learning-signals-desc"></span></div>
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
      const translations = {translations_json};
      let currentSnapshot = {snapshot_json};
      let currentLanguage = localStorage.getItem('playbookos-language') || 'zh';

      function t(key) {{
        return translations[currentLanguage][key];
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

      function applyLanguage(language) {{
        currentLanguage = translations[language] ? language : 'zh';
        localStorage.setItem('playbookos-language', currentLanguage);
        document.documentElement.lang = t('html_lang');
        document.title = t('page_title');
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
        renderSummary(currentSnapshot);
        renderEndpointCards();
      }}

      function renderSummary(snapshot) {{
        currentSnapshot = snapshot || {{}};
        const summaryGrid = document.getElementById('summary-grid');
        summaryGrid.innerHTML = sectionOrder.map((section) => createSummaryCard(section, snapshot[section] || {{}})).join('');
        const resourceTotal = sectionOrder.reduce((total, section) => total + sumValues(snapshot[section] || {{}}), 0);
        const blockedTotal = Number((snapshot.goals || {{}}).blocked || 0) + Number((snapshot.runs || {{}}).waiting_human || 0);
        const learningTotal = Number(sumValues(snapshot.reflections || {{}})) + Number((snapshot.goals || {{}}).review || 0);
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
        const endpoint = `${{apiBase}}/${{section}}`;
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

      function renderResourceRows(payloads) {{
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

      async function refresh() {{
        const [board, goals, skills, tasks, sessions, runs, acceptances, artifacts, reflections, events] = await Promise.all([
          fetchJson('board'),
          fetchJson('goals'),
          fetchJson('skills'),
          fetchJson('tasks'),
          fetchJson('sessions'),
          fetchJson('runs'),
          fetchJson('acceptances'),
          fetchJson('artifacts'),
          fetchJson('reflections'),
          fetchJson('events'),
        ]);
        renderSummary(board);
        renderResourceRows({{ goals, skills, tasks, sessions, runs, acceptances, artifacts, reflections, events }});
      }}

      document.getElementById('lang-zh').addEventListener('click', () => applyLanguage('zh'));
      document.getElementById('lang-en').addEventListener('click', () => applyLanguage('en'));

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
        document.getElementById('resource-rows').innerHTML = `<div class="row"><div><strong>${{escapeHtml(t('api_unavailable_title'))}}</strong><small>${{escapeHtml(error.message)}}</small></div><span class="state">${{escapeHtml(t('offline'))}}</span></div>`;
      }});
    </script>
  </body>
</html>
"""
