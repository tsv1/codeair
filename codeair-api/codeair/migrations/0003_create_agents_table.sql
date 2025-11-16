-- +goose Up
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY,
    project_id INTEGER NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    engine VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    enabled BOOLEAN NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    created_by INTEGER NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    updated_by INTEGER NOT NULL,

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE RESTRICT
);

-- For filtering by project
CREATE INDEX idx_agents_project_id ON agents(project_id);

-- For the common query: find by project + order by created_at
CREATE INDEX idx_agents_project_created ON agents(project_id, created_at DESC);

-- +goose Down
DROP TABLE IF EXISTS agents;
