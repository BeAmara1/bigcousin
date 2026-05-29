import discord
from discord import app_commands
from discord.ext import commands

from sqlalchemy import select

from database.connection import async_session
from database.models import Game
from services.rating_service import set_rating
from services.user_service import get_or_create_user
from utils.autocomplete import user_library_games
from utils.embeds import rating_embed
from utils.errors import send_error


class RateCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="rate",
        description="Avalia um jogo da sua biblioteca com nota de 1 a 10",
    )
    @app_commands.autocomplete(jogo=user_library_games)
    async def rate(
        self,
        interaction: discord.Interaction,
        jogo: str,
        nota: app_commands.Range[int, 1, 10],
    ):
        await interaction.response.defer()

        game_id = int(jogo)

        async with async_session() as session:
            user = await get_or_create_user(session, interaction.user)
            try:
                rating = await set_rating(session, user.discord_id, game_id, nota)
                game_result = await session.execute(select(Game).where(Game.id == game_id))
                game = game_result.scalar_one()
                embed = rating_embed(interaction.user, game, nota)
            except Exception as e:
                await send_error(interaction, str(e))
                return

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(RateCog(bot))
