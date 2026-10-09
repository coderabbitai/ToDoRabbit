# API reference

The backend exposes a JSON REST API under `/api`. When the backend is running, interactive documentation is available at `/docs`.

## The todo object

```json
{
  "id": 1,
  "title": "Write release notes",
  "description": "Cover the new archive endpoint",
  "completed": false,
  "archived_at": null,
  "created_at": "2026-03-01T09:30:00Z",
  "updated_at": "2026-03-01T09:30:00Z"
}
```

## Endpoints

### List todos

```http
GET /api/todos
```

Returns todos, newest first. Archived todos are hidden unless you ask for them.

| Query parameter | Type | Description |
| --- | --- | --- |
| `completed` | boolean | Return only completed or only open todos. |
| `include_archived` | boolean | Include archived todos. Defaults to `false`. |
| `search` | string | Only return todos whose title or description contains the text, ignoring case. 1 to 100 characters. |

```bash
curl "http://localhost:8000/api/todos?completed=false"
curl "http://localhost:8000/api/todos?search=milk"
```

### Create a todo

```http
POST /api/todos
```

The body requires a `title` (1 to 255 characters) and accepts an optional `description`. Responds with `201 Created` and the new todo.

```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Write release notes", "description": "Cover the new archive endpoint"}'
```

### Get a todo

```http
GET /api/todos/{id}
```

Responds with `404 Not Found` if the todo does not exist.

### Update a todo

```http
PATCH /api/todos/{id}
```

Send only the fields you want to change: `title`, `description`, or `completed`.

```bash
curl -X PATCH http://localhost:8000/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Archive a todo

```http
POST /api/todos/{id}/archive
```

Sets `archived_at` and removes the todo from the default list. Archiving an already archived todo leaves the original timestamp in place. Archived todos are deleted permanently after the retention period, see [configuration](configuration.md#archived-todo-retention).

### Delete a todo

```http
DELETE /api/todos/{id}
```

Responds with `204 No Content`.

### Health check

```http
GET /api/health
```

Returns `{"status": "healthy"}`. Used by the Docker Compose health check.
