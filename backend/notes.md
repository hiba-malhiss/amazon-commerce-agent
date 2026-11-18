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
./scripts/dev.sh
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

---

# Entity references & card display — issues faced and fixes

### Approach (how it works)

A turn flows `understand → request_resolver → tool_workflow → collect → respond`.
Two ideas keep "which result did the user mean?" honest:

- **Deterministic cards.** Application code (`numbered_cards`) selects and orders the cards
  the user sees, capped by config (`max_cards_per_reply`). The response LLM only *describes*
  them — it never chooses or reorders what is displayed.
- **Grounded references.** The Understanding LLM maps the user's words to visible results,
  then **code** (`check_references`) validates that the reference is real and the quote is
  the user's own words — the model can't invent a reference. The product id always comes
  from stored data, never the LLM.

### Issues we hit and how we fixed them

1. **Cards and the reply disagreed on order.** A search returned an off-topic result
   (a monitor for a TV query) as card #1; the reply dropped it from its prose but the card
   stayed, so "the first option" was ambiguous (card #1 ≠ first named in text).
   *Fix:* cards are selected/ordered deterministically by `numbered_cards` and the reply is
   told to describe results in card order; `collect`/`service` show exactly those cards.
   (We deliberately did **not** add relevance filtering yet — evaluate first.)

2. **"The first option" resolved to an older results list.** With several lists on screen,
   a bare position was read against the wrong one.
   *Fix:* `visible_briefs` feeds Understanding newest-list-first, numbered from 1, and the
   prompt states a bare position counts within the most recent list.

3. **"Compare it to the third option" showed only one card.** The model resolved "it"
   correctly but quoted the product's *name* (or an invented "the first option") instead of
   "it", so `check_references` rejected it with "Which item do you mean?" → that request
   returned no entity → one card.
   *Fix:* `check_references` now accepts a quote that **names the referenced visible result**
   (`quote_names_references`), and the name-ambiguity check (rule 3) only runs for quotes
   taken from the user's own message. Both requests resolve → both cards show. The displayed
   cards are the successful outcomes' entities, combined by `numbered_cards`.

4. **Language-specific stopwords.** `quote_names_references` first filtered English filler
   words, which breaks for other languages.
   *Fix:* it now compares the quote's words to the result's label words and accepts when at
   least half overlap — no hard-coded word list, so it works in any language.

5. **Prompts were commerce/Amazon-specific.** To reuse the agent for other companies, the
   domain now lives only in config (`AGENT_OBJECTIVE`); the Understanding and response
   prompts use generic wording ("results"/"items", not "products"/"TVs"/brand names).

### Still open (evaluate before fixing)

- **Search relevance.** Off-topic results (a monitor for "TV") still appear as cards; we only
  fixed the card/text consistency, not retrieval quality.
- **RAG answerability.** A topically-near chunk can be retrieved for a question the document
  doesn't actually answer (e.g. "cancel after it ships"); a cosine threshold can't separate
  answerable from not-answerable (measured). Needs a relevance grader or citation check.
