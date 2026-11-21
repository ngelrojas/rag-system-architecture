-- sql/001_outbox.sql — tables for the outbox pattern (3.8)
-- Loaded automatically by docker compose (docker-entrypoint-initdb.d).

CREATE TABLE IF NOT EXISTS chunks (
    key        TEXT PRIMARY KEY,
    embedding  REAL[] NOT NULL,
    metadata   JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS outbox (
    id          UUID PRIMARY KEY,
    event_type  TEXT NOT NULL,
    payload     JSONB NOT NULL,
    published   BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS outbox_unpublished ON outbox (created_at) WHERE published = false;
