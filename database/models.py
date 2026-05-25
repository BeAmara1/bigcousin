from datetime import datetime, timezone
from sqlalchemy import (BigInteger, Column, DateTime, Float, ForeignKey,
                        Integer, JSON, String, Text, UniqueConstraint)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    discord_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    backlogs = relationship("Backlog", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} ({self.discord_id})>"


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    cover_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    genres = Column(JSON, nullable=True)
    platforms = Column(JSON, nullable=True)
    release_year = Column(Integer, nullable=True)
    community_rating = Column(Float, nullable=True)

    ratings = relationship("Rating", back_populates="game", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="game", cascade="all, delete-orphan")
    backlogs = relationship("Backlog", back_populates="game", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="game", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game {self.name}>"


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.discord_id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="ratings")
    game = relationship("Game", back_populates="ratings")

    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game_rating"),)

    def __repr__(self):
        return f"<Rating {self.user_id} -> {self.game_id}: {self.score}>"


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.discord_id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="reviews")
    game = relationship("Game", back_populates="reviews")

    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game_review"),)

    def __repr__(self):
        return f"<Review {self.user_id} -> {self.game_id}>"


class Backlog(Base):
    __tablename__ = "backlogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.discord_id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="backlogs")
    game = relationship("Game", back_populates="backlogs")

    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game_backlog"),)

    def __repr__(self):
        return f"<Backlog {self.user_id} -> {self.game_id}>"


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.discord_id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="favorites")
    game = relationship("Game", back_populates="favorites")

    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game_favorite"),)

    def __repr__(self):
        return f"<Favorite {self.user_id} -> {self.game_id}>"
