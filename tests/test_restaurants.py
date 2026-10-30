def test_list_restaurants_returns_five_seeded(client):
    resp = client.get("/restaurants")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 5
    assert body[0] == {
        "id": 1,
        "name": "Bella Napoli",
        "cuisine": "Italian",
        "opens_at": "11:00",
        "closes_at": "22:00",
        "avg_prep_minutes": 20,
    }


def test_menu_lists_only_that_restaurants_items(client):
    resp = client.get("/restaurants/2/menu")
    assert resp.status_code == 200
    assert resp.json() == [
        {"id": 3, "name": "Salmon Bento", "price_cents": 1399},
        {"id": 4, "name": "Miso Soup", "price_cents": 399},
    ]


def test_menu_for_unknown_restaurant_is_404(client):
    resp = client.get("/restaurants/999/menu")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "RESTAURANT_NOT_FOUND"
