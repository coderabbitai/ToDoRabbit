# API cookbook

Copy-paste recipes for working with the ToDoRabbit API from a terminal. All examples assume the backend is running on `http://localhost:8000`. See the [API reference](api-reference.md) for every endpoint and field.

## Check that the API is up

```bash
curl http://localhost:8000/health
```

You should see `{"status":"healthy"}`.

## Create a todo

```bash
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Book flights", "description": "Check the dates with the team first"}'
```

The response contains the new todo, including its `id`.

## List open todos

```bash
curl "http://localhost:8000/api/todos?completed=false"
```

## Mark a todo as done

Replace `1` with the `id` of the todo you want to update.

```bash
curl -X PUT http://localhost:8000/api/todo/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

## Archive a todo

```bash
curl -X POST http://localhost:8000/api/todos/1/archive
```

Archived todos are hidden from the default list.

## List archived todos too

```bash
curl "http://localhost:8000/api/todos?archived=true"
```

## Delete a todo

```bash
curl -X DELETE http://localhost:8000/api/todos/1
```

A successful delete returns `204 No Content` and an empty body.
