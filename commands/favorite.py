import discord
from discord import app_commands
from discord.ext import commands

from database.connection import async_session
from services.favorite_service import toggle_favorite
from services.user_service import get_or_create_user
from utils.autocomplete import user_library_games
from utils.errors import send_error, send_success


class FavoriteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="favorite",
        description="Alterna um jogo como favorito (ou remove dos favoritos)",
    )
    @app_commands.autocomplete(jogo=user_library_games)
    async def favorite(self, interaction: discord.Interaction, jogo: str):
        await interaction.response.defer()

        game_id = int(jogo)

        async with async_session() as session:
            user = await get_or_create_user(session, interaction.user)
            try:
                is_fav = await toggle_favorite(session, user.discord_id, game_id)
                from database.models import Game
                from sqlalchemy import select
                game_result = await session.execute(select(Game).where(Game.id == game_id))
                game = game_result.scalar_one()
            except Exception as e:
                await send_error(interaction, str(e))
                return

        if is_fav:
            await send_success(
                interaction,
                "⭐ Favorito Adicionado",
                f"**{game.name}** agora é um dos seus favoritos!",
            )
        else:
            await send_success(
                interaction,
                "⭐ Favorito Removido",
                f"**{game.name}** foi removido dos seus favoritos.",
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(FavoriteCog(bot))
