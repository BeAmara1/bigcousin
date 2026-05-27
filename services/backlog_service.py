import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Backlog, Game, Rating, UserGame
from utils.errors import (AlreadyInBacklogError, GameNotFoundError,
                           NotInBacklogError)

logger = logging.getLogger("bigcousin.backlog_service")


async def add_to_backlog(session: AsyncSession, discord_id: int, game_id: int) -> Backlog:
    game = await session.get(Game, game_id)
    if not game:
        raise GameNotFoundError(f"Jogo {game_id} não encontrado no catálogo")

    existing = await session.execute(
        select(Backlog).where(Backlog.user_id == discord_id, Backlog.game_id == game_id)
    )
    if existing.scalar_one_or_none():
        raise AlreadyInBacklogError(f"{game.name} já está no backlog")

    has_game = await session.execute(
        select(UserGame).where(UserGame.user_id == discord_id, UserGame.game_id == game_id)
    )
    if not has_game.scalar_one_or_none():
        raise GameNotFoundError("Adicione o jogo à sua biblioteca primeiro com /addgame")

    backlog = Backlog(user_id=discord_id, game_id=game_id)
    session.add(backlog)
    await session.commit()
    logger.info(f"Adicionado ao backlog: {discord_id} -> {game.name}")
    return backlog


async def remove_from_backlog(session: AsyncSession, discord_id: int, game_id: int) -> bool:
    result = await session.execute(
        select(Backlog).where(Backlog.user_id == discord_id, Backlog.game_id == game_id)
    )
    backlog = result.scalar_one_or_none()
    if not backlog:
        raise NotInBacklogError("Este jogo não está no seu backlog")

    await session.delete(backlog)
    await session.commit()
    logger.info(f"Removido do backlog: {discord_id} -> game_id {game_id}")
    return True


async def get_backlog(session: AsyncSession, discord_id: int) -> list[Game]:
    result = await session.execute(
        select(Backlog)
        .options(selectinload(Backlog.game))
        .where(Backlog.user_id == discord_id)
        .order_by(Backlog.added_at.desc())
    )
    backlogs = result.scalars().all()
    return [b.game for b in backlogs if b.game]


async def get_backlog_game_ids(session: AsyncSession, discord_id: int) -> list[int]:
    result = await session.execute(
        select(Backlog.game_id).where(Backlog.user_id == discord_id)
    )
    return [row[0] for row in result.fetchall()]


async def is_in_backlog(session: AsyncSession, discord_id: int, game_id: int) -> bool:
    result = await session.execute(
        select(Backlog).where(Backlog.user_id == discord_id, Backlog.game_id == game_id)
    )
    return result.scalar_one_or_none() is not None
