import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Game, Rating
from utils.errors import GameNotFoundError, NotInLibraryError

logger = logging.getLogger("bigcousin.rating_service")


async def set_rating(session: AsyncSession, discord_id: int, game_id: int, score: int) -> Rating:
    game = await session.get(Game, game_id)
    if not game:
        raise GameNotFoundError(f"Jogo {game_id} não encontrado no catálogo")

    existing_rating = await session.execute(
        select(Rating).where(Rating.user_id == discord_id, Rating.game_id == game_id)
    )
    rating = existing_rating.scalar_one_or_none()

    if rating is None:
        raise NotInLibraryError("Adicione o jogo à sua biblioteca primeiro com /addgame")

    rating.score = score
    await session.commit()
    logger.info(f"Rating atualizado: {discord_id} -> {game.name}: {score}/10")
    return rating


async def get_rating(session: AsyncSession, discord_id: int, game_id: int) -> Rating | None:
    result = await session.execute(
        select(Rating).where(Rating.user_id == discord_id, Rating.game_id == game_id)
    )
    return result.scalar_one_or_none()


async def get_user_ratings(session: AsyncSession, discord_id: int) -> list[Rating]:
    result = await session.execute(
        select(Rating).where(Rating.user_id == discord_id).order_by(Rating.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_average_rating(session: AsyncSession, discord_id: int) -> float:
    from sqlalchemy import func
    result = await session.execute(
        select(func.avg(Rating.score)).where(Rating.user_id == discord_id)
    )
    avg = result.scalar()
    return round(avg, 1) if avg else 0.0
