CREATE TABLE IF NOT EXISTS goals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    objective TEXT NOT NULL,
    constraints_json TEXT NOT NULL,
    definition_of_done_json TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    budget_amount TEXT,
    budget_currency TEXT NOT NULL,
    due_at TEXT,
    owner_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS playbooks (
    id TEXT PRIMARY KEY,
    goal_id TEXT,
    name TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    source_uri TEXT NOT NULL,
    compiled_spec_json TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goal_id) REFERENCES goals(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    playbook_id TEXT NOT NULL,
    parent_task_id TEXT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    priority INTEGER NOT NULL,
    depends_on_json TEXT NOT NULL,
    assigned_skill_id TEXT,
    approval_required INTEGER NOT NULL,
    queue_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goal_id) REFERENCES goals(id),
    FOREIGN KEY(playbook_id) REFERENCES playbooks(id),
    FOREIGN KEY(parent_task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    status TEXT NOT NULL,
    worker_type TEXT NOT NULL,
    trace_id TEXT,
    session_id TEXT,
    started_at TEXT,
    finished_at TEXT,
    error_class TEXT,
    error_message TEXT,
    metrics_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS reflections (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    failure_category TEXT NOT NULL,
    summary TEXT NOT NULL,
    proposal_json TEXT NOT NULL,
    eval_status TEXT NOT NULL,
    approval_status TEXT NOT NULL,
    approved_by TEXT,
    published_target_version TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    uri TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    checksum TEXT,
    version TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);
