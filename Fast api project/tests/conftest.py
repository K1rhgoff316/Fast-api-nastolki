"""Shared pytest fixtures."""

from collections.abc import Generator
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_board_games.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator:
    """Use a separate SQLite database for tests."""

    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database() -> Generator:
    """Recreate tables around each test."""

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return FastAPI test client."""

    with TestClient(app) as test_client:
        yield test_client


def register_and_login(client: TestClient, username: str, email: str) -> dict[str, str]:
    """Create a user and return bearer headers."""

    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": "secret123"},
    )
    response = client.post("/auth/login", data={"username": username, "password": "secret123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def headers(client: TestClient) -> dict[str, str]:
    """Auth headers for the default user."""

    return register_and_login(client, "alice", "alice@example.com")


@pytest.fixture
def second_user(client: TestClient) -> dict:
    """Create a second user."""

    response = client.post(
        "/auth/register",
        json={"username": "bob", "email": "bob@example.com", "password": "secret123"},
    )
    return response.json()
