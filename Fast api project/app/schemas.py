"""Pydantic schemas for requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    """Payload for user registration."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "alice",
                "email": "alice@example.com",
                "password": "secret123",
            }
        }
    )


class UserPublic(BaseModel):
    """Public user data."""

    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Simple JSON login payload for the web interface."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "alice",
                "password": "secret123",
            }
        }
    )


class Token(BaseModel):
    """OAuth2 bearer token response."""

    access_token: str
    token_type: str = "bearer"


class BoardGameBase(BaseModel):
    """Common board game fields."""

    name: str = Field(min_length=2, max_length=120)
    publisher: str = Field(min_length=2, max_length=120)
    genre: str = Field(min_length=2, max_length=80)
    min_players: int = Field(ge=1, le=20)
    max_players: int = Field(ge=1, le=20)
    play_time_minutes: int = Field(ge=10, le=600)
    complexity: float = Field(ge=1.0, le=5.0)

    @model_validator(mode="after")
    def validate_player_range(self):
        """Ensure min_players is not greater than max_players."""

        if self.min_players > self.max_players:
            raise ValueError("min_players cannot be greater than max_players")
        return self


class BoardGameCreate(BoardGameBase):
    """Payload for creating a board game."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Catan",
                "publisher": "Kosmos",
                "genre": "Family",
                "min_players": 3,
                "max_players": 4,
                "play_time_minutes": 90,
                "complexity": 2.3,
            }
        }
    )


class BoardGameUpdate(BoardGameBase):
    """Payload for updating a board game."""


class BoardGamePublic(BoardGameBase):
    """Board game response."""

    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class ParticipantBase(BaseModel):
    """Common participant result fields."""

    user_id: int
    score: Optional[int] = Field(default=None, ge=0)
    is_winner: bool = False


class ParticipantCreate(ParticipantBase):
    """Payload for adding a participant."""


class ParticipantUpdate(BaseModel):
    """Payload for changing a participant result."""

    score: Optional[int] = Field(default=None, ge=0)
    is_winner: bool = False


class ParticipantPublic(ParticipantBase):
    """Participant response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class SessionBase(BaseModel):
    """Common game session fields."""

    title: str = Field(min_length=2, max_length=120)
    game_id: int
    scheduled_at: datetime
    status: str = Field(default="planned", pattern="^(planned|completed|cancelled)$")
    notes: Optional[str] = Field(default=None, max_length=1000)


class SessionCreate(SessionBase):
    """Payload for creating a session with optional participants."""

    participants: list[ParticipantCreate] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Friday game night",
                "game_id": 1,
                "scheduled_at": "2026-05-10T18:00:00",
                "status": "planned",
                "notes": "Beginner friendly table",
                "participants": [{"user_id": 1}, {"user_id": 2}],
            }
        }
    )


class SessionUpdate(BaseModel):
    """Payload for editing a session."""

    title: str = Field(min_length=2, max_length=120)
    scheduled_at: datetime
    status: str = Field(pattern="^(planned|completed|cancelled)$")
    notes: Optional[str] = Field(default=None, max_length=1000)


class SessionPublic(SessionBase):
    """Session response with participants."""

    id: int
    organizer_id: int
    participants: list[ParticipantPublic] = []

    model_config = ConfigDict(from_attributes=True)


class ReviewBase(BaseModel):
    """Common review fields."""

    game_id: int
    rating: int = Field(ge=1, le=10)
    comment: str = Field(min_length=5, max_length=1000)


class ReviewCreate(ReviewBase):
    """Payload for creating a review."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "game_id": 1,
                "rating": 9,
                "comment": "Easy to explain and fun for a mixed group.",
            }
        }
    )


class ReviewUpdate(BaseModel):
    """Payload for updating a review."""

    rating: int = Field(ge=1, le=10)
    comment: str = Field(min_length=5, max_length=1000)


class ReviewPublic(ReviewBase):
    """Review response."""

    id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)


class Recommendation(BaseModel):
    """Business recommendation response."""

    game_id: int
    game_name: str
    suitability_score: float
    reason: str


class PlayerStats(BaseModel):
    """Personal analytics response."""

    total_sessions: int
    won_sessions: int
    win_rate: float
    average_score: float
