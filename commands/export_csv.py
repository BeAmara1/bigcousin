import csv
import io
import zipfile

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from database.connection import async_session
from database.models import (AnalyticsEvent, Backlog, Favorite, Game, Rating,
                             Review, User, UserGame)

DEV_ID = 619659490731622421

TABLES: list[tuple[str, type, list[str]]] = [
    ("usuarios", User, ["discord_id", "username", "avatar_url", "created_at"]),
    ("jogos", Game, ["id", "name", "cover_url", "genres", "platforms", "release_year", "community_rating"]),
    ("biblioteca", UserGame, ["id", "user_id", "game_id", "added_at"]),
    ("avaliacoes", Rating, ["id", "user_id", "game_id", "score", "created_at", "updated_at"]),
    ("reviews", Review, ["id", "user_id", "game_id", "text", "created_at", "updated_at"]),
    ("quero_jogar", Backlog, ["id", "user_id", "game_id", "added_at"]),
    ("favoritos", Favorite, ["id", "user_id", "game_id", "added_at"]),
    ("analytics", AnalyticsEvent, ["id", "guild_id", "user_id", "event_type", "game_id", "extra_data", "created_at"]),
]


async def _table_to_csv(session, model_cls, columns) -> str:
    result = await session.execute(select(model_cls))
    rows = result.scalars().all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns)
    for obj in rows:
        writer.writerow([getattr(obj, col, "") for col in columns])
    return buf.getvalue()


class ExportCSVCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="exportar-csv",
        description="[Dev] Exporta todas as tabelas do banco como CSV",
    )
    async def exportar_csv(self, interaction: discord.Interaction):
        if interaction.user.id != DEV_ID:
            await interaction.response.send_message("Apenas o desenvolvedor pode usar este comando.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        zip_buf = io.BytesIO()
        async with async_session() as session:
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for filename, model_cls, columns in TABLES:
                    csv_content = await _table_to_csv(session, model_cls, columns)
                    zf.writestr(f"{filename}.csv", csv_content)

        zip_buf.seek(0)
        file = discord.File(zip_buf, filename="bigcousin_dados.zip")
        await interaction.followup.send(file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(ExportCSVCog(bot))
