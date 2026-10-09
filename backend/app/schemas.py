"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoCreate(BaseModel):
    """Schema for creating a new todo."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class TodoUpdate(BaseModel):
    """Schema for updating an existing todo."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    completed: bool | None = None


class TodoResponse(BaseModel):
    """Schema for todo responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime
