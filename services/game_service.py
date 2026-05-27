import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Backlog, Favorite, Game, Rating, User, UserGame
from services.rawg_api import rawg_client
from utils.errors import AlreadyInLibraryError, GameNotFoundError

logger = logging.getLogger("bigcousin.game_service")


async def get_or_create_game(session: AsyncSession, game_data: dict) -> Game:
    game = await session.get(Game, game_data["id"])
    if game is None:
        game = Game(
            id=game_data["id"],
            name=game_data["name"],
            cover_url=game_data.get("cover_url"),
            description=game_data.get("description"),
            genres=game_data.get("genres"),
            platforms=game_data.get("platforms"),
            release_year=game_data.get("release_year"),
            community_rating=game_data.get("community_rating"),
        )
        session.add(game)
        await session.commit()
        logger.info(f"Novo jogo adicionado ao catálogo: {game.name}")
    return game


async def add_to_library(session: AsyncSession, discord_id: int, game_id: int) -> UserGame:
    existing = await session.execute(
        select(UserGame).where(UserGame.user_id == discord_id, UserGame.game_id == game_id)
    )
    if existing.scalar_one_or_none():
        game = await session.get(Game, game_id)
        name = game.name if game else str(game_id)
        raise AlreadyInLibraryError(f"**{name}** já está na sua biblioteca!")

    user_game = UserGame(user_id=discord_id, game_id=game_id)
    session.add(user_game)
    await session.commit()
    return user_game


async def search_and_add_game(session: AsyncSession, discord_id: int, query: str) -> Game:
    results = await rawg_client.search_and_parse(query)
    if not results:
        raise GameNotFoundError(f"Nenhum jogo encontrado para: {query}")

    game_data = results[0]
    game = await get_or_create_game(session, game_data)
    await add_to_library(session, discord_id, game.id)
    return game


async def get_user_games(session: AsyncSession, discord_id: int):
    user_games_query = (
        select(UserGame)
        .options(selectinload(UserGame.game))
        .where(UserGame.user_id == discord_id)
        .order_by(UserGame.added_at.desc())
    )
    result = await session.execute(user_games_query)
    user_games = result.scalars().all()

    game_ids = [ug.game_id for ug in user_games]
    ratings = {}
    if game_ids:
        ratings_query = select(Rating).where(
            Rating.user_id == discord_id,
            Rating.game_id.in_(game_ids)
        )
        ratings_result = await session.execute(ratings_query)
        for r in ratings_result.scalars().all():
            ratings[r.game_id] = r

    backlog_ids = {row[0] for row in (await session.execute(
        select(Backlog.game_id).where(Backlog.user_id == discord_id)
    )).fetchall()}

    fav_ids = {row[0] for row in (await session.execute(
        select(Favorite.game_id).where(Favorite.user_id == discord_id)
    )).fetchall()}

    games_with_flags = []
    for ug in user_games:
        if ug.game:
            games_with_flags.append((
                ug.game,
                ratings.get(ug.game_id),
                ug.game_id in backlog_ids,
                ug.game_id in fav_ids,
            ))

    return games_with_flags


async def get_user_game_ids(session: AsyncSession, discord_id: int) -> list[int]:
    result = await session.execute(
        select(UserGame.game_id).where(UserGame.user_id == discord_id)
    )
    return [row[0] for row in result.fetchall()]


async def get_user_games_with_details(session: AsyncSession, discord_id: int) -> list[Game]:
    game_ids = await get_user_game_ids(session, discord_id)
    if not game_ids:
        return []

    result = await session.execute(
        select(Game).where(Game.id.in_(game_ids))
    )
    return list(result.scalars().all())
