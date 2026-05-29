import discord
from discord import app_commands
from discord.ext import commands

from database.connection import async_session
from services.user_service import delete_user_data


class ConfirmDeleteView(discord.ui.View):
    def __init__(self, target_id: int):
        super().__init__(timeout=60)
        self.target_id = target_id
        self.confirmed = False

    @discord.ui.button(label="Sim, quero excluir", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("Você não pode confirmar por outro usuário.", ephemeral=True)
            return

        await interaction.response.defer()
        async with async_session() as session:
            await delete_user_data(session, self.target_id)

        embed = discord.Embed(
            title="🗑️ Dados Excluídos",
            description="Todos os seus dados foram removidos do banco do BigCousin.",
            color=0x57F287,
        )
        await interaction.followup.send(embed=embed)
        self.confirmed = True
        self.stop()

    @discord.ui.button(label="Não, cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("Você não pode cancelar por outro usuário.", ephemeral=True)
            return

        embed = discord.Embed(
            title="✅ Operação Cancelada",
            description="Nenhum dado foi removido.",
            color=0xFEE75C,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()


class DeleteDataCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="excluir-dados",
        description="Exclui permanentemente todos os seus dados do BigCousin",
    )
    async def excluir_dados(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚠️ Excluir Todos os Dados",
            description=(
                "Tem certeza? Esta ação irá remover **permanentemente**:\n\n"
                "• Todos os jogos da sua biblioteca\n"
                "• Todas as suas avaliações e reviews\n"
                "• Sua lista de 'quero jogar'\n"
                "• Seus favoritos\n"
                "• Registros de uso\n\n"
                "Esta ação **não pode ser desfeita**."
            ),
            color=0xED4245,
        )
        view = ConfirmDeleteView(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(DeleteDataCog(bot))
