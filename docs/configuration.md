# Configuration

The backend reads its settings from environment variables, or from a `.env` file in the `backend/` directory.

## Settings

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./todos.db` | SQLAlchemy async database URL. |
| `CORS_ORIGINS` | `["http://localhost:5173", "http://localhost:3000"]` | JSON list of origins allowed to call the API from a browser. |
| `ARCHIVE_RETENTION_DAYS` | `30` | Days to keep archived todos before the nightly cleanup deletes them. |
| `AUTH_ENABLED` | `false` | Require a session cookie for `/api/todos`. See [Authentication](#authentication). |
| `AUTH_USERNAME` | `admin` | Username accepted by `POST /api/auth/login`. |
| `AUTH_PASSWORD` | empty | Password accepted by `POST /api/auth/login`. Required when authentication is enabled. |
| `SESSION_SECRET` | empty | Secret used to sign session cookies. Required when authentication is enabled. |
| `SESSION_TTL_MINUTES` | `60` | How long a session stays valid after login, in minutes. |
| `SESSION_COOKIE_SECURE` | `true` | Send the session cookie over HTTPS only. Set to `false` for local development over plain HTTP. |

Example `backend/.env`:

```bash
DATABASE_URL=sqlite+aiosqlite:///./data/todos.db
CORS_ORIGINS=["https://todos.example.com"]
ARCHIVE_RETENTION_DAYS=60
```

## Authentication

Authentication is off by default. Set `AUTH_ENABLED=true` together with `AUTH_PASSWORD` and `SESSION_SECRET` to protect the todo endpoints. The backend refuses to start if either value is missing.

```bash
curl -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

curl -b cookies.txt http://localhost:8000/api/todos
```

A successful login sets an `HttpOnly`, `SameSite=Lax` cookie that expires after `SESSION_TTL_MINUTES`. `POST /api/auth/logout` clears it. Use a long random value for `SESSION_SECRET`, and keep it the same across all backend instances. Changing it signs everyone out. `/api/health` stays public.

## Archived todo retention

Archiving a todo hides it from the default list but keeps the row. The `purge_archived` job removes archived todos once they are older than `ARCHIVE_RETENTION_DAYS`.

Run it manually from the `backend/` directory:

```bash
python -m app.jobs.purge_archived --retention-days 14
```

The repository also ships a scheduled GitHub Actions workflow, `.github/workflows/nightly-cleanup.yml`, that runs the job every day at 03:00 UTC. Set the `DATABASE_URL` repository variable to point it at your database.

## Frontend

The frontend calls the API through the relative path `/api`. In development, Vite proxies it to `http://localhost:8000`. In production, nginx proxies it to the `backend` service, see `frontend/nginx.conf`.
