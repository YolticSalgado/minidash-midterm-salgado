# AGENTS.md — rules for AI coding assistants on MiniDash

## Stack
- Python 3.12+ (developed on 3.14), FastAPI, SQLite via the standard-library `sqlite3` module.
- Tests: pytest with FastAPI's `TestClient`. Lint/format: ruff (`ruff check .`, `ruff format .`).

## Architecture (do not blur these layers)
- `routes.py` — HTTP only: parse input, call a service, return the result. No SQL.
- `services.py` / `scheduling.py` — business rules. No HTTP objects, no SQL strings.
- `repository.py` — every SQL statement lives here.
- Domain errors are raised as `DomainError` subclasses (`errors.py`); the app turns them into
  `{"error": {"code": ..., "message": ...}}` responses.

## Conventions
1. **Never call `datetime.now()` in business logic.** Time comes from the injected `Clock`
   (`clock.py`). Tests use a fixed clock.
2. **All datetimes are timezone-aware UTC.** Store them with `to_db()` so they compare correctly
   as text in SQLite. Reject naive datetimes from clients.
3. **Every acceptance criterion in `docs/requirements.md` has a test** named after its ID
   (e.g. `test_ac1_...`). Write or approve the test before the implementation.
4. Use parameterized SQL (`?` placeholders). Never build SQL from strings.

## Do-not rules
- Do not add a dependency without it being listed in `docs/design.md` and checked on PyPI.
- Do not touch files outside the current slice in `docs/tasks.md`.
- Do not weaken, skip, or delete a test to make the build green.
- Never put secrets, API keys, or personal data in code, tests, or prompts.
