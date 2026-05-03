"""Authentication endpoint tests."""


def test_register_login_and_read_me(client):
    """A user can register, login, and call a protected endpoint."""

    register_response = client.post(
        "/auth/register",
        json={"username": "mike", "email": "mike@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={"username": "mike", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "mike"


def test_json_login_is_available_for_web_interface(client):
    """The friendly website can login with JSON instead of form data."""

    client.post(
        "/auth/register",
        json={"username": "site", "email": "site@example.com", "password": "password123"},
    )
    response = client.post(
        "/auth/login-json",
        json={"username": "site", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_users_list_requires_auth_and_returns_players(client):
    """The website can load players after login."""

    client.post(
        "/auth/register",
        json={"username": "site", "email": "site@example.com", "password": "password123"},
    )
    login_response = client.post(
        "/auth/login-json",
        json={"username": "site", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    anonymous_response = client.get("/users")
    users_response = client.get("/users", headers=headers)

    assert anonymous_response.status_code == 401
    assert users_response.status_code == 200
    assert users_response.json()[0]["username"] == "site"


def test_protected_endpoint_rejects_anonymous_user(client):
    """Protected endpoints require a bearer token."""

    response = client.get("/auth/me")
    assert response.status_code == 401


def test_duplicate_registration_is_rejected(client):
    """Duplicate usernames or emails are rejected."""

    payload = {"username": "mike", "email": "mike@example.com", "password": "password123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
