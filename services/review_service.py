import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Game, Review
from utils.errors import GameNotFoundError, NotInLibraryError

logger = logging.getLogger("bigcousin.review_service")


async def set_review(session: AsyncSession, discord_id: int, game_id: int, text: str) -> Review:
    game = await session.get(Game, game_id)
    if not game:
        raise GameNotFoundError(f"Jogo {game_id} não encontrado no catálogo")

    existing = await session.execute(
        select(Review).where(Review.user_id == discord_id, Review.game_id == game_id)
    )
    review = existing.scalar_one_or_none()

    if review is None:
        from database.models import Rating
        has_game = await session.execute(
            select(Rating).where(Rating.user_id == discord_id, Rating.game_id == game_id)
        )
        if not has_game.scalar_one_or_none():
            raise NotInLibraryError("Adicione o jogo à sua biblioteca primeiro com /addgame")

        review = Review(user_id=discord_id, game_id=game_id, text=text)
        session.add(review)
    else:
        review.text = text

    await session.commit()
    logger.info(f"Review salva: {discord_id} -> {game.name}")
    return review


async def get_review(session: AsyncSession, discord_id: int, game_id: int) -> Review | None:
    result = await session.execute(
        select(Review).where(Review.user_id == discord_id, Review.game_id == game_id)
    )
    return result.scalar_one_or_none()


async def get_user_reviews(session: AsyncSession, discord_id: int, limit: int = 5) -> list[Review]:
    result = await session.execute(
        select(Review)
        .options(selectinload(Review.game))
        .where(Review.user_id == discord_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
