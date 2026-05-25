import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Backlog, Favorite, Game, Rating, User
from services.rawg_api import rawg_client
from utils.errors import GameNotFoundError

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


async def search_and_add_game(session: AsyncSession, discord_id: int, query: str) -> Game:
    results = await rawg_client.search_and_parse(query)
    if not results:
        raise GameNotFoundError(f"Nenhum jogo encontrado para: {query}")

    game_data = results[0]
    game = await get_or_create_game(session, game_data)

    existing = await session.execute(
        select(Rating).where(Rating.user_id == discord_id, Rating.game_id == game.id)
    )
    if existing.scalar_one_or_none() is None:
        rating = Rating(user_id=discord_id, game_id=game.id, score=0)
        session.add(rating)
        await session.commit()
        logger.info(f"Jogo {game.name} adicionado ao usuário {discord_id}")

    return game


async def get_user_games(session: AsyncSession, discord_id: int):
    ratings_query = (
        select(Rating)
        .options(selectinload(Rating.game))
        .where(Rating.user_id == discord_id)
        .order_by(Rating.updated_at.desc())
    )
    ratings_result = await session.execute(ratings_query)
    ratings = ratings_result.scalars().all()

    backlog_ids_query = select(Backlog.game_id).where(Backlog.user_id == discord_id)
    backlog_ids_result = await session.execute(backlog_ids_query)
    backlog_ids = {row[0] for row in backlog_ids_result.fetchall()}

    fav_ids_query = select(Favorite.game_id).where(Favorite.user_id == discord_id)
    fav_ids_result = await session.execute(fav_ids_query)
    fav_ids = {row[0] for row in fav_ids_result.fetchall()}

    games_with_flags = []
    for r in ratings:
        if r.game:
            games_with_flags.append((
                r.game,
                r,
                r.game_id in backlog_ids,
                r.game_id in fav_ids,
            ))

    return games_with_flags


async def get_user_game_ids(session: AsyncSession, discord_id: int) -> list[int]:
    result = await session.execute(
        select(Rating.game_id).where(Rating.user_id == discord_id)
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
