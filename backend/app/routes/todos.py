"""Todo CRUD endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Todo
from app.schemas import TodoCreate, TodoResponse, TodoUpdate

router = APIRouter(prefix="/api/todos", tags=["todos"])


def _like_pattern(term: str) -> str:
    """Build a case-insensitive "contains" pattern, escaping LIKE wildcards in the term."""
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


@router.get("", response_model=list[TodoResponse])
async def list_todos(
    completed: bool | None = Query(None, description="Filter by completion status"),
    include_archived: bool = Query(False, description="Include archived todos"),
    search: str | None = Query(
        None,
        min_length=1,
        max_length=100,
        description="Only return todos whose title or description contains this text",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[Todo]:
    """Retrieve all todos, optionally filtered by completion status."""
    query = select(Todo).order_by(Todo.created_at.desc())

    if completed is not None:
        query = query.where(Todo.completed == completed)

    if not include_archived:
        query = query.where(Todo.archived_at.is_(None))

    if search:
        pattern = _like_pattern(search)
        query = query.where(
            or_(
                Todo.title.ilike(pattern, escape="\\"),
                Todo.description.ilike(pattern, escape="\\"),
            )
        )
    
    result = await db.execute(query)
    todos = result.scalars().all()
    return list(todos)


@router.post("", response_model=TodoResponse, status_code=201)
async def create_todo(
    todo_data: TodoCreate,
    db: AsyncSession = Depends(get_db),
) -> Todo:
    """Create a new todo item."""
    todo = Todo(
        title=todo_data.title,
        description=todo_data.description,
    )
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
) -> Todo:
    """Retrieve a specific todo by ID."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    return todo


@router.patch("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    db: AsyncSession = Depends(get_db),
) -> Todo:
    """Update an existing todo item."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    update_data = todo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)
    
    todo.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a todo item."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()
    
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    await db.delete(todo)
    await db.commit()


@router.post("/{todo_id}/archive", response_model=TodoResponse)
async def archive_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
) -> Todo:
    """Archive a todo so it no longer shows up in the default list."""
    result = await db.execute(select(Todo).where(Todo.id == todo_id))
    todo = result.scalar_one_or_none()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.archived_at is None:
        todo.archived_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(todo)

    return todo
