import logging
import traceback

import discord
from discord import app_commands

logger = logging.getLogger("bigcousin.errors")


class GameNotFoundError(app_commands.AppCommandError):
    pass


class AlreadyInLibraryError(app_commands.AppCommandError):
    pass


class NotInLibraryError(app_commands.AppCommandError):
    pass


class AlreadyInBacklogError(app_commands.AppCommandError):
    pass


class NotInBacklogError(app_commands.AppCommandError):
    pass


class AlreadyFavoriteError(app_commands.AppCommandError):
    pass


class APIManager:
    pass


async def send_error(interaction: discord.Interaction, message: str):
    embed = discord.Embed(
        title="Erro",
        description=message,
        color=0xED4245,
    )
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def send_success(interaction: discord.Interaction, title: str, description: str):
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x57F287,
    )
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed)
    else:
        await interaction.response.send_message(embed=embed)


async def global_error_handler(interaction: discord.Interaction, error: app_commands.AppCommandError):
    error = getattr(error, "original", error)

    if isinstance(error, GameNotFoundError):
        await send_error(interaction, "Jogo não encontrado. Verifique o nome e tente novamente.")
    elif isinstance(error, AlreadyInLibraryError):
        await send_error(interaction, "Este jogo já está na sua biblioteca.")
    elif isinstance(error, NotInLibraryError):
        await send_error(interaction, "Este jogo não está na sua biblioteca. Use /addgame primeiro.")
    elif isinstance(error, AlreadyInBacklogError):
        await send_error(interaction, "Este jogo já está no seu backlog.")
    elif isinstance(error, NotInBacklogError):
        await send_error(interaction, "Este jogo não está no seu backlog.")
    elif isinstance(error, AlreadyFavoriteError):
        await send_error(interaction, "Este jogo já está nos seus favoritos.")
    elif isinstance(error, discord.app_commands.errors.TransformerError):
        await send_error(interaction, "Valor inválido. Verifique os parâmetros do comando.")
    else:
        logger.error(f"Erro não tratado: {type(error).__name__}: {error}\n{traceback.format_exc()}")
        await send_error(interaction, "Ocorreu um erro inesperado. Tente novamente mais tarde.")

    return True
