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

## Updating

```bash
git pull
docker compose up --build -d
```

Compose rebuilds only the images whose inputs changed.
