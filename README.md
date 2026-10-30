# MiniDash

A small food-delivery REST API (FastAPI + SQLite) built for CSCI-665 Software Engineering.

## Setup

Requires Python 3.12 or newer (developed on 3.14).

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

On macOS/Linux use `python3 -m venv .venv` and `source .venv/bin/activate`.

## Run the app

```powershell
uvicorn --factory minidash.app:create_app --app-dir src --reload
```

Then open http://127.0.0.1:8000/docs for interactive API docs. The database file
`minidash.db` is created and seeded with 5 restaurants on first start (set `MINIDASH_DB` to
use a different path).

## Run the tests and linter

```powershell
pytest
ruff check .
ruff format --check .
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/restaurants` | List restaurants with cuisine, opening hours (UTC), and average prep time |
| GET | `/restaurants/{id}/menu` | List one restaurant's menu items |
| POST | `/orders` | Place an order now, or schedule it with `scheduled_for` |
| GET | `/orders/{id}` | Get one order with its items, total, status, and `scheduled_for` |
| POST | `/orders/{id}/cancel` | Cancel a scheduled order before it is released |
| PATCH | `/orders/{id}/status` | Update order status (restaurant and driver tools) |

Errors use one shape: `{"error": {"code": "ORDER_NOT_FOUND", "message": "..."}}`.

## Feature: Scheduled Orders (Track A)

A customer can order now for delivery later by adding `scheduled_for` (ISO 8601 **with** a UTC
offset) to `POST /orders`:

- It must be **45 minutes to 7 days** ahead, and the restaurant must be **open** at that time
  (hours are UTC, `[opens_at, closes_at)`). Otherwise the response is 422 with `error.code`
  `SCHEDULE_TOO_SOON`, `SCHEDULE_TOO_FAR`, `SCHEDULE_TIMEZONE_REQUIRED`, or `RESTAURANT_CLOSED`.
- A valid order is stored as `SCHEDULED`. A background loop (every 30 s) moves it to `PLACED`,
  which releases it to the kitchen, **30 minutes before** `scheduled_for`, exactly once.
- `POST /orders/{id}/cancel` cancels it while it is still `SCHEDULED` (409 afterwards).
- All time logic uses an injected `Clock`, so the tests never depend on the real time.

Spec, design, and ADR: [docs/requirements.md](docs/requirements.md),
[docs/design.md](docs/design.md), [docs/tasks.md](docs/tasks.md).
AI use: [AI_LOG.md](AI_LOG.md).

### Try it (PowerShell, with the app running)

Restaurant 5 is open 24 hours, so it works at any time of day.

```powershell
$when = (Get-Date).ToUniversalTime().AddHours(1).ToString("yyyy-MM-ddTHH:mm:ssZ")
$body = @{ restaurant_id = 5; items = @(@{ menu_item_id = 9; quantity = 1 });
           address = "1 Main St"; scheduled_for = $when } | ConvertTo-Json -Depth 3
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/orders -Body $body -ContentType "application/json"
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/orders/1/cancel
```

The Swagger UI at http://127.0.0.1:8000/docs does the same without typing commands.

## Project layout

```
src/minidash/
  app.py          app factory, lifespan (starts/stops the release loop)
  routes.py       HTTP routes
  services.py     ordering logic (place, release, cancel, status)
  scheduling.py   pure scheduling rules (lead time, opening hours, UTC text)
  worker.py       background release loop
  clock.py        Clock / SystemClock
  repository.py   all SQL
  db.py           schema, migration, seed data
tests/            pytest suite (test_sliceN_*.py per feature slice)
docs/             requirements, design + ADR, tasks
AGENTS.md         rules for AI coding assistants
AI_LOG.md         AI usage log
```

## Known follow-ups

- Starlette warns that `httpx` is deprecated for its test client in favor of `httpx2`; the
  pinned `httpx` still works.
- A per-test timeout (`pytest-timeout`) would turn a hung release loop into a fast test failure.
