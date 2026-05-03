"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """Registered API user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    games: Mapped[list["BoardGame"]] = relationship(back_populates="owner")
    sessions: Mapped[list["GameSession"]] = relationship(back_populates="organizer")
    participations: Mapped[list["SessionParticipant"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(back_populates="author")


class BoardGame(Base):
    """Board game from the club catalog."""

    __tablename__ = "board_games"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    publisher: Mapped[str] = mapped_column(String(120), nullable=False)
    genre: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    min_players: Mapped[int] = mapped_column(Integer, nullable=False)
    max_players: Mapped[int] = mapped_column(Integer, nullable=False)
    play_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    complexity: Mapped[float] = mapped_column(Float, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    owner: Mapped[User] = relationship(back_populates="games")
    sessions: Mapped[list["GameSession"]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
    )


class GameSession(Base):
    """Planned or completed game meetup."""

    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("board_games.id"), nullable=False)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="planned", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    game: Mapped[BoardGame] = relationship(back_populates="sessions")
    organizer: Mapped[User] = relationship(back_populates="sessions")
    participants: Mapped[list["SessionParticipant"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class SessionParticipant(Base):
    """User result inside a game session."""

    __tablename__ = "session_participants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("game_sessions.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    session: Mapped[GameSession] = relationship(back_populates="participants")
    user: Mapped[User] = relationship(back_populates="participations")


class Review(Base):
    """User review for a board game."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("board_games.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    game: Mapped[BoardGame] = relationship(back_populates="reviews")
    author: Mapped[User] = relationship(back_populates="reviews")
