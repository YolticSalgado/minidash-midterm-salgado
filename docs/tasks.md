# Tasks — Track A: Scheduled Orders

Each slice is small enough to review in a few minutes and is merged on its own with a passing
suite. Test files are named after the slice; test names include the AC they prove.

- [x] **Slice 1 — Inject a clock** (AC12)
  Add `Clock` / `SystemClock`; `create_app(clock=...)`; `place_order` takes `now` instead of
  calling `datetime.now()`; add `to_db()` for UTC timestamps.
  *Verify:* `test_slice1_clock.py` — `created_at` equals the fixed clock's time; `to_db()` always
  produces the same fixed-width UTC format, including from a non-UTC offset.

- [x] **Slice 2 — Data model and migration** (AC1, AC2)
  `orders.scheduled_for TEXT NULL`, `SCHEDULED` status, idempotent `migrate()`.
  *Verify:* `test_slice2_migration.py` — an old-schema DB with an existing order gains the column,
  the old order reads back with `scheduled_for = NULL`, and migrating twice is safe.

- [x] **Slice 3 — Lead-time rule** (AC3, AC4, AC5)
  `validate_schedule()` lead-time and time-zone checks.
  *Verify:* `test_slice3_lead_time.py` — 44:59 / 45:00 / 46:00 minutes; 7 days and 7 days + 1 s;
  naive time rejected; non-UTC offset converted to UTC.

- [x] **Slice 4 — Opening-hours rule** (AC6)
  `is_open_at()` with `[open, close)`, overnight wrap, and 24-hour restaurants.
  *Verify:* `test_slice4_opening_hours.py` — table of boundary times for day, overnight, and 24 h
  hours.

- [ ] **Slice 5 — API: place a scheduled order** (AC1–AC6)
  `POST /orders` accepts `scheduled_for`; returns `SCHEDULED` or 422 with the right code.
  *Verify:* `test_slice5_api_schedule.py` — 201 `SCHEDULED`; each 422 code; nothing stored on
  rejection; unscheduled orders still `PLACED`.

- [ ] **Slice 6 — Release due orders exactly once** (AC7, AC8)
  `release_due_orders(conn, now)` with one atomic `UPDATE`.
  *Verify:* `test_slice6_release.py` — 30 min 1 s before: not released; exactly 30 min before:
  released; second run releases nothing; only due orders move.

- [ ] **Slice 7 — Background release loop** (AC7)
  `run_release_loop()` in `worker.py`, started and stopped by the FastAPI lifespan.
  *Verify:* `test_slice7_worker.py` — the loop calls release, survives an exception, and stops
  when signalled; the app releases a due order on startup with a fixed clock.

- [ ] **Slice 8 — Cancel and status guard** (AC9, AC10, AC11)
  `POST /orders/{id}/cancel`; `PATCH /status` refuses `SCHEDULED` orders and the `SCHEDULED` value.
  *Verify:* `test_slice8_cancel.py` — cancel `SCHEDULED` → `CANCELLED` and never released; cancel
  `PLACED` → 409 unchanged; unknown → 404; PATCH guard → 409.

## Traceability

| AC | Slice | Tests |
|---|---|---|
| AC1 | 2, 5 | `test_ac1_*` |
| AC2 | 2, 5 | `test_ac2_*` |
| AC3 | 3, 5 | `test_ac3_*` |
| AC4 | 3, 5 | `test_ac4_*` |
| AC5 | 3, 5 | `test_ac5_*` |
| AC6 | 4, 5 | `test_ac6_*` |
| AC7 | 6, 7 | `test_ac7_*` |
| AC8 | 6 | `test_ac8_*` |
| AC9 | 8 | `test_ac9_*` |
| AC10 | 8 | `test_ac10_*` |
| AC11 | 8 | `test_ac11_*` |
| AC12 | 1 | `test_ac12_*` |
