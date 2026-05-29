import discord
from discord import app_commands
from discord.ext import commands

from services.analytics_service import log_event

HELP_TEXT = (
    "**📋 Comandos disponíveis**\n\n"
    "**👤 Perfil**\n"
    "`/profile [usuario]` — Seu perfil ou de outro usuário\n\n"
    "**📚 Biblioteca**\n"
    "`/addgame <nome>` — Adiciona jogo à sua biblioteca\n"
    "`/games` — Lista todos os jogos da sua biblioteca\n"
    "`/remover <jogo>` — Remove um jogo da sua biblioteca\n\n"
    "**⭐ Avaliações**\n"
    "`/rate <jogo> <nota>` — Avalia um jogo (1 a 10)\n"
    "`/review <jogo> <texto>` — Escreve uma review\n\n"
    "**📋 Quero Jogar**\n"
    "`/querojogar add <jogo>` — Adiciona à lista\n"
    "`/querojogar remove <jogo>` — Remove da lista\n"
    "`/querojogar list` — Lista seus jogos\n\n"
    "**⭐ Favoritos**\n"
    "`/favorite <jogo>` — Adiciona ou remove dos favoritos\n\n"
    "**❓ Ajuda**\n"
    "`/help` — Mostra esta mensagem"
)


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Mostra a lista de comandos disponíveis do BigCousin",
    )
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎮 BigCousin — Ajuda",
            description=HELP_TEXT,
            color=0x5865F2,
        )
        embed.set_footer(text="Use TAB para ver os parâmetros de cada comando")

        await log_event("help", interaction.user.id, interaction.guild_id)

        await interaction.response.send_message(embed=embed, ephemeral=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
