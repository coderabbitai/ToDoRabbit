# Deployment

ToDoRabbit ships as two containers: the FastAPI backend and an nginx container that serves the built frontend and proxies `/api` to the backend.

## Docker Compose

```bash
docker compose up --build -d
```

The frontend is available on port 3000 and the API on port 8000. Check that the backend is healthy:

```bash
curl http://localhost:8000/api/health
```

## Persist the database

By default the SQLite file lives inside the backend container and is lost when the container is recreated. Mount a volume and point `DATABASE_URL` at it:

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=sqlite+aiosqlite:////data/todos.db
    volumes:
      - todo-data:/data

volumes:
  todo-data:
```

Save this as `docker-compose.override.yml` next to `docker-compose.yml`, and Compose picks it up automatically.

## Allow your domain

If you serve the frontend from your own domain, add it to `CORS_ORIGINS` on the backend, for example `CORS_ORIGINS=["https://todos.example.com"]`. See [configuration](configuration.md) for all settings.

## Upgrade an existing database

The backend creates missing tables on startup but never alters existing ones. When a release adds columns, apply the matching script from `backend/migrations/` once before you deploy it. Take a copy of the database file first.

```bash
cp todos.db todos.db.bak
sqlite3 todos.db < backend/migrations/20261009_add_priority_and_due_date.sql
```

## Updating

```bash
git pull
docker compose up --build -d
```

Compose rebuilds only the images whose inputs changed.
