-- +goose Up
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    last_login_at TIMESTAMP NOT NULL
);

-- +goose Down
DROP TABLE IF EXISTS users;
