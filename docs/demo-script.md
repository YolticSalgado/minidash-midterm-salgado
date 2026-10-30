# 5-minute demo script

Before recording: activate the venv, then delete `minidash.db` so the IDs start at 1.

| Time | Show | Say |
|---|---|---|
| 0:00–0:30 | `docs/requirements.md` | "Track A, scheduled orders. Twelve EARS criteria; here's what's out of scope." |
| 0:30–1:00 | `docs/design.md`: Mermaid diagrams, ADR-001 | "Release runs in an in-app loop; exactly-once comes from one atomic UPDATE. I rejected APScheduler and an external trigger endpoint because…" |
| 1:00–1:30 | Terminal: `pytest -q` and `ruff check .` | "75 tests, one or more per acceptance criterion, using a fixed clock." |
| 1:30–2:00 | Terminal: `uvicorn --factory minidash.app:create_app --app-dir src` | Open http://127.0.0.1:8000/docs |
| 2:00–2:45 | Swagger `POST /orders`, restaurant 5, `scheduled_for` = now + 1 h in UTC with `Z` | 201, status `SCHEDULED`, `scheduled_for` in UTC. |
| 2:45–3:30 | Same request with now + 10 min; then without the `Z`; then restaurant 1 at 23:00Z | 422 `SCHEDULE_TOO_SOON`, `SCHEDULE_TIMEZONE_REQUIRED`, `RESTAURANT_CLOSED`. |
| 3:30–4:00 | `POST /orders/1/cancel` twice | 200 `CANCELLED`, then 409 `ORDER_NOT_CANCELLABLE`. |
| 4:00–4:45 | `tests/test_slice6_release.py` | "Release can't be shown live without waiting, so the tests move a fixed clock: at 17:29:59 it stays SCHEDULED, at 17:30 it's PLACED, and a second run releases nothing." |
| 4:45–5:00 | `AI_LOG.md` entry 10 | "One defect the AI introduced and how it was caught." |

Tip: to get "now + 1 hour" in UTC, run
`(Get-Date).ToUniversalTime().AddHours(1).ToString("yyyy-MM-ddTHH:mm:ssZ")`.
