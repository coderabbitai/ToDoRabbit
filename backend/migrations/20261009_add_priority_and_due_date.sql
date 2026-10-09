-- Adds a priority and an optional due date to todos.
--
-- New databases get these columns from the models. Apply this script once to an
-- existing SQLite database before deploying the matching backend version:
--
--   sqlite3 todos.db < backend/migrations/20261009_add_priority_and_due_date.sql
--
-- Existing rows get the default priority "medium" and no due date.

BEGIN;

ALTER TABLE todos ADD COLUMN priority VARCHAR(16) NOT NULL DEFAULT 'medium';
ALTER TABLE todos ADD COLUMN due_date DATE;

CREATE INDEX IF NOT EXISTS ix_todos_due_date ON todos (due_date);

COMMIT;
