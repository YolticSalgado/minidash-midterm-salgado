ORDER = {
    "restaurant_id": 1,
    "items": [{"menu_item_id": 1, "quantity": 2}, {"menu_item_id": 2, "quantity": 1}],
    "address": "1 Main St",
}


def test_place_order_computes_total_and_starts_placed(client):
    resp = client.post("/orders", json=ORDER)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "PLACED"
    assert body["total_cents"] == 2 * 1299 + 1499
    assert [i["menu_item_id"] for i in body["items"]] == [1, 2]


def test_place_order_rejects_item_from_another_restaurant(client):
    bad = {**ORDER, "items": [{"menu_item_id": 3, "quantity": 1}]}
    resp = client.post("/orders", json=bad)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "ITEM_NOT_ON_MENU"


def test_place_order_rejects_zero_quantity(client):
    bad = {**ORDER, "items": [{"menu_item_id": 1, "quantity": 0}]}
    assert client.post("/orders", json=bad).status_code == 422


def test_place_order_unknown_restaurant_is_404(client):
    resp = client.post("/orders", json={**ORDER, "restaurant_id": 999})
    assert resp.status_code == 404


def test_get_order_round_trips(client):
    created = client.post("/orders", json=ORDER).json()
    resp = client.get(f"/orders/{created['id']}")
    assert resp.status_code == 200
    assert resp.json() == created


def test_get_unknown_order_is_404(client):
    resp = client.get("/orders/999")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "ORDER_NOT_FOUND"


def test_patch_status_updates_order(client):
    order_id = client.post("/orders", json=ORDER).json()["id"]
    resp = client.patch(f"/orders/{order_id}/status", json={"status": "PREPARING"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "PREPARING"


def test_patch_status_rejects_unknown_status(client):
    order_id = client.post("/orders", json=ORDER).json()["id"]
    resp = client.patch(f"/orders/{order_id}/status", json={"status": "TELEPORTED"})
    assert resp.status_code == 422
