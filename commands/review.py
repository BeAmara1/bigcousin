import discord
from discord import app_commands
from discord.ext import commands

from database.connection import async_session
from services.review_service import set_review
from services.user_service import get_or_create_user
from utils.autocomplete import user_library_games
from utils.embeds import review_embed
from utils.errors import send_error


class ReviewCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="review",
        description="Escreve uma review para um jogo da sua biblioteca",
    )
    @app_commands.autocomplete(jogo=user_library_games)
    async def review(
        self,
        interaction: discord.Interaction,
        jogo: str,
        texto: str,
    ):
        await interaction.response.defer()

        game_id = int(jogo)

        async with async_session() as session:
            user = await get_or_create_user(session, interaction.user)
            try:
                review = await set_review(session, user.discord_id, game_id, texto)
                from database.models import Game
                from sqlalchemy import select
                game_result = await session.execute(select(Game).where(Game.id == game_id))
                game = game_result.scalar_one()
            except Exception as e:
                await send_error(interaction, str(e))
                return

        embed = review_embed(interaction.user, game, texto)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReviewCog(bot))
