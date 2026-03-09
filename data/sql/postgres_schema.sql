CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    objective TEXT NOT NULL,
    constraints_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    definition_of_done_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    risk_level TEXT NOT NULL,
    budget_amount NUMERIC(18, 2),
    budget_currency TEXT NOT NULL DEFAULT 'USD',
    due_at TIMESTAMPTZ,
    owner_id TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);

CREATE TABLE IF NOT EXISTS playbooks (
    id UUID PRIMARY KEY,
    goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    source_uri TEXT NOT NULL,
    compiled_spec_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_playbooks_goal_id ON playbooks(goal_id);
CREATE INDEX IF NOT EXISTS idx_playbooks_status ON playbooks(status);

CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    input_schema_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    output_schema_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    required_mcp_servers_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    approval_policy_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    evaluation_policy_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    rollback_version TEXT,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_skills_status ON skills(status);

CREATE TABLE IF NOT EXISTS mcp_servers (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    transport TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    scopes_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    auth_config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mcp_servers_status ON mcp_servers(status);

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY,
    goal_id UUID NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    playbook_id UUID NOT NULL REFERENCES playbooks(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    depends_on_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    assigned_skill_id UUID,
    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
    queue_name TEXT NOT NULL DEFAULT 'default',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_goal_id ON tasks(goal_id);
CREATE INDEX IF NOT EXISTS idx_tasks_playbook_id ON tasks(playbook_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

CREATE TABLE IF NOT EXISTS runs (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    attempt INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL,
    worker_type TEXT NOT NULL,
    trace_id TEXT,
    session_id TEXT,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    error_class TEXT,
    error_message TEXT,
    metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_task_id ON runs(task_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);

CREATE TABLE IF NOT EXISTS reflections (
    id UUID PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    failure_category TEXT NOT NULL,
    summary TEXT NOT NULL,
    proposal_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    eval_status TEXT NOT NULL,
    approval_status TEXT NOT NULL,
    approved_by TEXT,
    published_target_version TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reflections_run_id ON reflections(run_id);
CREATE INDEX IF NOT EXISTS idx_reflections_eval_status ON reflections(eval_status);

CREATE TABLE IF NOT EXISTS artifacts (
    id UUID PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    uri TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    checksum TEXT,
    version TEXT NOT NULL DEFAULT '1',
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_artifacts_run_id ON artifacts(run_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_kind ON artifacts(kind);
