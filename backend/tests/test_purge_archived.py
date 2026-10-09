"""Tests for the archived todo purge job."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.purge_archived import DEFAULT_RETENTION_DAYS, purge_archived
from app.models import Todo

NOW = datetime(2026, 3, 1, 3, 0, tzinfo=timezone.utc)


def make_todo(title: str, archived_days_ago: int | None) -> Todo:
    archived_at = None if archived_days_ago is None else NOW - timedelta(days=archived_days_ago)
    return Todo(title=title, archived_at=archived_at)


async def remaining_titles(session: AsyncSession) -> list[str]:
    result = await session.execute(select(Todo.title).order_by(Todo.title))
    return list(result.scalars().all())


@pytest.mark.asyncio
async def test_purges_todos_archived_before_the_cutoff(test_db: AsyncSession):
    test_db.add_all([make_todo("Archived long ago", 45), make_todo("Archived last week", 7)])
    await test_db.commit()

    deleted = await purge_archived(test_db, retention_days=30, now=NOW)

    assert deleted == 1
    assert await remaining_titles(test_db) == ["Archived last week"]


@pytest.mark.asyncio
async def test_keeps_todos_that_are_not_archived(test_db: AsyncSession):
    test_db.add_all([make_todo("Still active", None), make_todo("Archived long ago", 90)])
    await test_db.commit()

    deleted = await purge_archived(test_db, retention_days=30, now=NOW)

    assert deleted == 1
    assert await remaining_titles(test_db) == ["Still active"]


@pytest.mark.asyncio
async def test_returns_zero_when_nothing_is_eligible(test_db: AsyncSession):
    test_db.add_all([make_todo("Active", None), make_todo("Archived yesterday", 1)])
    await test_db.commit()

    assert await purge_archived(test_db, retention_days=30, now=NOW) == 0
    assert await remaining_titles(test_db) == ["Active", "Archived yesterday"]


@pytest.mark.asyncio
async def test_uses_the_default_retention_window(test_db: AsyncSession):
    test_db.add_all(
        [
            make_todo("Just inside the window", DEFAULT_RETENTION_DAYS - 1),
            make_todo("Just outside the window", DEFAULT_RETENTION_DAYS + 1),
        ]
    )
    await test_db.commit()

    deleted = await purge_archived(test_db, now=NOW)

    assert deleted == 1
    assert await remaining_titles(test_db) == ["Just inside the window"]


@pytest.mark.asyncio
async def test_rejects_a_retention_window_below_one_day(test_db: AsyncSession):
    with pytest.raises(ValueError):
        await purge_archived(test_db, retention_days=0, now=NOW)
