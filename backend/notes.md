# Security
#### What it already does:
- Read-only tools. It can only search and fetch details, so a prompt injection can't cause any action.
- Tools come only from config: an unknown tool fails in params_check.
- Required parameters are checked before any API call.
- References are validated in code: only visible products, the quote must be in the message, and the product id comes from stored data, never from the LLM.
- Limits: message length, at most 5 requests per turn, token budgets per prompt.
- External data is passed to the reply as "data, not instructions".
- Safe UI markdown: no raw HTML is rendered.
- No secrets in prompts. API keys stay in .env, which isn't tracked in git.

#### Missing:
- capping and cleaning API text before the reply sees it
- rate limiting per user or IP & Auth

---

# Evaluation

#### What it already has:
- one LangSmith eval: 8 one-turn Understanding cases, graded per field

#### Missing:
- unit tests (the old ones were deleted)
- Understanding cases with references and follow-ups
- multi-turn conversations with a fake SearchApi
- adversarial cases (injection in product titles, odd input)
- an LLM judge for reply quality

---

# Monitoring

#### What it already has:
- structured events per node, with statuses (started / completed / failnts panel
- the exact system prompts sent each turn, in the Prompts panel
- API call details: URL, parameters, status code, duration
- outcomes per request: success / missing_info / needs_clarification /
- conversations saved in Postgres (threads, messages, cards, checkpoint

#### Missing:
- traces stored and searchable (LangSmith tracing)
- metrics and alerts (outcome counts, error rate, latency, tokens and c
- a sampled LLM judge on real replies
- 👍/👎 feedback

---

## Development Guide

### 1. Validate the Project

Run the following commands to check code quality, formatting, and application configuration.

```bash
# Check code quality
uv run ruff check .

# Format code
uv run ruff format .

# Validate application configuration
uv run python -c "from app.config.validator import validate_config; validate_config(); print('Configuration valid!')"
```

### 2. Run Tests

Run the configuration tests using pytest:

```bash
uv run python -m pytest tests/test_config.py -v
```

### 3. Lint and Format

Automatically fix linting issues and format the code:

```bash
# Fix linting issues
uv run ruff check . --fix

# Format code
uv run ruff format .
```

### 4. Run the Backend Locally

#### Step 1: Navigate to the Project Directory

```bash
cd ~/Desktop/amazon-commerce-agent
```

#### Step 2: Start PostgreSQL

Make sure Docker is running, then start the PostgreSQL service:

```bash
docker compose up -d postgres
```

#### Step 3: Apply Database Migrations

Navigate to the backend directory and apply the latest Alembic migrations:

```bash
cd backend
.venv/bin/alembic upgrade head
```

#### Step 4: Start the Backend Server

Start the FastAPI application with automatic reload enabled:

```bash
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at:

- **API:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### Quick Start

Once dependencies and configuration are set up, use these commands to start the backend:

```bash
cd ~/Desktop/amazon-commerce-agent

# Start PostgreSQL
docker compose up -d postgres

# Apply migrations
cd backend
.venv/bin/alembic upgrade head

# Start FastAPI
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
