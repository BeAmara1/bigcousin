import logging

from discord import app_commands

from database.connection import async_session
from services.backlog_service import get_backlog_game_ids
from services.favorite_service import get_favorite_game_ids
from services.game_service import get_user_game_ids
from services.rawg_api import rawg_client

logger = logging.getLogger("bigcousin.autocomplete")


async def search_rawg_games(interaction, current: str):
    if not current or len(current) < 3:
        return []

    try:
        results = await rawg_client.search(current, page_size=5)
        choices = []
        for game in results:
            name = game.get("name", "Unknown")
            game_id = game.get("id")
            year = ""
            if game.get("released"):
                year = f" ({game['released'][:4]})"
            label = f"{name}{year}"
            choices.append(app_commands.Choice(name=label[:100], value=str(game_id)))
        return choices
    except Exception:
        logger.warning(f"Falha no autocomplete RAWG para: {current}", exc_info=True)
        return []


async def user_library_games(interaction, current: str):
    async with async_session() as session:
        game_ids = await get_user_game_ids(session, interaction.user.id)
        if not game_ids:
            return []

        from database.models import Game
        from sqlalchemy import select
        stmt = select(Game).where(Game.id.in_(game_ids))
        if current:
            stmt = stmt.where(Game.name.ilike(f"%{current}%"))
        result = await session.execute(stmt)
        games = result.scalars().all()

        return [
            app_commands.Choice(name=g.name[:100], value=str(g.id))
            for g in games[:10]
        ]


async def backlog_games(interaction, current: str):
    async with async_session() as session:
        game_ids = await get_backlog_game_ids(session, interaction.user.id)
        if not game_ids:
            return []

        from database.models import Game
        from sqlalchemy import select
        stmt = select(Game).where(Game.id.in_(game_ids))
        if current:
            stmt = stmt.where(Game.name.ilike(f"%{current}%"))
        result = await session.execute(stmt)
        games = result.scalars().all()

        return [
            app_commands.Choice(name=g.name[:100], value=str(g.id))
            for g in games[:10]
        ]


async def favorite_games(interaction, current: str):
    async with async_session() as session:
        game_ids = await get_favorite_game_ids(session, interaction.user.id)
        if not game_ids:
            return []

        from database.models import Game
        from sqlalchemy import select
        stmt = select(Game).where(Game.id.in_(game_ids))
        if current:
            stmt = stmt.where(Game.name.ilike(f"%{current}%"))
        result = await session.execute(stmt)
        games = result.scalars().all()

        return [
            app_commands.Choice(name=g.name[:100], value=str(g.id))
            for g in games[:10]
        ]
