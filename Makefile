.PHONY: install-backend install-frontend install ingest dev test lint format clean

install-backend:
	cd backend && poetry install

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend

ingest:
	cd backend && poetry run python -m app.ingestion.download_10k
	cd backend && poetry run python -m app.ingestion.indexer_job

dev:
	@echo "Starting backend and frontend servers..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:5173"
	@cd backend && poetry run uvicorn app.main:app --reload --port 8000 & \
	cd frontend && npm run dev

test:
	cd backend && poetry run pytest -q

lint:
	cd backend && poetry run ruff check .
	cd frontend && npm run lint

format:
	cd backend && poetry run black .
	cd backend && poetry run ruff check --fix .

clean:
	rm -rf backend/.venv
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf data/
