import discord
from discord import app_commands
from discord.ext import commands

from database.connection import async_session
from services.analytics_service import log_event
from services.game_service import remove_from_library
from utils.autocomplete import user_library_games
from utils.errors import send_error, send_success


class RemoveGameCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="remover",
        description="Remove um jogo da sua biblioteca (inclui notas, reviews, favoritos)",
    )
    @app_commands.autocomplete(jogo=user_library_games)
    async def remover(self, interaction: discord.Interaction, jogo: str):
        await interaction.response.defer()

        game_id = int(jogo)

        async with async_session() as session:
            try:
                game_name = await remove_from_library(session, interaction.user.id, game_id)
                await log_event("remover", interaction.user.id, interaction.guild_id, game_id)
            except Exception as e:
                await send_error(interaction, str(e))
                return

        await send_success(
            interaction,
            "🗑️ Jogo Removido",
            f"**{game_name}** foi removido da sua biblioteca junto com notas, reviews e favoritos.",
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(RemoveGameCog(bot))
