"""Session, review, and analytics tests."""

from datetime import datetime, timedelta


def create_game(client, headers, name="Catan"):
    """Create a game through the API and return its id."""

    response = client.post(
        "/games",
        headers=headers,
        json={
            "name": name,
            "publisher": "Kosmos",
            "genre": "Family",
            "min_players": 2,
            "max_players": 4,
            "play_time_minutes": 90,
            "complexity": 2.3,
        },
    )
    return response.json()["id"]


def test_session_participant_and_stats_flow(client, headers, second_user):
    """Completed sessions store participant results and power player stats."""

    game_id = create_game(client, headers)
    scheduled_at = (datetime.utcnow() + timedelta(days=1)).isoformat()
    session_response = client.post(
        "/sessions",
        headers=headers,
        json={
            "title": "Friday game night",
            "game_id": game_id,
            "scheduled_at": scheduled_at,
            "status": "completed",
            "participants": [
                {"user_id": 1, "score": 10, "is_winner": True},
                {"user_id": second_user["id"], "score": 7, "is_winner": False},
            ],
        },
    )
    assert session_response.status_code == 201
    assert len(session_response.json()["participants"]) == 2

    stats_response = client.get("/analytics/me", headers=headers)
    assert stats_response.status_code == 200
    assert stats_response.json()["win_rate"] == 100.0


def test_planned_session_rejects_scores(client, headers, second_user):
    """Business rule forbids results before a session is completed."""

    game_id = create_game(client, headers)
    response = client.post(
        "/sessions",
        headers=headers,
        json={
            "title": "Future game night",
            "game_id": game_id,
            "scheduled_at": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "status": "planned",
            "participants": [
                {"user_id": 1, "score": 10, "is_winner": False},
                {"user_id": second_user["id"], "score": None, "is_winner": False},
            ],
        },
    )
    assert response.status_code == 400


def test_add_update_remove_participant(client, headers, second_user):
    """Participant CRUD works for planned sessions."""

    game_id = create_game(client, headers)
    third_user = client.post(
        "/auth/register",
        json={"username": "carol", "email": "carol@example.com", "password": "secret123"},
    ).json()
    session_response = client.post(
        "/sessions",
        headers=headers,
        json={
            "title": "Weekend game",
            "game_id": game_id,
            "scheduled_at": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            "status": "planned",
            "participants": [{"user_id": 1}, {"user_id": second_user["id"]}],
        },
    )
    session_id = session_response.json()["id"]

    add_response = client.post(
        f"/sessions/{session_id}/participants",
        headers=headers,
        json={"user_id": third_user["id"]},
    )
    assert add_response.status_code == 201

    update_response = client.put(
        f"/sessions/{session_id}/participants/{third_user['id']}",
        headers=headers,
        json={"score": 8, "is_winner": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["score"] == 8

    delete_response = client.delete(
        f"/sessions/{session_id}/participants/{third_user['id']}",
        headers=headers,
    )
    assert delete_response.status_code == 204


def test_review_crud_and_recommendations(client, headers):
    """Reviews affect the recommendation endpoint's weighted score."""

    game_id = create_game(client, headers, "Azul")
    review_response = client.post(
        "/reviews",
        headers=headers,
        json={"game_id": game_id, "rating": 9, "comment": "Elegant and tactical puzzle."},
    )
    assert review_response.status_code == 201
    review_id = review_response.json()["id"]

    update_response = client.put(
        f"/reviews/{review_id}",
        headers=headers,
        json={"rating": 10, "comment": "Still excellent after many plays."},
    )
    assert update_response.status_code == 200

    recommendation_response = client.get(
        "/analytics/recommendations",
        params={"players": 2, "max_duration": 120, "max_complexity": 3},
    )
    assert recommendation_response.status_code == 200
    assert recommendation_response.json()[0]["game_name"] == "Azul"

    delete_response = client.delete(f"/reviews/{review_id}", headers=headers)
    assert delete_response.status_code == 204


def test_demo_seed_creates_ready_to_use_data(client):
    """One demo endpoint should prepare data for the simple web interface."""

    response = client.post("/demo/seed")
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["user"]["username"] == "demo"
    assert data["game"]["name"] == "Catan Demo"
    assert len(data["popular_games"]) >= 7
    assert len(data["participants"]) == 2


def test_popular_games_seed_adds_selectable_catalog_items(client):
    """Popular games endpoint should create several ready-to-pick games."""

    response = client.post("/demo/popular-games")
    assert response.status_code == 200
    data = response.json()
    game_names = {game["name"] for game in data["games"]}

    assert data["access_token"]
    assert {"Azul", "Ticket to Ride", "Codenames"}.issubset(game_names)


def test_home_page_is_human_interface(client):
    """Root page should be an HTML interface, not raw JSON."""

    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Клуб настольных игр" in response.text
