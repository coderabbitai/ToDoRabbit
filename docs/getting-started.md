# Getting started

This guide walks you through running ToDoRabbit on your machine, either with Docker or as two local processes.

## Run with Docker

You need Docker and Docker Compose.

```bash
make up
```

This builds both images and starts the services:

| Service | URL |
| --- | --- |
| Frontend | <http://localhost:3000> |
| Backend API | <http://localhost:8000> |
| Interactive API docs | <http://localhost:8000/docs> |

Stop everything with `make down`.

## Run without Docker

You need Python 3.11 or newer and Node.js 20 or newer.

Start the backend:

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

In a second terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on port 3000 and proxies `/api` requests to the backend on port 8000.

## Run the tests

```bash
make test-backend   # pytest
make test-frontend  # type check and Vitest
make test           # both
```

## Troubleshooting

### Port 3000 or 8000 is already in use

Stop the process that is using the port, or change the published port in `docker-compose.yml`, for example `"3001:3000"`. To see what is listening on a port, run `lsof -i :3000` for the frontend or `lsof -i :8000` for the backend.

### The frontend shows an API error

The frontend could not reach the backend. Check that the backend is running and healthy:

```bash
curl http://localhost:8000/api/health
```

If you run the frontend with `npm run dev`, the backend must listen on port 8000, because Vite proxies `/api` requests there.

### Browser requests fail with a CORS error

Add the origin you are loading the frontend from to `CORS_ORIGINS`. See [configuration](configuration.md) for the format.

### Start again with an empty database

Stop the app and delete the SQLite file. With the default configuration and a local run, that is `backend/todos.db`. If you changed `DATABASE_URL`, delete the file it points to instead. With Docker Compose, remove the containers and their volumes:

```bash
docker compose down -v
```

## Next steps

- Browse the [API reference](api-reference.md) to see every endpoint.
- Read about [configuration](configuration.md) options.
- Follow the [deployment guide](deployment.md) to run ToDoRabbit on a server.
