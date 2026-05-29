import logging

import discord
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import (AnalyticsEvent, Backlog, Favorite, Game, Rating,
                             Review, User, UserGame)
from services.game_service import get_user_games
from utils.errors import GameNotFoundError

logger = logging.getLogger("bigcousin.user_service")


async def get_or_create_user(session: AsyncSession, discord_user: discord.User) -> User:
    user = await session.get(User, discord_user.id)
    if user is None:
        user = User(
            discord_id=discord_user.id,
            username=discord_user.name,
            avatar_url=discord_user.display_avatar.url,
        )
        session.add(user)
        await session.commit()
        logger.info(f"Novo usuário criado: {discord_user.name} ({discord_user.id})")
    else:
        if user.username != discord_user.name or user.avatar_url != discord_user.display_avatar.url:
            user.username = discord_user.name
            user.avatar_url = discord_user.display_avatar.url
            await session.commit()
    return user


async def get_user(session: AsyncSession, discord_id: int) -> User | None:
    return await session.get(User, discord_id)


async def get_user_stats(session: AsyncSession, discord_id: int) -> dict:
    user = await session.get(User, discord_id)
    if not user:
        return {}

    user_games = await session.execute(
        select(UserGame).where(UserGame.user_id == discord_id)
    )
    user_game_ids = [ug.game_id for ug in user_games.scalars().all()]

    ratings = {}
    if user_game_ids:
        ratings_result = await session.execute(
            select(Rating).where(
                Rating.user_id == discord_id,
                Rating.game_id.in_(user_game_ids)
            )
        )
        for r in ratings_result.scalars().all():
            ratings[r.game_id] = r

    total_games = len(user_game_ids)
    beaten_count = len(ratings)
    avg_rating = (
        round(sum(r.score for r in ratings.values()) / len(ratings), 1)
        if ratings else 0.0
    )

    backlog_count = (await session.execute(
        select(func.count(Backlog.id)).where(Backlog.user_id == discord_id)
    )).scalar() or 0

    recent_query = (
        select(UserGame)
        .options(selectinload(UserGame.game))
        .where(UserGame.user_id == discord_id)
        .order_by(UserGame.added_at.desc())
        .limit(5)
    )
    recent_result = await session.execute(recent_query)
    recent_user_games = recent_result.scalars().all()
    recent_games = [(ug.game, ratings.get(ug.game_id)) for ug in recent_user_games if ug.game]

    fav_query = (
        select(Favorite)
        .options(selectinload(Favorite.game))
        .where(Favorite.user_id == discord_id)
        .limit(5)
    )
    fav_result = await session.execute(fav_query)
    favorites = fav_result.scalars().all()

    latest_review_query = (
        select(Review)
        .options(selectinload(Review.game))
        .where(Review.user_id == discord_id)
        .order_by(Review.created_at.desc())
        .limit(1)
    )
    latest_review_result = await session.execute(latest_review_query)
    latest_review = latest_review_result.scalar_one_or_none()

    return {
        "total_games": total_games,
        "avg_rating": avg_rating,
        "beaten_count": beaten_count,
        "backlog_count": backlog_count,
        "recent_games": recent_games,
        "favorites": favorites,
        "latest_review": latest_review,
    }


async def delete_user_data(session: AsyncSession, discord_id: int):
    for model_cls in (UserGame, Rating, Review, Backlog, Favorite, AnalyticsEvent):
        result = await session.execute(
            select(model_cls).where(model_cls.user_id == discord_id)  # type: ignore
        )
        for obj in result.scalars().all():
            await session.delete(obj)
    await session.commit()
