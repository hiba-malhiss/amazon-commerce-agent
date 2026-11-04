### validate:
--
`uv run ruff check .
uv run ruff format .
uv run python -c "from app.config.validator import validate_config; validate_config(); print('Configuration valid!')"
`
### run test
---
`uv run python -m pytest tests/test_config.py -v`

### lint: 
uv run ruff check . --fix                 
uv run ruff format .

### run backend:
cd ~/Desktop/amazon-commerce-agent

# 1. Start Postgres (if it isn't already running)
docker compose up -d postgres

# 2. Apply database migrations
cd backend
.venv/bin/alembic upgrade head

# 3. Start the backend
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
