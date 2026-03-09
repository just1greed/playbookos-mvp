#!/usr/bin/env bash
set -euo pipefail

API_BASE="${PLAYBOOKOS_API_BASE:-http://127.0.0.1:8000}"
AGENT_ID="${PLAYBOOKOS_AGENT_ID:-openclaw-main}"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

log() {
  printf '\n[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "missing required command: $1" >&2
    exit 1
  }
}

require_cmd curl
require_cmd python3

SOP_FILE="$WORK_DIR/weekly-report.md"
cat > "$SOP_FILE" <<'DOC'
# Weekly Report SOP

1. Research competitor updates in Notion
2. Draft the weekly summary
3. Publish the summary to Slack
DOC

render_json() {
  local path="$1"
  python3 - "$path" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
print(json.dumps(json.loads(path.read_text()), indent=2, ensure_ascii=False))
PY
}

post_json() {
  local method="$1"
  local url="$2"
  local payload_file="$3"
  local output_file="$4"
  curl -fsS -X "$method" "$url" -H 'Content-Type: application/json' --data @"$payload_file" > "$output_file"
}

log "1/5 Discover manifest"
curl -fsS "$API_BASE/api/agent/manifest" > "$WORK_DIR/manifest.json"
render_json "$WORK_DIR/manifest.json"

log "2/5 Sync context"
curl -fsS "$API_BASE/api/agent/context" > "$WORK_DIR/context.json"
render_json "$WORK_DIR/context.json"

log "3/5 Create intake plan"
python3 - "$WORK_DIR/intake_payload.json" "$SOP_FILE" <<'PY'
import json, sys
from pathlib import Path
payload_path = Path(sys.argv[1])
sop_path = Path(sys.argv[2])
payload = {
    "message": "Import this SOP and prepare the required skill and MCP setup",
    "resource_name": "Weekly Report SOP",
    "markdown_sop": sop_path.read_text(),
}
payload_path.write_text(json.dumps(payload, ensure_ascii=False))
PY
post_json POST "$API_BASE/api/agent/intake" "$WORK_DIR/intake_payload.json" "$WORK_DIR/intake.json"
render_json "$WORK_DIR/intake.json"

log "4/5 Create delegation profile"
cat > "$WORK_DIR/delegation_payload.json" <<JSON
{
  "name": "Managed OpenClaw Operator",
  "description": "Allow SOP ingestion and draft capability creation",
  "operator_agent_id": "$AGENT_ID",
  "agent_type": "openclaw",
  "allowed_endpoints": [
    "/api/playbooks/ingest",
    "/api/playbooks/{playbook_id}/skill-drafts",
    "/api/playbooks/{playbook_id}/mcp-drafts"
  ],
  "approval_required_endpoints": [],
  "scope_goal_ids": [],
  "max_operations_per_apply": 6,
  "status": "active",
  "metadata": {"mode": "managed"}
}
JSON
post_json POST "$API_BASE/api/delegation-profiles" "$WORK_DIR/delegation_payload.json" "$WORK_DIR/delegation.json"
render_json "$WORK_DIR/delegation.json"

DELEGATION_ID="$(python3 - "$WORK_DIR/delegation.json" <<'PY'
import json, sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text())["id"])
PY
)"

log "5/5 Apply recommended operations"
python3 - "$WORK_DIR/apply_payload.json" "$WORK_DIR/intake.json" "$SOP_FILE" "$DELEGATION_ID" "$AGENT_ID" <<'PY'
import json, sys
from pathlib import Path
out_path = Path(sys.argv[1])
intake = json.loads(Path(sys.argv[2]).read_text())
sop = Path(sys.argv[3]).read_text()
delegation_id = sys.argv[4]
agent_id = sys.argv[5]
ops = [item.get("id", "") for item in intake.get("recommended_operations", [])]
selected = []
for item in ops:
    if item == "ingest_playbook" and item not in selected:
        selected.append(item)
for item in ops:
    if item.startswith("create_skill_draft_") and item not in selected:
        selected.append(item)
        break
for item in ops:
    if item.startswith("create_mcp_draft_") and item not in selected:
        selected.append(item)
        break
if not selected:
    raise SystemExit("no applicable operation_ids found in intake response")
payload = {
    "message": "Import this SOP and prepare the required skill and MCP setup",
    "resource_name": "Weekly Report SOP",
    "markdown_sop": sop,
    "agent_id": agent_id,
    "delegation_profile_id": delegation_id,
    "operation_ids": selected,
}
out_path.write_text(json.dumps(payload, ensure_ascii=False))
print("selected operation_ids:", ", ".join(selected))
PY
post_json POST "$API_BASE/api/agent/apply" "$WORK_DIR/apply_payload.json" "$WORK_DIR/apply.json"
render_json "$WORK_DIR/apply.json"

log "Demo completed"
python3 - "$WORK_DIR/apply.json" <<'PY'
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text())
created = payload.get("created_resources", [])
summary = [f"{item.get('kind')}:{item.get('id')}" for item in created]
print("created resources:")
for line in summary:
    print(f"- {line}")
PY
