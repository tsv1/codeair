-- +goose Up
CREATE TABLE IF NOT EXISTS job_logs (
    job_id INTEGER PRIMARY KEY,
    exit_code INTEGER NOT NULL,
    stdout TEXT NULL,
    stderr TEXT NULL,
    elapsed_ms INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,

    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Index for ordering logs by created_at
CREATE INDEX idx_job_logs_created_at ON job_logs(created_at DESC);

-- +goose Down
DROP TABLE IF EXISTS job_logs;
