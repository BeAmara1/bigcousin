import discord
from discord import app_commands
from discord.ext import commands

from sqlalchemy import select

from database.connection import async_session
from database.models import Game
from services.backlog_service import add_to_backlog, get_backlog, remove_from_backlog
from services.user_service import get_or_create_user
from utils.autocomplete import backlog_games, search_rawg_games
from utils.embeds import backlog_embed
from utils.errors import send_error, send_success
from utils.paginator import PaginatorView

ITEMS_PER_PAGE = 10


class QueroJogarCog(commands.GroupCog, name="querojogar"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add", description="Adiciona um jogo à sua lista de 'quero jogar'")
    @app_commands.autocomplete(jogo=search_rawg_games)
    async def add(self, interaction: discord.Interaction, jogo: str):
        await interaction.response.defer()

        game_id = int(jogo)

        async with async_session() as session:
            user = await get_or_create_user(session, interaction.user)
            try:
                await add_to_backlog(session, user.discord_id, game_id)
                game_result = await session.execute(select(Game).where(Game.id == game_id))
                game = game_result.scalar_one()
                game_name = game.name
            except Exception as e:
                await send_error(interaction, str(e))
                return

        await send_success(
            interaction,
            "📋 Quero Jogar",
            f"**{game_name}** foi adicionado à sua lista de 'quero jogar'!",
        )

    @app_commands.command(name="remove", description="Remove um jogo da sua lista de 'quero jogar'")
    @app_commands.autocomplete(jogo=backlog_games)
    async def remove(self, interaction: discord.Interaction, jogo: str):
        await interaction.response.defer()

        game_id = int(jogo)

        async with async_session() as session:
            user = await get_or_create_user(session, interaction.user)
            try:
                await remove_from_backlog(session, user.discord_id, game_id)
                game_result = await session.execute(select(Game).where(Game.id == game_id))
                game = game_result.scalar_one()
                game_name = game.name
            except Exception as e:
                await send_error(interaction, str(e))
                return

        await send_success(
            interaction,
            "📋 Removido da Lista",
            f"**{game_name}** foi removido da sua lista de 'quero jogar'.",
        )

    @app_commands.command(name="list", description="Lista todos os jogos da sua lista de 'quero jogar'")
    async def list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async with async_session() as session:
            user = await get_or_create_user(session, interaction.user)
            games = await get_backlog(session, user.discord_id)

        if not games:
            await send_error(interaction, "Sua lista de 'quero jogar' está vazia! Use **/querojogar add** para adicionar jogos.")
            return

        async def render_page(page_items, page, total_pages):
            return backlog_embed(page_items, page, total_pages)

        view = PaginatorView(games, ITEMS_PER_PAGE, render_page)
        await view.start(interaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(QueroJogarCog(bot))
