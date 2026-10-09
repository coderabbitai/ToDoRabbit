.PHONY: up down test-backend test-frontend test clean

# Start all services with Docker Compose
up:
	docker compose up --build

# Stop all services
down:
	docker compose down

# Run backend tests using pytest
test-backend:
	cd backend && python -m pytest

# Run frontend type checking and unit tests
test-frontend:
	cd frontend && npm run lint && npm test

# Run all tests (backend + frontend)
test: test-backend test-frontend

# Clean up Docker resources and build artifacts
clean:
	docker compose down -v
	docker system prune -f
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
