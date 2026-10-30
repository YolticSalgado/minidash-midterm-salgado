# AI Usage Log

Tool for every entry: **Claude Code (Anthropic), model Claude Opus 5.5, agent mode inside VS Code**,
with `AGENTS.md` as the rules file. Each entry matches one commit (hash in the Outcome row).
For slices 1–8 the prompt was the slice's entry in `docs/tasks.md` plus its acceptance criteria;
the agent worked from those, under the constraints in `AGENTS.md`.
Entries 2 and 10 are the ones where AI output was rejected or substantially rewritten; entry 9 was
modified before acceptance.

---

### Entry 1

| Field | Entry |
|---|---|
| Entry # / date | 1 / Oct 30, 3:11 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Baseline (not graded) |
| Prompt (summarized) | The Appendix C baseline prompt: FastAPI + SQLite, four tables, five endpoints, routes/services/repository layering, seed 5 restaurants, pytest per endpoint, README, no dependency beyond fastapi, uvicorn, pytest. |
| What the AI produced | The layered app (`db`, `repository`, `services`, `routes`, `app`, `errors`, `schemas`), 11 tests, README. It also needed `httpx`, which Appendix C did not list: FastAPI's `TestClient` requires it. |
| What I verified | Checked fastapi, uvicorn, pytest, httpx, and ruff on pypi.org (official project URLs, versions) before installing, then pinned them. Ran pytest (11 passed) and ruff. |
| What I changed and why | Ruff flagged `Depends()` used as a default argument (B008) in every route. Replaced it with an `Annotated` `Conn` alias, the current FastAPI style. Accepted `httpx` as a test-only dependency because it is required by `TestClient`. |
| Outcome | Modified, then accepted. Commit `2663d22`. |

### Entry 2 — rejected / rewritten output

| Field | Entry |
|---|---|
| Entry # / date | 2 / Oct 30, 3:13 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Spec package (requirements, design + ADR, tasks, AGENTS.md) |
| Prompt (summarized) | Asked for options on the four open decisions (release mechanism, time zones, what "closed" means, cancel API), then to draft the three spec files from my answers. |
| What the AI produced | Three options for each decision with trade-offs. After I chose, it produced the three documents and a commit message. |
| What I verified | That the ADR records the option I picked and names the two I rejected, and that the EARS criteria use the inclusive bounds the assignment states ("at least 45 minutes", "at most 7 days"). |
| What I changed and why | **Rejected the first commit message.** It said "I reviewed boundaries and the out-of-scope list" before any review had happened. An AI-use note that claims verification that did not happen defeats the purpose of the log, so the message was rewritten to say only what was true: I chose the four options and the AI drafted the documents. |
| Outcome | Commit message rewritten before pushing. Commit `f734acc`. |

### Entry 3

| Field | Entry |
|---|---|
| Entry # / date | 3 / Oct 30, 3:14 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Slice 1: inject a clock (AC12) |
| Prompt (summarized) | Add a `Clock` protocol and `SystemClock`; pass `now` into `place_order` instead of calling `datetime.now()`; add `to_db()` for fixed-width UTC text; tests with a fixed clock. Touch only `clock.py`, `scheduling.py`, `services.py`, `routes.py`, `app.py`, `conftest.py`. |
| What the AI produced | The clock module, `to_db()` (rejects naive datetimes), the wiring, a `FixedClock` in `conftest.py`, and 5 tests. |
| What I verified | pytest 16 passed. `grep datetime.now src/` shows it only in `clock.py`. Mutation check: shifted `created_at` by 1 s and the AC12 test failed. |
| What I changed and why | Nothing. Note: the baseline from entry 1 called `datetime.now(UTC)` directly inside `place_order`, which is the defect this slice removes. |
| Outcome | Accepted. Commit `3063379`. |

### Entry 4

| Field | Entry |
|---|---|
| Entry # / date | 4 / Oct 30, 3:16 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Slice 2: `scheduled_for` column, `SCHEDULED` status, migration |
| Prompt (summarized) | Add a nullable `scheduled_for` column with an idempotent migration that runs on startup; existing orders must be unaffected. Migration and model only, no API change. |
| What the AI produced | `db.migrate()` (checks `PRAGMA table_info`, then `ALTER TABLE`), `SCHEDULED` added to `OrderStatus`, `scheduled_for` on the response model, 3 tests including a real baseline-schema database with an old `DELIVERED` order. |
| What I verified | pytest 19 passed. Mutation check: skipping `migrate()` made all 3 tests fail. Ruff found one long line (E501), which was fixed. |
| What I changed and why | Accepted here, but see entry 10: adding `SCHEDULED` to the shared status enum quietly let `PATCH /status` set it. |
| Outcome | Accepted. Commit `90f4235`. |

### Entry 5

| Field | Entry |
|---|---|
| Entry # / date | 5 / Oct 30, 3:17 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Slice 3: lead-time rule `validate_schedule()` (AC3–AC5) |
| Prompt (summarized) | Slice 3 of `tasks.md`: AC3–AC5 with the boundary examples (44:59, 45:00, 46:00 minutes; 7 days; 7 days + 1 s; naive time). Tests first, then a pure function that takes `now` as a parameter. |
| What the AI produced | `validate_schedule(scheduled_for, now)` and 12 parametrized tests. |
| What I verified | pytest 31 passed. Mutation checks, all killed: `<` → `<=`, 45 → 44, `>` → `>=`, and removing the UTC conversion. |
| What I changed and why | Nothing in this slice. In Slice 4 the function gained the restaurant's hours, and the Slice 3 tests were updated to pass "always open" hours (`00:00`–`00:00`), so they keep testing only lead time instead of failing for the wrong reason. |
| Outcome | Accepted. Commit `303e6ae` (test update in `bc56b03`). |

### Entry 6

| Field | Entry |
|---|---|
| Entry # / date | 6 / Oct 30, 3:18 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Slice 4: opening-hours rule `is_open_at()` (AC6) |
| Prompt (summarized) | Slice 4 of `tasks.md` and the requirements' definition of "open" (`[opens_at, closes_at)`, wrap past midnight, equal = 24 h); boundary table test before the function. |
| What the AI produced | `is_open_at()`, the `RESTAURANT_CLOSED` check inside `validate_schedule()` (after the lead-time checks), and 18 tests including a −05:00 offset case. |
| What I verified | pytest 49 passed. 5 mutation checks killed: `<` → `<=`, `<=` → `<`, `or` → `and` (overnight), 24 h → closed, and comparing the caller's local time instead of UTC. |
| What I changed and why | Nothing. |
| Outcome | Accepted. Commit `bc56b03`. |

### Entry 7

| Field | Entry |
|---|---|
| Entry # / date | 7 / Oct 30, 3:19 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Slice 5: `POST /orders` accepts `scheduled_for` (AC1–AC6) |
| Prompt (summarized) | Slice 5 of `tasks.md`: minimal change to the existing `place_order` handler (optional field, call `validate_schedule()`, store UTC, status `SCHEDULED`), keeping the existing error shape. |
| What the AI produced | A 10-line change to `place_order` plus the optional field, and 8 API tests, including a "nothing stored on rejection" check. |
| What I verified | pytest 57 passed. Mutation checks killed: `SCHEDULED` → `PLACED`, and storing the raw input string instead of UTC. Confirmed validation runs before the insert transaction, so a rejected order writes nothing. |
| What I changed and why | Nothing. |
| Outcome | Accepted. Commit `20fff60`. |

### Entry 8

| Field | Entry |
|---|---|
| Entry # / date | 8 / Oct 30, 3:21 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Slice 6: release due orders exactly once (AC7, AC8) |
| Prompt (summarized) | Slice 6 of `tasks.md`. Following the Module 6 tip, the race conditions (double run; release vs. cancel) were listed before any code, then the release function with tests at 30 min 1 s, exactly 30 min, a second run, and only-due-orders. |
| What the AI produced | One atomic `UPDATE … WHERE status='SCHEDULED' AND scheduled_for <= ? RETURNING id`, a service wrapper, and 5 tests including a microsecond boundary. |
| What I verified | pytest 62 passed. Mutation checks killed: `<=` → `<`, dropping the status filter, 30 → 31 min. **One mutant survived** in this file: removing the fixed microsecond format from `to_db()`. Investigated: it is equivalent for comparisons because `+` sorts before `.` in UTC text. It is still killed by the Slice 1 format tests. |
| What I changed and why | Nothing in the code. Recorded the survivor and why it is acceptable. |
| Outcome | Accepted. Commit `2a3e9eb`. |

### Entry 9

| Field | Entry |
|---|---|
| Entry # / date | 9 / Oct 30, 3:26 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Slice 7: background release loop (AC7) |
| Prompt (summarized) | Implement ADR-001: an asyncio loop started and stopped in the FastAPI lifespan; no new dependencies; a failing pass must not kill the loop. |
| What the AI produced | `worker.run_release_loop()` running each pass in `asyncio.to_thread`, a lifespan that starts and stops it, and 5 tests. |
| What I verified | pytest 67 passed. Worker tests repeated 3 times with no flakes. Mutation checks: removing the catch-up pass and narrowing the `except` were caught by failing tests. Making the loop never exit, or removing `stop.set()`, made the suite **hang** instead of fail. |
| What I changed and why | The first plan released on the loop's first tick, which made "release on startup" racy in tests. It was changed to an explicit catch-up release in the lifespan, before serving requests. The hang is noted as a follow-up: `pytest-timeout` would turn it into a fast failure but is a new dependency. |
| Outcome | Modified, then accepted. Commit `647522e`. |

### Entry 10 — rejected / rewritten output

| Field | Entry |
|---|---|
| Entry # / date | 10 / Oct 30, 3:28 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Slice 8: cancel endpoint and status guard (AC9–AC11) |
| Prompt (summarized) | Slice 8 of `tasks.md`: `POST /orders/{id}/cancel`, allowed only while `SCHEDULED`. |
| What the AI produced | The cancel endpoint with an atomic `UPDATE … WHERE id=? AND status='SCHEDULED'`. While checking for other code paths that could change a scheduled order, the review found a defect left by Slice 2. |
| What I verified | **Defect found:** since Slice 2 added `SCHEDULED` to the shared `OrderStatus` enum, the staff `PATCH /orders/{id}/status` endpoint accepted `{"status": "SCHEDULED"}` and could move a scheduled order straight to `PREPARING` or `CANCELLED`, skipping the 30-minute release rule. No test caught it, because no criterion covered it. |
| What I changed and why | Added AC11 to the requirements and a guard in `update_status()`: 409 `STATUS_CHANGE_NOT_ALLOWED` when the order is `SCHEDULED` or the target is `SCHEDULED`. Tests cover both directions. Mutation checks: removing either half of the guard was caught. pytest 75 passed. |
| Outcome | Slice 2's change rewritten; new criterion added. Commit `65da3a5`. |

### Entry 11

| Field | Entry |
|---|---|
| Entry # / date | 11 / Oct 30, 3:30 pm |
| Tool, model, mode | Claude Code, Opus 5.5, agent mode |
| Slice | Verification and documentation (README, this log) |
| Prompt (summarized) | Run the real app and exercise the feature; update the README with run, test, and demo steps; check that the suite passes from a fresh clone. |
| What the AI produced | A smoke run against uvicorn with the real clock, README updates, and a fresh-clone test run. |
| What I verified | Real server: schedule +1 h → 201 `SCHEDULED`; +10 min → 422 `SCHEDULE_TOO_SOON`; cancel → 200, cancel again → 409; `/docs` → 200. Starlette warns that `httpx` is deprecated for its test client; checked `httpx2` on PyPI but kept the pinned `httpx` (it is only a warning). |
| What I changed and why | Nothing. |
| Outcome | Accepted. |

### Entry 12

| Field | Entry |
|---|---|
| Entry # / date | 12 / Oct 30 |
| Tool, model, mode | Claude Code, Opus 5.5, chat |
| Slice | Reflection (written deliverable, not code) |
| Prompt (summarized) | Gave it my own reflection draft and asked for feedback, then for a revised sample that adds the missing Prompt 3 paragraph. |
| What the AI produced | Feedback on my draft (Prompt 3 missing, over 2 pages, several sentences inaccurate about who did what), then a revised version: tighter wording, accuracy fixes, and a drafted Prompt 3 paragraph built from facts in this log and the commit history. |
| What I verified | Checked each fact in the revision against this log and the commits. |
| What I changed and why | My own draft supplied the structure and content for prompts 1, 2, 4, and 5. The AI drafted the Prompt 3 paragraph and revised the wording of the rest; the final version is my edit of that. |
| Outcome | Used as the basis for the submitted reflection PDF. |
