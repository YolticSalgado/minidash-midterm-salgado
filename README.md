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
| GET | `/restaurants` | List restaurants with cuisine, opening hours, and average prep time |
| GET | `/restaurants/{id}/menu` | List one restaurant's menu items |
| POST | `/orders` | Place an order |
| GET | `/orders/{id}` | Get one order with its items, total, and status |
| PATCH | `/orders/{id}/status` | Update order status (restaurant and driver tools) |

Errors use one shape: `{"error": {"code": "ORDER_NOT_FOUND", "message": "..."}}`.

## Project layout

```
src/minidash/   application code (routes → services → repository → SQLite)
tests/          pytest suite
AGENTS.md       rules for AI coding assistants
```
