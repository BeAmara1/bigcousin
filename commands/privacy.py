import discord
from discord import app_commands
from discord.ext import commands

PRIVACY_URL = "https://bigcousin.fly.dev/privacy"

PRIVACY_TEXT = (
    "**🔒 Resumo da Política de Privacidade**\n\n"
    "O BigCousin coleta e armazena:\n"
    "• Seu ID, nome e avatar do Discord\n"
    "• Jogos adicionados à sua biblioteca\n"
    "• Avaliações e reviews que você escreve\n"
    "• Jogos marcados como 'quero jogar' ou favoritos\n"
    "• Registro anônimo de uso dos comandos\n\n"
    "**🔐 Seus dados são seus**\n"
    "• Nada é compartilhado com terceiros\n"
    "• A API RAWG recebe apenas buscas por nome de jogos\n"
    "• Você pode excluir todos os seus dados com `/excluir-dados`\n\n"
    f"📄 [Política completa disponível aqui]({PRIVACY_URL})"
)


class PrivacyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="privacidade",
        description="Mostra informações sobre privacidade e coleta de dados",
    )
    async def privacidade(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛡️ Privacidade — BigCousin",
            description=PRIVACY_TEXT,
            color=0x5865F2,
        )
        embed.set_footer(text="Use /excluir-dados para apagar todas as suas informações")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(PrivacyCog(bot))
