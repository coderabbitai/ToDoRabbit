"""Tests for todo CRUD endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_todo(client: AsyncClient):
    """Test creating a new todo."""
    response = await client.post(
        "/api/todos",
        json={"title": "Test Todo", "description": "Test description"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test description"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_todo_without_description(client: AsyncClient):
    """Test creating a todo without a description."""
    response = await client.post(
        "/api/todos",
        json={"title": "Simple Todo"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Simple Todo"
    assert data["description"] is None
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_list_todos(client: AsyncClient):
    """Test listing all todos."""
    # Create some todos
    await client.post("/api/todos", json={"title": "Todo 1"})
    await client.post("/api/todos", json={"title": "Todo 2"})
    
    response = await client.get("/api/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Todo 2"  # Most recent first
    assert data[1]["title"] == "Todo 1"


@pytest.mark.asyncio
async def test_filter_todos_by_completed(client: AsyncClient):
    """Test filtering todos by completion status."""
    # Create completed and incomplete todos
    response1 = await client.post("/api/todos", json={"title": "Incomplete Todo"})
    todo1_id = response1.json()["id"]
    
    response2 = await client.post("/api/todos", json={"title": "Complete Todo"})
    todo2_id = response2.json()["id"]
    await client.patch(f"/api/todos/{todo2_id}", json={"completed": True})
    
    # Filter for completed todos
    response = await client.get("/api/todos?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Complete Todo"
    assert data[0]["completed"] is True
    
    # Filter for incomplete todos
    response = await client.get("/api/todos?completed=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Incomplete Todo"
    assert data[0]["completed"] is False


@pytest.mark.asyncio
async def test_get_todo(client: AsyncClient):
    """Test retrieving a specific todo."""
    create_response = await client.post(
        "/api/todos",
        json={"title": "Specific Todo", "description": "Details"},
    )
    todo_id = create_response.json()["id"]
    
    response = await client.get(f"/api/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Specific Todo"
    assert data["description"] == "Details"


@pytest.mark.asyncio
async def test_get_nonexistent_todo(client: AsyncClient):
    """Test retrieving a todo that doesn't exist."""
    response = await client.get("/api/todos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient):
    """Test updating a todo."""
    create_response = await client.post(
        "/api/todos",
        json={"title": "Original Title", "description": "Original description"},
    )
    todo_id = create_response.json()["id"]
    
    response = await client.patch(
        f"/api/todos/{todo_id}",
        json={"title": "Updated Title", "completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Original description"
    assert data["completed"] is True


@pytest.mark.asyncio
async def test_update_partial_todo(client: AsyncClient):
    """Test partially updating a todo."""
    create_response = await client.post(
        "/api/todos",
        json={"title": "Original", "description": "Description"},
    )
    todo_id = create_response.json()["id"]
    
    response = await client.patch(
        f"/api/todos/{todo_id}",
        json={"completed": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Original"
    assert data["description"] == "Description"
    assert data["completed"] is True


@pytest.mark.asyncio
async def test_update_nonexistent_todo(client: AsyncClient):
    """Test updating a todo that doesn't exist."""
    response = await client.patch(
        "/api/todos/9999",
        json={"title": "Updated"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient):
    """Test deleting a todo."""
    create_response = await client.post(
        "/api/todos",
        json={"title": "To Delete"},
    )
    todo_id = create_response.json()["id"]
    
    response = await client.delete(f"/api/todos/{todo_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = await client.get(f"/api/todos/{todo_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_todo(client: AsyncClient):
    """Test deleting a todo that doesn't exist."""
    response = await client.delete("/api/todos/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_archive_todo_hides_it_from_default_list(client: AsyncClient):
    """Test that archived todos are excluded from the default list."""
    create_response = await client.post("/api/todos", json={"title": "Old task"})
    todo_id = create_response.json()["id"]

    archive_response = await client.post(f"/api/todos/{todo_id}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["archived_at"] is not None

    default_list = await client.get("/api/todos")
    assert default_list.json() == []

    full_list = await client.get("/api/todos?include_archived=true")
    assert [todo["id"] for todo in full_list.json()] == [todo_id]


@pytest.mark.asyncio
async def test_archive_nonexistent_todo(client: AsyncClient):
    """Test archiving a todo that doesn't exist."""
    response = await client.post("/api/todos/9999/archive")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"
