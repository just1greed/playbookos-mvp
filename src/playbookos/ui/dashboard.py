from __future__ import annotations

import html
import json
from typing import Any


SECTION_ORDER = ["goals", "tasks", "runs", "artifacts", "reflections"]
SECTION_LABELS = {
    "goals": "Goals",
    "tasks": "Tasks",
    "runs": "Runs",
    "artifacts": "Artifacts",
    "reflections": "Reflections",
}


def build_dashboard_html(board_snapshot: dict[str, dict[str, int]] | None = None, *, api_base: str = "/api") -> str:
    snapshot = board_snapshot or {section: {} for section in SECTION_ORDER}
    cards_markup = "".join(_build_summary_card(section, snapshot.get(section, {})) for section in SECTION_ORDER)
    endpoint_cards = "".join(_build_endpoint_card(api_base, section) for section in SECTION_ORDER)
    snapshot_json = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
    api_base_json = json.dumps(api_base)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PlaybookOS Console</title>
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
        --success: #22c55e;
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
      .shell {{
        width: min(1180px, calc(100vw - 32px));
        margin: 24px auto 48px;
      }}
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
        display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px;
        border-radius: 999px; background: rgba(124, 58, 237, 0.16); color: #ddd6fe; font-size: 13px;
        border: 1px solid rgba(196, 181, 253, 0.15);
      }}
      h1 {{ margin: 14px 0 10px; font-size: clamp(32px, 5vw, 54px); line-height: 1.04; }}
      .hero p {{ margin: 0; max-width: 760px; color: var(--muted); font-size: 16px; line-height: 1.7; }}
      .hero-actions {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 24px; }}
      .button {{
        border: 0; border-radius: 14px; padding: 12px 16px; font-weight: 600; cursor: pointer; text-decoration: none;
        color: var(--text); background: linear-gradient(135deg, var(--accent), #4f46e5); box-shadow: 0 12px 32px rgba(79, 70, 229, 0.35);
      }}
      .button.secondary {{ background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border); box-shadow: none; }}
      .hero-meta {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 28px; }}
      .meta-card {{ padding: 18px; border-radius: 20px; background: rgba(15, 23, 42, 0.65); border: 1px solid var(--border); }}
      .meta-card strong {{ display: block; font-size: 24px; margin-top: 8px; }}
      .section {{ margin-top: 24px; }}
      .section-title {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 14px; }}
      .section-title h2 {{ margin: 0; font-size: 20px; }}
      .section-title span {{ color: var(--muted); font-size: 14px; }}
      .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }}
      .card {{
        grid-column: span 12; padding: 22px; border-radius: 24px; border: 1px solid var(--border);
        background: var(--panel); box-shadow: var(--shadow); backdrop-filter: blur(14px);
      }}
      .summary-card {{ grid-column: span 12; position: relative; overflow: hidden; }}
      .summary-card::after {{
        content: ""; position: absolute; inset: auto -30px -40px auto; width: 140px; height: 140px;
        border-radius: 999px; background: radial-gradient(circle, rgba(6, 182, 212, 0.22), transparent 70%);
      }}
      .summary-card h3, .endpoint-card h3 {{ margin: 0 0 8px; font-size: 18px; }}
      .eyebrow {{ color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; }}
      .metric {{ display: flex; align-items: baseline; gap: 10px; margin-top: 10px; }}
      .metric strong {{ font-size: 38px; line-height: 1; }}
      .metric span {{ color: var(--muted); }}
      .pills {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }}
      .pill {{
        border-radius: 999px; padding: 8px 10px; background: var(--panel-soft); color: #dbeafe;
        border: 1px solid rgba(125, 211, 252, 0.12); font-size: 13px;
      }}
      .chart {{ height: 10px; margin-top: 18px; border-radius: 999px; background: rgba(30, 41, 59, 0.88); overflow: hidden; }}
      .chart > span {{ display: block; height: 100%; width: 0%; background: linear-gradient(90deg, var(--accent), var(--accent-2)); transition: width 0.35s ease; }}
      .endpoint-card {{ grid-column: span 4; background: var(--panel-strong); }}
      .endpoint-link {{ display: inline-flex; margin-top: 14px; color: #c4b5fd; text-decoration: none; }}
      .endpoint-link:hover {{ color: #ddd6fe; }}
      .list-card {{ grid-column: span 8; }}
      .activity-card {{ grid-column: span 4; }}
      .rows {{ display: grid; gap: 10px; margin-top: 14px; }}
      .row {{
        display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 14px 16px;
        border-radius: 16px; background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(148, 163, 184, 0.08);
      }}
      .row strong {{ font-size: 14px; }}
      .row small {{ color: var(--muted); display: block; margin-top: 4px; }}
      .state {{ color: #bfdbfe; background: rgba(59, 130, 246, 0.14); padding: 6px 9px; border-radius: 999px; font-size: 12px; }}
      .timeline {{ display: grid; gap: 14px; margin-top: 10px; }}
      .timeline-item {{ position: relative; padding-left: 18px; color: var(--muted); line-height: 1.6; }}
      .timeline-item::before {{
        content: ""; position: absolute; left: 0; top: 10px; width: 8px; height: 8px; border-radius: 999px;
        background: linear-gradient(135deg, var(--accent), var(--accent-2)); box-shadow: 0 0 18px rgba(99, 102, 241, 0.55);
      }}
      pre {{
        margin: 0; padding: 18px; border-radius: 18px; overflow: auto; font-size: 13px;
        color: #cbd5e1; background: rgba(2, 6, 23, 0.74); border: 1px solid rgba(148, 163, 184, 0.08);
      }}
      .footer {{ margin-top: 20px; color: var(--muted); font-size: 13px; text-align: center; }}
      @media (max-width: 980px) {{
        .hero-meta {{ grid-template-columns: 1fr; }}
        .endpoint-card, .list-card, .activity-card {{ grid-column: span 12; }}
      }}
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <div class="hero-top">
          <div>
            <span class="badge">✦ PlaybookOS · AI Work Operating System</span>
            <h1>用一个可视化控制台，追踪 Goal → Task → Run → Reflection 的闭环。</h1>
            <p>这个页面直接消费 PlaybookOS 控制面 API，展示看板快照、关键资源入口、最近状态分布，以及执行与学习主链路的运行节奏。</p>
            <div class="hero-actions">
              <button class="button" id="refresh-board" type="button">刷新看板</button>
              <a class="button secondary" href="{html.escape(api_base)}/board" target="_blank" rel="noreferrer">查看原始 Board JSON</a>
            </div>
          </div>
          <div class="meta-card" style="min-width: 240px;">
            <div class="eyebrow">Live Data Source</div>
            <strong id="api-base-label">{html.escape(api_base)}</strong>
            <span id="last-updated" style="display:block;margin-top:10px;color:var(--muted);">Waiting for refresh…</span>
          </div>
        </div>
        <div class="hero-meta">
          <div class="meta-card"><div class="eyebrow">Total Resources</div><strong id="resource-total">0</strong><span>Goals, tasks, runs, artifacts, reflections</span></div>
          <div class="meta-card"><div class="eyebrow">Blocked Signals</div><strong id="blocked-total">0</strong><span>Blocked goals + waiting human runs</span></div>
          <div class="meta-card"><div class="eyebrow">Learning Signals</div><strong id="learning-total">0</strong><span>Reflections and published improvement paths</span></div>
        </div>
      </section>

      <section class="section">
        <div class="section-title"><h2>Control Board</h2><span>Live status distribution from /api/board</span></div>
        <div class="grid" id="summary-grid">{cards_markup}</div>
      </section>

      <section class="section">
        <div class="section-title"><h2>API Entry Points</h2><span>Core resources for manual inspection and automation</span></div>
        <div class="grid">{endpoint_cards}</div>
      </section>

      <section class="section">
        <div class="grid">
          <article class="card list-card">
            <div class="section-title"><h2>Quick Resource Peek</h2><span>Recent entities fetched from the API</span></div>
            <div class="rows" id="resource-rows">
              <div class="row"><div><strong>等待加载资源</strong><small>页面会自动抓取 goals / tasks / runs / reflections / artifacts。</small></div><span class="state">booting</span></div>
            </div>
          </article>
          <article class="card activity-card">
            <div class="section-title"><h2>Operating Rhythm</h2><span>Recommended loop for the MVP</span></div>
            <div class="timeline">
              <div class="timeline-item">Import / compile a playbook, then turn it into a task DAG.</div>
              <div class="timeline-item">Dispatch ready tasks into runs and capture trace + artifact metadata.</div>
              <div class="timeline-item">Reflect on outcomes, evaluate proposals, approve carefully, then publish safely.</div>
            </div>
          </article>
        </div>
      </section>

      <section class="section">
        <div class="section-title"><h2>Snapshot JSON</h2><span>Useful when debugging UI/data mismatches</span></div>
        <article class="card"><pre id="snapshot-json"></pre></article>
      </section>

      <div class="footer">Built for PlaybookOS MVP · single-file dashboard · no external frontend dependencies</div>
    </main>

    <script>
      const apiBase = {api_base_json};
      const sectionOrder = {json.dumps(SECTION_ORDER)};
      const sectionLabels = {json.dumps(SECTION_LABELS, ensure_ascii=False)};
      let currentSnapshot = {snapshot_json};

      function sumValues(record) {{
        return Object.values(record || {{}}).reduce((total, value) => total + Number(value || 0), 0);
      }}

      function formatStateLabel(value) {{
        return String(value).replaceAll('_', ' ');
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
        document.getElementById('last-updated').textContent = `Last updated: ${{new Date().toLocaleString()}}`;
      }}

      function createSummaryCard(section, stats) {{
        const total = sumValues(stats);
        const topEntries = Object.entries(stats).sort((left, right) => Number(right[1]) - Number(left[1]));
        const dominant = topEntries[0] || ['empty', 0];
        const dominantShare = total > 0 ? Math.max(8, Math.round((Number(dominant[1]) / total) * 100)) : 8;
        const pills = (topEntries.length ? topEntries : [['empty', 0]])
          .slice(0, 4)
          .map(([name, value]) => `<span class="pill">${{formatStateLabel(name)}} · ${{value}}</span>`)
          .join('');

        return `
          <article class="card summary-card">
            <div class="eyebrow">${{sectionLabels[section]}}</div>
            <h3>${{sectionLabels[section]}} overview</h3>
            <div class="metric"><strong>${{total}}</strong><span>tracked items</span></div>
            <div class="pills">${{pills}}</div>
            <div class="chart"><span style="width:${{dominantShare}}%"></span></div>
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
        const sections = [
          ['goals', 'Goal'],
          ['tasks', 'Task'],
          ['runs', 'Run'],
          ['artifacts', 'Artifact'],
          ['reflections', 'Reflection'],
        ];

        for (const [resourceName, label] of sections) {{
          const items = Array.isArray(payloads[resourceName]) ? payloads[resourceName].slice(0, 2) : [];
          if (!items.length) {{
            rows.push(`<div class="row"><div><strong>No ${{label}}s yet</strong><small>${{resourceName}} endpoint returned an empty list.</small></div><span class="state">idle</span></div>`);
            continue;
          }}
          for (const item of items) {{
            const title = item.title || item.name || item.summary || item.id;
            const state = item.status || item.eval_status || item.kind || 'ready';
            rows.push(`<div class="row"><div><strong>${{escapeHtml(title)}}</strong><small>${{label}} · ${{escapeHtml(item.id || 'n/a')}}</small></div><span class="state">${{escapeHtml(formatStateLabel(state))}}</span></div>`);
          }}
        }}

        document.getElementById('resource-rows').innerHTML = rows.join('');
      }}

      function escapeHtml(value) {{
        return String(value)
          .replaceAll('&', '&amp;')
          .replaceAll('<', '&lt;')
          .replaceAll('>', '&gt;')
          .replaceAll('"', '&quot;')
          .replaceAll("'", '&#39;');
      }}

      async function refresh() {{
        const [board, goals, tasks, runs, artifacts, reflections] = await Promise.all([
          fetchJson('board'),
          fetchJson('goals'),
          fetchJson('tasks'),
          fetchJson('runs'),
          fetchJson('artifacts'),
          fetchJson('reflections'),
        ]);

        renderSummary(board);
        renderResourceRows({{ goals, tasks, runs, artifacts, reflections }});
      }}

      document.getElementById('refresh-board').addEventListener('click', async () => {{
        const button = document.getElementById('refresh-board');
        button.textContent = '刷新中…';
        button.disabled = true;
        try {{
          await refresh();
        }} catch (error) {{
          document.getElementById('resource-rows').innerHTML = `<div class="row"><div><strong>加载失败</strong><small>${{escapeHtml(error.message)}}</small></div><span class="state">error</span></div>`;
        }} finally {{
          button.disabled = false;
          button.textContent = '刷新看板';
        }}
      }});

      renderSummary(currentSnapshot);
      refresh().catch((error) => {{
        document.getElementById('resource-rows').innerHTML = `<div class="row"><div><strong>API 暂不可达</strong><small>${{escapeHtml(error.message)}}</small></div><span class="state">offline</span></div>`;
      }});
    </script>
  </body>
</html>
"""


def _build_summary_card(section: str, stats: dict[str, int]) -> str:
    total = sum(stats.values())
    pills = "".join(
        f'<span class="pill">{html.escape(name.replace("_", " "))} · {value}</span>' for name, value in list(stats.items())[:4]
    ) or '<span class="pill">empty · 0</span>'
    return (
        f'<article class="card summary-card">'
        f'<div class="eyebrow">{html.escape(SECTION_LABELS[section])}</div>'
        f'<h3>{html.escape(SECTION_LABELS[section])} overview</h3>'
        f'<div class="metric"><strong>{total}</strong><span>tracked items</span></div>'
        f'<div class="pills">{pills}</div>'
        f'<div class="chart"><span style="width:8%"></span></div>'
        f'</article>'
    )


def _build_endpoint_card(api_base: str, section: str) -> str:
    endpoint = f"{api_base}/{section}"
    title = SECTION_LABELS[section]
    return (
        f'<article class="card endpoint-card">'
        f'<div class="eyebrow">API</div>'
        f'<h3>{html.escape(title)}</h3>'
        f'<p style="color:var(--muted);margin:0;line-height:1.7;">'
        f'Inspect {html.escape(title.lower())} directly or wire this endpoint into your own tools and operator flows.</p>'
        f'<a class="endpoint-link" href="{html.escape(endpoint)}" target="_blank" rel="noreferrer">{html.escape(endpoint)} →</a>'
        f'</article>'
    )
