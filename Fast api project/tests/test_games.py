"""Board game CRUD tests."""


def game_payload(name="Catan"):
    """Return a valid game payload."""

    return {
        "name": name,
        "publisher": "Kosmos",
        "genre": "Family",
        "min_players": 3,
        "max_players": 4,
        "play_time_minutes": 90,
        "complexity": 2.3,
    }


def test_game_crud_flow(client, headers):
    """Games can be created, listed, updated, read, and deleted."""

    create_response = client.post("/games", headers=headers, json=game_payload())
    assert create_response.status_code == 201
    game_id = create_response.json()["id"]

    list_response = client.get("/games", params={"players": 3, "genre": "fam"})
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    updated = game_payload("Catan Deluxe")
    update_response = client.put(f"/games/{game_id}", headers=headers, json=updated)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Catan Deluxe"

    read_response = client.get(f"/games/{game_id}")
    assert read_response.status_code == 200

    delete_response = client.delete(f"/games/{game_id}", headers=headers)
    assert delete_response.status_code == 204
    assert client.get(f"/games/{game_id}").status_code == 404


def test_game_validation_rejects_invalid_player_range(client, headers):
    """Schema validation blocks games with impossible player range."""

    payload = game_payload()
    payload["min_players"] = 5
    payload["max_players"] = 2
    response = client.post("/games", headers=headers, json=payload)
    assert response.status_code == 422


def test_only_owner_can_update_game(client, headers, second_user):
    """Users cannot update games owned by someone else."""

    create_response = client.post("/games", headers=headers, json=game_payload())
    game_id = create_response.json()["id"]
    assert second_user["username"] == "bob"

    login_response = client.post("/auth/login", data={"username": "bob", "password": "secret123"})
    bob_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    response = client.put(f"/games/{game_id}", headers=bob_headers, json=game_payload("Other"))
    assert response.status_code == 403
