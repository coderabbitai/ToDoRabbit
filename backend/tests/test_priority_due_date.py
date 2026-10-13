"""Tests for todo priority and due date, including the SQL migration."""

import sqlite3
from pathlib import Path

import pytest
from httpx import AsyncClient

MIGRATION = Path(__file__).parent.parent / "migrations" / "20261009_add_priority_and_due_date.sql"


@pytest.mark.asyncio
async def test_new_todos_default_to_medium_priority(client: AsyncClient):
    response = await client.post("/api/todos", json={"title": "Plan sprint"})
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == "medium"
    assert data["due_date"] is None


@pytest.mark.asyncio
async def test_create_todo_with_priority_and_due_date(client: AsyncClient):
    response = await client.post(
        "/api/todos",
        json={"title": "Ship release", "priority": "high", "due_date": "2026-11-01"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == "high"
    assert data["due_date"] == "2026-11-01"


@pytest.mark.asyncio
async def test_update_priority_and_due_date(client: AsyncClient):
    created = await client.post("/api/todos", json={"title": "Review PRs"})
    todo_id = created.json()["id"]

    response = await client.patch(
        f"/api/todos/{todo_id}",
        json={"priority": "low", "due_date": "2026-12-24"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "low"
    assert data["due_date"] == "2026-12-24"
    assert data["title"] == "Review PRs"


@pytest.mark.asyncio
async def test_rejects_unknown_priority(client: AsyncClient):
    response = await client.post("/api/todos", json={"title": "Bad", "priority": "urgent"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rejects_malformed_due_date(client: AsyncClient):
    response = await client.post("/api/todos", json={"title": "Bad", "due_date": "next week"})
    assert response.status_code == 422


def test_migration_upgrades_an_existing_database(tmp_path: Path):
    db_path = tmp_path / "legacy.db"
    connection = sqlite3.connect(db_path)
    connection.executescript(
        """
        CREATE TABLE todos (
            id INTEGER NOT NULL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            completed BOOLEAN NOT NULL,
            archived_at DATETIME,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        );
        INSERT INTO todos (title, completed, created_at, updated_at)
        VALUES ('Existing todo', 0, '2026-01-01 00:00:00', '2026-01-01 00:00:00');
        """
    )

    connection.executescript(MIGRATION.read_text())

    columns = {row[1] for row in connection.execute("PRAGMA table_info(todos)")}
    assert {"priority", "due_date"} <= columns
    row = connection.execute("SELECT priority, due_date FROM todos").fetchone()
    assert row == ("medium", None)
    connection.close()
