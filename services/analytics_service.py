import logging

from sqlalchemy import func, select

from database.connection import async_session
from database.models import AnalyticsEvent, Game, UserGame, User

logger = logging.getLogger("bigcousin.analytics")


async def log_event(event_type: str, user_id: int, guild_id: int | None = None, game_id: int | None = None, metadata: dict | None = None):
    try:
        async with async_session() as session:
            event = AnalyticsEvent(
                guild_id=guild_id,
                user_id=user_id,
                event_type=event_type,
                game_id=game_id,
                metadata=metadata,
            )
            session.add(event)
            await session.commit()
    except Exception:
        logger.warning(f"Falha ao registrar evento: {event_type}", exc_info=True)


async def get_total_events() -> int:
    async with async_session() as session:
        result = await session.execute(select(func.count(AnalyticsEvent.id)))
        return result.scalar() or 0


async def get_unique_users() -> int:
    async with async_session() as session:
        result = await session.execute(select(AnalyticsEvent.user_id.distinct()))
        return len(result.fetchall())


async def get_guild_count() -> int:
    async with async_session() as session:
        result = await session.execute(select(AnalyticsEvent.guild_id.distinct()))
        return len([r for r in result.fetchall() if r[0] is not None])


async def get_top_games(limit: int = 10) -> list[tuple[str, int]]:
    async with async_session() as session:
        result = await session.execute(
            select(Game.name, func.count(AnalyticsEvent.id).label("count"))
            .join(Game, AnalyticsEvent.game_id == Game.id)
            .where(AnalyticsEvent.event_type == "addgame")
            .group_by(AnalyticsEvent.game_id, Game.name)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        )
        return [(row[0], row[1]) for row in result.fetchall()]


async def get_top_users(limit: int = 10) -> list[tuple[str, int]]:
    async with async_session() as session:
        result = await session.execute(
            select(func.count(AnalyticsEvent.id).label("count"), AnalyticsEvent.user_id)
            .group_by(AnalyticsEvent.user_id)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(limit)
        )
        rows = []
        for count, uid in result:
            user_result = await session.execute(select(User.username).where(User.discord_id == uid))
            username = user_result.scalar()
            rows.append((username or str(uid), count))
        return rows


async def get_event_breakdown() -> list[tuple[str, int]]:
    async with async_session() as session:
        result = await session.execute(
            select(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id).label("count"))
            .group_by(AnalyticsEvent.event_type)
            .order_by(func.count(AnalyticsEvent.id).desc())
        )
        return [(row[0], row[1]) for row in result.fetchall()]


async def get_total_users_with_data() -> int:
    async with async_session() as session:
        result = await session.execute(select(UserGame.user_id.distinct()))
        return len(result.fetchall())
