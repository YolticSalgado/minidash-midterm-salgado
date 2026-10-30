import pytest

# The client's clock is Monday 2026-11-02 12:00 UTC; Bella Napoli (id 1) is open 11:00-22:00 UTC.
ORDER = {"restaurant_id": 1, "items": [{"menu_item_id": 1, "quantity": 2}], "address": "1 Main St"}


def place(client, scheduled_for):
    return client.post("/orders", json={**ORDER, "scheduled_for": scheduled_for})


def test_ac2_valid_time_creates_scheduled_order(client):
    resp = place(client, "2026-11-02T18:00:00Z")
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "SCHEDULED"
    assert body["scheduled_for"] == "2026-11-02T18:00:00.000000+00:00"
    assert body["total_cents"] == 2 * 1299
    assert client.get(f"/orders/{body['id']}").json() == body


def test_ac2_offset_input_is_stored_and_returned_in_utc(client):
    body = place(client, "2026-11-02T13:00:00-05:00").json()
    assert body["scheduled_for"] == "2026-11-02T18:00:00.000000+00:00"


@pytest.mark.parametrize(
    "scheduled_for, code",
    [
        ("2026-11-02T12:44:59Z", "SCHEDULE_TOO_SOON"),  # AC3
        ("2026-11-09T12:00:01Z", "SCHEDULE_TOO_FAR"),  # AC4
        ("2026-11-02T18:00:00", "SCHEDULE_TIMEZONE_REQUIRED"),  # AC5
        ("2026-11-02T22:00:00Z", "RESTAURANT_CLOSED"),  # AC6
    ],
)
def test_ac3_to_ac6_invalid_time_is_rejected_and_nothing_is_stored(client, scheduled_for, code):
    resp = place(client, scheduled_for)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == code
    assert client.get("/orders/1").status_code == 404


def test_ac1_null_scheduled_for_places_order_now(client):
    body = place(client, None).json()
    assert body["status"] == "PLACED"
    assert body["scheduled_for"] is None


def test_unparseable_time_is_a_request_validation_error(client):
    assert place(client, "tomorrow at six").status_code == 422
