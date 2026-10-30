# Requirements — Track A: Scheduled Orders

## User stories

- **US1 — Schedule.** As a customer, I want to order now for delivery later, so dinner arrives
  when I need it.
- **US2 — Cancel.** As a customer, I want to cancel a scheduled order before the restaurant starts
  on it, so I am not charged for food I no longer need.
- **US3 — Release.** As a restaurant, I want a scheduled order to reach my kitchen 30 minutes
  before its delivery time, exactly once, so I can prepare it on time and never cook it twice.

## Definitions

- **now** — the current time from the injected clock (never the real system clock in tests).
- **scheduled_for** — the requested delivery time, an ISO 8601 timestamp *with* a UTC offset
  (e.g. `2026-11-01T18:00:00Z`). It is stored and returned in UTC.
- **Open** — a restaurant is open at time *t* (UTC) when *t* is in `[opens_at, closes_at)`:
  opening time included, closing time excluded. If `closes_at < opens_at` the hours wrap past
  midnight (e.g. 18:00–02:00). If `opens_at == closes_at` the restaurant is open 24 hours.

## Acceptance criteria (EARS)

| ID | Criterion | Story |
|---|---|---|
| AC1 | WHEN a customer places an order without `scheduled_for`, THE SYSTEM SHALL create it with status `PLACED`, unchanged from the baseline. | US1 |
| AC2 | WHEN a customer places an order whose `scheduled_for` is at least 45 minutes and at most 7 days after now, at a time the restaurant is open, THE SYSTEM SHALL create it with status `SCHEDULED`, respond 201, and return `scheduled_for` in UTC. | US1 |
| AC3 | WHEN `scheduled_for` is less than 45 minutes after now, THE SYSTEM SHALL reject the order with 422 `SCHEDULE_TOO_SOON` and create nothing. | US1 |
| AC4 | WHEN `scheduled_for` is more than 7 days after now, THE SYSTEM SHALL reject the order with 422 `SCHEDULE_TOO_FAR` and create nothing. | US1 |
| AC5 | IF `scheduled_for` has no UTC offset, THEN THE SYSTEM SHALL reject the order with 422 `SCHEDULE_TIMEZONE_REQUIRED`. | US1 |
| AC6 | IF the restaurant is not open at `scheduled_for`, THEN THE SYSTEM SHALL reject the order with 422 `RESTAURANT_CLOSED`. | US1 |
| AC7 | WHEN now reaches 30 minutes before a `SCHEDULED` order's `scheduled_for`, THE SYSTEM SHALL change it from `SCHEDULED` to `PLACED` exactly once, even if the release check runs repeatedly. | US3 |
| AC8 | WHILE now is earlier than 30 minutes before `scheduled_for`, THE SYSTEM SHALL keep the order `SCHEDULED`. | US3 |
| AC9 | WHEN a customer cancels an order that is `SCHEDULED`, THE SYSTEM SHALL mark it `CANCELLED` and never release it. | US2 |
| AC10 | IF a customer cancels an order that is not `SCHEDULED`, THEN THE SYSTEM SHALL reject the request with 409 `ORDER_NOT_CANCELLABLE` and leave the order unchanged. | US2 |
| AC11 | IF the status-update endpoint is asked to change a `SCHEDULED` order, or to set status `SCHEDULED`, THEN THE SYSTEM SHALL reject the request with 409 `STATUS_CHANGE_NOT_ALLOWED`, so the release rule cannot be bypassed. | US3 |
| AC12 | THE SYSTEM SHALL obtain the current time only from an injected clock, so every time-dependent test is deterministic. | all |

Boundaries are inclusive where the assignment says "at least" / "at most": exactly 45 minutes and
exactly 7 days are accepted; 44 minutes 59 seconds and 7 days + 1 second are rejected. The release
fires at exactly `scheduled_for − 30 min`, not one tick later.

## Out of scope

- Per-restaurant time zones and daylight-saving time (all hours are UTC).
- Days of the week / holiday closures (hours are the same every day).
- Changing the time or items of a scheduled order after it is placed.
- Checking that the restaurant is open at release time (only the delivery time is checked).
- Authentication — who is allowed to cancel whose order.
- Notifications to customers or restaurants.
- Running several app instances at once (one instance runs the release loop).
- Opening-hours checks for immediate (non-scheduled) orders — baseline behavior is kept.
- A front-end page.
