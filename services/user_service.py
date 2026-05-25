import logging

import discord
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Favorite, Game, Rating, Review, User
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

    total_games_query = select(func.count(Rating.game_id.distinct())).where(Rating.user_id == discord_id)
    total_games_result = await session.execute(total_games_query)
    total_games = total_games_result.scalar() or 0

    avg_rating_query = select(func.avg(Rating.score)).where(Rating.user_id == discord_id)
    avg_rating_result = await session.execute(avg_rating_query)
    avg_rating = avg_rating_result.scalar() or 0.0

    from database.models import Backlog
    backlog_count_query = select(func.count(Backlog.id)).where(Backlog.user_id == discord_id)
    backlog_count_result = await session.execute(backlog_count_query)
    backlog_count = backlog_count_result.scalar() or 0

    recent_query = (
        select(Rating)
        .options(selectinload(Rating.game))
        .where(Rating.user_id == discord_id)
        .order_by(Rating.updated_at.desc())
        .limit(5)
    )
    recent_result = await session.execute(recent_query)
    recent_ratings = recent_result.scalars().all()
    recent_games = [(r.game, r) for r in recent_ratings]

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
        "avg_rating": round(avg_rating, 1) if avg_rating else 0.0,
        "beaten_count": total_games,
        "backlog_count": backlog_count,
        "recent_games": recent_games,
        "favorites": favorites,
        "latest_review": latest_review,
    }
