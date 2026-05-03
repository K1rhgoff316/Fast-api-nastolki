"""FastAPI application for a board game club."""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.database import Base, engine, get_db
from app.models import BoardGame, GameSession, Review, SessionParticipant, User
from app.schemas import (
    BoardGameCreate,
    BoardGamePublic,
    BoardGameUpdate,
    LoginRequest,
    ParticipantCreate,
    ParticipantPublic,
    ParticipantUpdate,
    PlayerStats,
    Recommendation,
    ReviewCreate,
    ReviewPublic,
    ReviewUpdate,
    SessionCreate,
    SessionPublic,
    SessionUpdate,
    Token,
    UserCreate,
    UserPublic,
)
from app.security import create_access_token, decode_access_token, hash_password, verify_password
from app.site import HOME_HTML

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
DEMO_TAG = "0. Быстрый старт"
AUTH_TAG = "1. Вход и регистрация"
GAMES_TAG = "2. Игры"
SESSIONS_TAG = "3. Игровые встречи"
REVIEWS_TAG = "4. Отзывы"
ANALYTICS_TAG = "5. Подбор и статистика"

TAGS_METADATA = [
    {
        "name": DEMO_TAG,
        "description": "Одна кнопка для демо: пользователь, игра, встреча и отзыв.",
    },
    {
        "name": AUTH_TAG,
        "description": "Обычный JSON-вход для сайта и OAuth2-вход для Swagger.",
    },
    {
        "name": GAMES_TAG,
        "description": "Каталог настольных игр: создать, посмотреть, изменить или удалить игру.",
    },
    {
        "name": SESSIONS_TAG,
        "description": "Игровые встречи: кто играет, когда встреча и кто победил.",
    },
    {
        "name": REVIEWS_TAG,
        "description": "Оценки и комментарии к играм.",
    },
    {
        "name": ANALYTICS_TAG,
        "description": "Готовая бизнес-логика: статистика игрока и подбор подходящих игр.",
    },
]

POPULAR_GAMES = [
    {
        "name": "Azul",
        "publisher": "Next Move Games",
        "genre": "Abstract",
        "min_players": 2,
        "max_players": 4,
        "play_time_minutes": 45,
        "complexity": 1.8,
    },
    {
        "name": "Ticket to Ride",
        "publisher": "Days of Wonder",
        "genre": "Family",
        "min_players": 2,
        "max_players": 5,
        "play_time_minutes": 60,
        "complexity": 1.9,
    },
    {
        "name": "Carcassonne",
        "publisher": "Hans im Glueck",
        "genre": "Tile Placement",
        "min_players": 2,
        "max_players": 5,
        "play_time_minutes": 45,
        "complexity": 1.9,
    },
    {
        "name": "Dixit",
        "publisher": "Libellud",
        "genre": "Party",
        "min_players": 3,
        "max_players": 8,
        "play_time_minutes": 30,
        "complexity": 1.2,
    },
    {
        "name": "Codenames",
        "publisher": "Czech Games Edition",
        "genre": "Party",
        "min_players": 2,
        "max_players": 8,
        "play_time_minutes": 20,
        "complexity": 1.3,
    },
    {
        "name": "Pandemic",
        "publisher": "Z-Man Games",
        "genre": "Cooperative",
        "min_players": 2,
        "max_players": 4,
        "play_time_minutes": 45,
        "complexity": 2.4,
    },
    {
        "name": "7 Wonders",
        "publisher": "Repos Production",
        "genre": "Strategy",
        "min_players": 3,
        "max_players": 7,
        "play_time_minutes": 30,
        "complexity": 2.3,
    },
]


@asynccontextmanager
async def lifespan(_application: FastAPI):
    """Create SQLite database tables automatically on startup."""

    Base.metadata.create_all(bind=engine)
    with Session(engine) as database:
        user = get_or_create_user(database, "demo", "demo@example.com", "secret123")
        get_or_create_popular_games(database, user)
    yield

app = FastAPI(
    title="Клуб настольных игр",
    description=(
        "Простой REST API: зарегистрируйтесь, добавьте игру, "
        "создайте встречу и получите рекомендацию."
    ),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Return authenticated user from bearer token."""

    username = decode_access_token(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


def get_game_or_404(db: Session, game_id: int) -> BoardGame:
    """Return a game or raise a 404 response."""

    game = db.get(BoardGame, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


def get_session_or_404(db: Session, session_id: int) -> GameSession:
    """Return a session or raise a 404 response."""

    session = db.get(GameSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def validate_session_rules(
    db: Session,
    game: BoardGame,
    status_value: str,
    participants: list[ParticipantCreate],
) -> None:
    """Check player limits and result rules before writing a session."""

    user_ids = {participant.user_id for participant in participants}
    if len(user_ids) != len(participants):
        raise HTTPException(status_code=400, detail="Duplicate participants are not allowed")

    if len(participants) < game.min_players or len(participants) > game.max_players:
        raise HTTPException(status_code=400, detail="Participant count does not match game limits")

    existing_users = db.query(User).filter(User.id.in_(user_ids)).count()
    if existing_users != len(user_ids):
        raise HTTPException(status_code=404, detail="One or more participants not found")

    has_results = any(item.score is not None or item.is_winner for item in participants)
    if status_value == "planned" and has_results:
        raise HTTPException(status_code=400, detail="Planned sessions cannot contain results")
    if status_value == "completed" and not any(item.is_winner for item in participants):
        raise HTTPException(status_code=400, detail="Completed sessions require a winner")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root() -> HTMLResponse:
    """Return the friendly web interface."""

    return HTMLResponse(HOME_HTML)


@app.post(
    "/auth/register",
    response_model=UserPublic,
    status_code=201,
    tags=[AUTH_TAG],
    summary="Создать пользователя",
)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    """Register a new user."""

    same_username = db.query(User).filter(User.username == payload.username).first()
    same_email = db.query(User).filter(User.email == payload.email).first()
    if same_username or same_email:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token, tags=[AUTH_TAG], summary="Войти и получить токен")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate a user and return a JWT token."""

    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return Token(access_token=create_access_token(user.username))


@app.post("/auth/login-json", response_model=Token, tags=[AUTH_TAG], summary="Войти через JSON")
def login_user_json(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate a user with a simple JSON payload."""

    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return Token(access_token=create_access_token(user.username))


@app.get("/auth/me", response_model=UserPublic, tags=[AUTH_TAG], summary="Проверить мой токен")
def read_me(current_user: User = Depends(get_current_user)) -> User:
    """Return current authenticated user."""

    return current_user


@app.get("/users", response_model=list[UserPublic], tags=[AUTH_TAG], summary="Список игроков")
def list_users(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[User]:
    """List users for participant selectors in the web interface."""

    return db.query(User).order_by(User.username).all()


def get_or_create_user(db: Session, username: str, email: str, password: str) -> User:
    """Return an existing demo user or create it."""

    user = db.query(User).filter(User.username == username).first()
    if user is not None:
        return user

    user = User(username=username, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_demo_game(db: Session, owner: User) -> BoardGame:
    """Return the demo game or create it."""

    game = (
        db.query(BoardGame)
        .filter(BoardGame.name == "Catan Demo", BoardGame.owner_id == owner.id)
        .first()
    )
    if game is not None:
        return game

    game = BoardGame(
        name="Catan Demo",
        publisher="Kosmos",
        genre="Family",
        min_players=2,
        max_players=4,
        play_time_minutes=90,
        complexity=2.3,
        owner_id=owner.id,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def get_or_create_popular_games(db: Session, owner: User) -> list[BoardGame]:
    """Create popular games for quick selection in the interface."""

    games = []
    for payload in POPULAR_GAMES:
        game = (
            db.query(BoardGame)
            .filter(BoardGame.name == payload["name"], BoardGame.owner_id == owner.id)
            .first()
        )
        if game is None:
            game = BoardGame(**payload, owner_id=owner.id)
            db.add(game)
            db.commit()
            db.refresh(game)
        games.append(game)
    return games


@app.post("/demo/popular-games", tags=[DEMO_TAG], summary="Добавить популярные игры")
def seed_popular_games(db: Session = Depends(get_db)) -> dict[str, object]:
    """Create several well-known games and return them for the web interface."""

    user = get_or_create_user(db, "demo", "demo@example.com", "secret123")
    games = get_or_create_popular_games(db, user)
    return {
        "access_token": create_access_token(user.username),
        "user": UserPublic.model_validate(user),
        "games": [BoardGamePublic.model_validate(game) for game in games],
    }


@app.post("/demo/seed", tags=[DEMO_TAG], summary="Создать демо-данные")
def seed_demo(db: Session = Depends(get_db)) -> dict[str, object]:
    """Create ready-to-use demo data and return a token."""

    user = get_or_create_user(db, "demo", "demo@example.com", "secret123")
    friend = get_or_create_user(db, "friend", "friend@example.com", "secret123")
    game = get_or_create_demo_game(db, user)
    popular_games = get_or_create_popular_games(db, user)

    session = (
        db.query(GameSession)
        .filter(GameSession.title == "Demo game night", GameSession.game_id == game.id)
        .first()
    )
    if session is None:
        session = GameSession(
            title="Demo game night",
            game_id=game.id,
            organizer_id=user.id,
            scheduled_at=datetime.utcnow() + timedelta(days=1),
            status="planned",
            notes="Ready-made demo session",
        )
        db.add(session)
        db.flush()
        db.add(SessionParticipant(session_id=session.id, user_id=user.id))
        db.add(SessionParticipant(session_id=session.id, user_id=friend.id))
        db.commit()
        db.refresh(session)

    review = (
        db.query(Review)
        .filter(Review.game_id == game.id, Review.author_id == user.id)
        .first()
    )
    if review is None:
        review = Review(
            game_id=game.id,
            author_id=user.id,
            rating=9,
            comment="Easy to explain and fun for a mixed group.",
        )
        db.add(review)
        db.commit()
        db.refresh(review)

    return {
        "access_token": create_access_token(user.username),
        "user": UserPublic.model_validate(user),
        "participants": [UserPublic.model_validate(user), UserPublic.model_validate(friend)],
        "game": BoardGamePublic.model_validate(game),
        "popular_games": [BoardGamePublic.model_validate(game_item) for game_item in popular_games],
        "session": SessionPublic.model_validate(session),
        "review": ReviewPublic.model_validate(review),
    }


@app.post(
    "/games",
    response_model=BoardGamePublic,
    status_code=201,
    tags=[GAMES_TAG],
    summary="Добавить игру",
)
def create_game(
    payload: BoardGameCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BoardGame:
    """Create a board game owned by the current user."""

    game = BoardGame(**payload.model_dump(), owner_id=current_user.id)
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@app.get("/games", response_model=list[BoardGamePublic], tags=[GAMES_TAG], summary="Список игр")
def list_games(
    genre: Optional[str] = Query(default=None, description="Фильтр по жанру, например Family"),
    players: Optional[int] = Query(
        default=None,
        ge=1,
        le=20,
        description="Сколько человек будет играть",
    ),
    db: Session = Depends(get_db),
) -> list[BoardGame]:
    """List games with optional filters."""

    query = db.query(BoardGame)
    if genre:
        query = query.filter(BoardGame.genre.ilike(f"%{genre}%"))
    if players:
        query = query.filter(BoardGame.min_players <= players, BoardGame.max_players >= players)
    return query.order_by(BoardGame.name).all()


@app.get("/games/{game_id}", response_model=BoardGamePublic, tags=[GAMES_TAG], summary="Одна игра")
def read_game(game_id: int, db: Session = Depends(get_db)) -> BoardGame:
    """Read one board game."""

    return get_game_or_404(db, game_id)


@app.put(
    "/games/{game_id}",
    response_model=BoardGamePublic,
    tags=[GAMES_TAG],
    summary="Изменить игру",
)
def update_game(
    game_id: int,
    payload: BoardGameUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BoardGame:
    """Update a board game owned by the current user."""

    game = get_game_or_404(db, game_id)
    if game.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can update this game")

    for field_name, value in payload.model_dump().items():
        setattr(game, field_name, value)
    db.commit()
    db.refresh(game)
    return game


@app.delete("/games/{game_id}", status_code=204, tags=[GAMES_TAG], summary="Удалить игру")
def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a board game owned by the current user."""

    game = get_game_or_404(db, game_id)
    if game.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete this game")
    db.delete(game)
    db.commit()


@app.post(
    "/sessions",
    response_model=SessionPublic,
    status_code=201,
    tags=[SESSIONS_TAG],
    summary="Создать игровую встречу",
)
def create_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameSession:
    """Create a session and attach participants."""

    game = get_game_or_404(db, payload.game_id)
    participants = list(payload.participants)
    if current_user.id not in {participant.user_id for participant in participants}:
        participants.append(ParticipantCreate(user_id=current_user.id))

    validate_session_rules(db, game, payload.status, participants)
    session = GameSession(
        title=payload.title,
        game_id=payload.game_id,
        organizer_id=current_user.id,
        scheduled_at=payload.scheduled_at,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(session)
    db.flush()
    for participant in participants:
        db.add(SessionParticipant(session_id=session.id, **participant.model_dump()))
    db.commit()
    db.refresh(session)
    return session


@app.get(
    "/sessions",
    response_model=list[SessionPublic],
    tags=[SESSIONS_TAG],
    summary="Список встреч",
)
def list_sessions(db: Session = Depends(get_db)) -> list[GameSession]:
    """List all game sessions."""

    return db.query(GameSession).order_by(GameSession.scheduled_at).all()


@app.get(
    "/sessions/{session_id}",
    response_model=SessionPublic,
    tags=[SESSIONS_TAG],
    summary="Одна встреча",
)
def read_session(session_id: int, db: Session = Depends(get_db)) -> GameSession:
    """Read one game session."""

    return get_session_or_404(db, session_id)


@app.put(
    "/sessions/{session_id}",
    response_model=SessionPublic,
    tags=[SESSIONS_TAG],
    summary="Изменить встречу",
)
def update_session(
    session_id: int,
    payload: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameSession:
    """Update session metadata."""

    session = get_session_or_404(db, session_id)
    if session.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can update this session")

    session.title = payload.title
    session.scheduled_at = payload.scheduled_at
    session.status = payload.status
    session.notes = payload.notes
    db.commit()
    db.refresh(session)
    return session


@app.delete(
    "/sessions/{session_id}",
    status_code=204,
    tags=[SESSIONS_TAG],
    summary="Удалить встречу",
)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a session organized by the current user."""

    session = get_session_or_404(db, session_id)
    if session.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can delete this session")
    db.delete(session)
    db.commit()


@app.post(
    "/sessions/{session_id}/participants",
    response_model=ParticipantPublic,
    status_code=201,
    tags=[SESSIONS_TAG],
    summary="Добавить участника",
)
def add_participant(
    session_id: int,
    payload: ParticipantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionParticipant:
    """Add a participant to a planned session."""

    session = get_session_or_404(db, session_id)
    if session.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can add participants")
    if session.status != "planned":
        raise HTTPException(
            status_code=400,
            detail="Participants can be added only to planned sessions",
        )
    if db.get(User, payload.user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")

    current_count = len(session.participants)
    if current_count + 1 > session.game.max_players:
        raise HTTPException(status_code=400, detail="Game player limit exceeded")
    duplicate = any(participant.user_id == payload.user_id for participant in session.participants)
    if duplicate:
        raise HTTPException(status_code=400, detail="User is already in session")

    participant = SessionParticipant(session_id=session_id, **payload.model_dump())
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


@app.put(
    "/sessions/{session_id}/participants/{user_id}",
    response_model=ParticipantPublic,
    tags=[SESSIONS_TAG],
    summary="Записать результат участника",
)
def update_participant(
    session_id: int,
    user_id: int,
    payload: ParticipantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionParticipant:
    """Update participant score and winner flag."""

    session = get_session_or_404(db, session_id)
    if session.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can update participants")

    participant = (
        db.query(SessionParticipant)
        .filter(SessionParticipant.session_id == session_id, SessionParticipant.user_id == user_id)
        .first()
    )
    if participant is None:
        raise HTTPException(status_code=404, detail="Participant not found")

    participant.score = payload.score
    participant.is_winner = payload.is_winner
    db.commit()
    db.refresh(participant)
    return participant


@app.delete(
    "/sessions/{session_id}/participants/{user_id}",
    status_code=204,
    tags=[SESSIONS_TAG],
    summary="Удалить участника",
)
def remove_participant(
    session_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove a participant from a session."""

    session = get_session_or_404(db, session_id)
    if session.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can remove participants")
    participant = (
        db.query(SessionParticipant)
        .filter(SessionParticipant.session_id == session_id, SessionParticipant.user_id == user_id)
        .first()
    )
    if participant is None:
        raise HTTPException(status_code=404, detail="Participant not found")
    db.delete(participant)
    db.commit()


@app.post(
    "/reviews",
    response_model=ReviewPublic,
    status_code=201,
    tags=[REVIEWS_TAG],
    summary="Оставить отзыв",
)
def create_review(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Review:
    """Create a game review."""

    get_game_or_404(db, payload.game_id)
    review = Review(**payload.model_dump(), author_id=current_user.id)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@app.get(
    "/reviews",
    response_model=list[ReviewPublic],
    tags=[REVIEWS_TAG],
    summary="Список отзывов",
)
def list_reviews(game_id: Optional[int] = None, db: Session = Depends(get_db)) -> list[Review]:
    """List reviews, optionally filtered by game."""

    query = db.query(Review)
    if game_id is not None:
        query = query.filter(Review.game_id == game_id)
    return query.order_by(Review.id).all()


@app.get(
    "/reviews/{review_id}",
    response_model=ReviewPublic,
    tags=[REVIEWS_TAG],
    summary="Один отзыв",
)
def read_review(review_id: int, db: Session = Depends(get_db)) -> Review:
    """Read one review."""

    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@app.put(
    "/reviews/{review_id}",
    response_model=ReviewPublic,
    tags=[REVIEWS_TAG],
    summary="Изменить отзыв",
)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Review:
    """Update review written by the current user."""

    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only author can update this review")

    review.rating = payload.rating
    review.comment = payload.comment
    db.commit()
    db.refresh(review)
    return review


@app.delete(
    "/reviews/{review_id}",
    status_code=204,
    tags=[REVIEWS_TAG],
    summary="Удалить отзыв",
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete review written by the current user."""

    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only author can delete this review")
    db.delete(review)
    db.commit()


@app.get(
    "/analytics/me",
    response_model=PlayerStats,
    tags=[ANALYTICS_TAG],
    summary="Моя статистика",
)
def personal_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlayerStats:
    """Calculate personal statistics for the current player."""

    participations = (
        db.query(SessionParticipant)
        .join(GameSession)
        .filter(SessionParticipant.user_id == current_user.id, GameSession.status == "completed")
        .all()
    )
    total_sessions = len(participations)
    won_sessions = sum(item.is_winner for item in participations)
    scores = [item.score for item in participations if item.score is not None]
    average_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    win_rate = round(won_sessions / total_sessions * 100, 2) if total_sessions else 0.0
    return PlayerStats(
        total_sessions=total_sessions,
        won_sessions=won_sessions,
        win_rate=win_rate,
        average_score=average_score,
    )


@app.get(
    "/analytics/recommendations",
    response_model=list[Recommendation],
    tags=[ANALYTICS_TAG],
    summary="Подобрать игру",
)
def recommend_games(
    players: int = Query(ge=1, le=20, description="Сколько человек будет играть"),
    max_duration: Optional[int] = Query(
        default=None,
        ge=10,
        le=600,
        description="Максимальная длительность партии в минутах",
    ),
    max_complexity: Optional[float] = Query(
        default=None,
        ge=1.0,
        le=5.0,
        description="Максимальная сложность игры от 1 до 5",
    ),
    db: Session = Depends(get_db),
) -> list[Recommendation]:
    """Recommend games using a weighted suitability algorithm."""

    query = db.query(BoardGame).filter(
        BoardGame.min_players <= players,
        BoardGame.max_players >= players,
    )
    if max_duration is not None:
        query = query.filter(BoardGame.play_time_minutes <= max_duration)
    if max_complexity is not None:
        query = query.filter(BoardGame.complexity <= max_complexity)

    recommendations = []
    for game in query.all():
        midpoint = (game.min_players + game.max_players) / 2
        player_score = max(0.0, 10 - abs(midpoint - players) * 2)
        duration_score = 10.0
        if max_duration is not None:
            duration_score = max(0.0, 10 - abs(max_duration - game.play_time_minutes) / 15)
        complexity_score = max(0.0, 10 - (game.complexity - 1) * 2)
        rating = db.query(func.avg(Review.rating)).filter(Review.game_id == game.id).scalar() or 7
        score = round(
            player_score * 0.35
            + duration_score * 0.25
            + complexity_score * 0.2
            + rating * 0.2,
            2,
        )
        recommendations.append(
            Recommendation(
                game_id=game.id,
                game_name=game.name,
                suitability_score=score,
                reason=(
                    f"{game.min_players}-{game.max_players} игроков, "
                    f"{game.play_time_minutes} минут, сложность {game.complexity}"
                ),
            )
        )

    return sorted(recommendations, key=lambda item: item.suitability_score, reverse=True)[:5]
