# CeleryApp Makefile

.PHONY: help build up down logs test clean init-db run-tasks stats

# Default target
help:
	@echo "Available commands:"
	@echo "  build       - Build Docker images"
	@echo "  up          - Start all services"
	@echo "  down        - Stop all services"
	@echo "  logs        - View logs"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean up containers and volumes"
	@echo "  init-db     - Initialize database"
	@echo "  run-tasks   - Run tasks manually"
	@echo "  stats       - Show user statistics"

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# Database commands
init-db:
	docker-compose run --rm db-init

# Application commands
run-tasks:
	docker-compose exec celery-worker python main.py run-tasks

stats:
	docker-compose exec celery-worker python main.py stats

# Testing
test:
	docker-compose exec celery-worker pytest

test-cov:
	docker-compose exec celery-worker pytest --cov=app --cov-report=html

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f

# Development
dev-setup:
	pip install -r requirements.txt
	cp env.example .env

dev-test:
	pytest

dev-run-worker:
	celery -A app.celery_app worker --loglevel=info

dev-run-beat:
	celery -A app.celery_app beat --loglevel=info

dev-run-flower:
	celery -A app.celery_app flower --port=5555
