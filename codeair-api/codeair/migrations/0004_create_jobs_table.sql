-- +goose Up
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    agent_id UUID NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    started_at TIMESTAMP NULL,
    ended_at TIMESTAMP NULL,

    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

-- For filtering jobs by agent AND ordering by created_at (compound index)
CREATE INDEX idx_jobs_agent_id_created_at ON jobs(agent_id, created_at DESC);

-- For finding pending jobs ordered by creation time
CREATE INDEX idx_jobs_pending_created_at ON jobs(created_at ASC) WHERE started_at IS NULL;

-- +goose Down
DROP TABLE IF EXISTS jobs;
