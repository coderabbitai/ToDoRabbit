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

## Next steps

- Browse the [API reference](api-reference.md) to see every endpoint.
- Read about [configuration](configuration.md) options.
- Follow the [deployment guide](deployment.md) to run ToDoRabbit on a server.
