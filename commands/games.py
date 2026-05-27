import discord
from discord import app_commands
from discord.ext import commands
from database.connection import async_session
from services.game_service import (add_to_library, get_or_create_game,
                                   get_user_games)
from services.rawg_api import rawg_client
from services.user_service import get_or_create_user
from utils.autocomplete import search_rawg_games
from utils.embeds import addgame_embed, game_list_embed
from utils.errors import AlreadyInLibraryError, send_error, send_success
from utils.paginator import PaginatorView

ITEMS_PER_PAGE = 5


class GamesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="addgame",
        description="Adiciona um jogo à sua biblioteca pessoal",
    )
    @app_commands.autocomplete(nome=search_rawg_games)
    async def addgame(self, interaction: discord.Interaction, nome: str):
        await interaction.response.defer()

        game_id = int(nome)

        try:
            game_data = await rawg_client.get_game_details_parsed(game_id)
        except Exception:
            await send_error(interaction, "Erro ao buscar detalhes do jogo na RAWG. Tente novamente.")
            return

        if game_data is None:
            await send_error(interaction, "Jogo não encontrado. Tente novamente.")
            return

        async with async_session() as session:
            user = await get_or_create_user(session, interaction.user)
            game = await get_or_create_game(session, game_data)

            try:
                await add_to_library(session, user.discord_id, game.id)
            except AlreadyInLibraryError as e:
                await send_error(interaction, str(e))
                return

            embed = addgame_embed(interaction.user, game)

        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="games",
        description="Lista todos os jogos da sua biblioteca",
    )
    async def games(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async with async_session() as session:
            user = await get_or_create_user(session, interaction.user)
            games = await get_user_games(session, user.discord_id)

        if not games:
            await send_error(interaction, "Sua biblioteca está vazia! Use **/addgame** para adicionar jogos.")
            return

        async def render_page(page_items, page, total_pages):
            return game_list_embed(interaction.user, page_items, page, total_pages)

        view = PaginatorView(games, ITEMS_PER_PAGE, render_page)
        await view.start(interaction)


async def setup(bot: commands.Bot):
    await bot.add_cog(GamesCog(bot))
