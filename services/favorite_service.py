import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Favorite, Game, Rating
from utils.errors import GameNotFoundError, NotInLibraryError

logger = logging.getLogger("bigcousin.favorite_service")


async def toggle_favorite(session: AsyncSession, discord_id: int, game_id: int) -> bool:
    game = await session.get(Game, game_id)
    if not game:
        raise GameNotFoundError(f"Jogo {game_id} não encontrado no catálogo")

    has_game = await session.execute(
        select(Rating).where(Rating.user_id == discord_id, Rating.game_id == game_id)
    )
    if not has_game.scalar_one_or_none():
        raise NotInLibraryError("Adicione o jogo à sua biblioteca primeiro com /addgame")

    existing = await session.execute(
        select(Favorite).where(Favorite.user_id == discord_id, Favorite.game_id == game_id)
    )
    favorite = existing.scalar_one_or_none()

    if favorite:
        await session.delete(favorite)
        await session.commit()
        logger.info(f"Removido dos favoritos: {discord_id} -> {game.name}")
        return False
    else:
        favorite = Favorite(user_id=discord_id, game_id=game_id)
        session.add(favorite)
        await session.commit()
        logger.info(f"Adicionado aos favoritos: {discord_id} -> {game.name}")
        return True


async def get_favorites(session: AsyncSession, discord_id: int) -> list[Game]:
    result = await session.execute(
        select(Favorite)
        .options(selectinload(Favorite.game))
        .where(Favorite.user_id == discord_id)
        .order_by(Favorite.added_at.desc())
    )
    favorites = result.scalars().all()
    return [f.game for f in favorites if f.game]


async def get_favorite_game_ids(session: AsyncSession, discord_id: int) -> list[int]:
    result = await session.execute(
        select(Favorite.game_id).where(Favorite.user_id == discord_id)
    )
    return [row[0] for row in result.fetchall()]


async def is_favorite(session: AsyncSession, discord_id: int, game_id: int) -> bool:
    result = await session.execute(
        select(Favorite).where(Favorite.user_id == discord_id, Favorite.game_id == game_id)
    )
    return result.scalar_one_or_none() is not None
