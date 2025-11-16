-- +goose Up
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    created_by INTEGER NOT NULL,
    webhook_id UUID NOT NULL,

    CONSTRAINT uk_projects_webhook_id UNIQUE (webhook_id),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- +goose Down
DROP TABLE IF EXISTS projects;
