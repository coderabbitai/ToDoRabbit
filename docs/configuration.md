# Configuration

The backend reads its settings from environment variables, or from a `.env` file in the `backend/` directory.

## Settings

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./todos.db` | SQLAlchemy async database URL. |
| `CORS_ORIGINS` | `["http://localhost:5173", "http://localhost:3000"]` | JSON list of origins allowed to call the API from a browser. |
| `ARCHIVE_RETENTION_DAYS` | `30` | Days to keep archived todos before the nightly cleanup deletes them. |

Example `backend/.env`:

```bash
DATABASE_URL=sqlite+aiosqlite:///./data/todos.db
CORS_ORIGINS=["https://todos.example.com"]
ARCHIVE_RETENTION_DAYS=60
```

## Archived todo retention

Archiving a todo hides it from the default list but keeps the row. The `purge_archived` job removes archived todos once they are older than `ARCHIVE_RETENTION_DAYS`.

Run it manually from the `backend/` directory:

```bash
python -m app.jobs.purge_archived --retention-days 14
```

The repository also ships a scheduled GitHub Actions workflow, `.github/workflows/nightly-cleanup.yml`, that runs the job every day at 03:00 UTC. Set the `DATABASE_URL` repository variable to point it at your database.

## Frontend

The frontend calls the API through the relative path `/api`. In development, Vite proxies it to `http://localhost:8000`. In production, nginx proxies it to the `backend` service, see `frontend/nginx.conf`.
