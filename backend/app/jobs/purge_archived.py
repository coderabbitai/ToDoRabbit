"""Nightly job that permanently deletes todos archived for longer than the retention window."""

import argparse
import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import Base
from app.models import Todo

logger = logging.getLogger("todorabbit.jobs.purge_archived")

DEFAULT_RETENTION_DAYS = 30


@dataclass(frozen=True)
class PurgeSummary:
    """Outcome of a purge run."""

    deleted: int
    cutoff: datetime


async def purge_archived(
    session: AsyncSession,
    retention_days: int = DEFAULT_RETENTION_DAYS,
    now: datetime | None = None,
) -> PurgeSummary:
    """Delete todos that were archived more than ``retention_days`` days ago.

    Returns a summary with the number of deleted todos and the cutoff that was applied.
    """
    if retention_days < 1:
        raise ValueError("retention_days must be at least 1")

    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=retention_days)
    result = await session.execute(
        delete(Todo).where(Todo.archived_at.is_not(None), Todo.archived_at < cutoff)
    )
    await session.commit()
    return PurgeSummary(deleted=result.rowcount, cutoff=cutoff)


async def run(retention_days: int, database_url: str) -> PurgeSummary:
    """Connect to the database, purge archived todos and return the summary."""
    engine = create_async_engine(database_url, echo=False, future=True)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as session:
            return await purge_archived(session, retention_days)
    finally:
        await engine.dispose()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Delete todos archived longer than N days ago.")
    parser.add_argument(
        "--retention-days",
        type=int,
        default=int(os.environ.get("ARCHIVE_RETENTION_DAYS", DEFAULT_RETENTION_DAYS)),
        help="Keep archived todos for this many days (default: %(default)s)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    summary = asyncio.run(run(args.retention_days, settings.database_url))
    logger.info(
        "Purged %d archived todo(s) archived before %s",
        summary.deleted,
        summary.cutoff.isoformat(),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
