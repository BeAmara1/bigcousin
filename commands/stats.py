import discord
from discord import app_commands
from discord.ext import commands

from database.connection import async_session
from database.models import User
from services.analytics_service import (
    get_event_breakdown, get_guild_count, get_top_games,
    get_top_users, get_total_events, get_total_users_with_data,
    get_unique_users,
)

DEV_ID = 619659490731622421


class StatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="stats",
        description="[Dev] Mostra estatísticas de uso do bot",
    )
    async def stats(self, interaction: discord.Interaction):
        if interaction.user.id != DEV_ID:
            await interaction.response.send_message(
                "Apenas o desenvolvedor pode usar este comando.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        total_events = await get_total_events()
        unique_users = await get_unique_users()
        guild_count = await get_guild_count()
        users_with_data = await get_total_users_with_data()
        top_games = await get_top_games(5)
        top_users = await get_top_users(5)
        breakdown = await get_event_breakdown()

        embed = discord.Embed(
            title="📊 Estatísticas do BigCousin",
            color=0x5865F2,
        )

        embed.add_field(name="👥 Usuários", value=f"**{unique_users}** únicos\n**{users_with_data}** com dados", inline=True)
        embed.add_field(name="🖥️ Servidores", value=f"**{guild_count}**", inline=True)
        embed.add_field(name="📈 Eventos", value=f"**{total_events}** no total", inline=True)

        if breakdown:
            lines = "\n".join(f"`{t.split('_')[0] if '_' in t else t}` → **{c}**" for t, c in breakdown[:8])
            embed.add_field(name="📋 Comandos", value=lines, inline=False)

        if top_games:
            lines = "\n".join(f"**{i + 1}.** {name} — {count}x" for i, (name, count) in enumerate(top_games))
            embed.add_field(name="🎮 Top Jogos", value=lines, inline=False)

        if top_users:
            lines = "\n".join(f"**{i + 1}.** {name} — {count} comandos" for i, (name, count) in enumerate(top_users))
            embed.add_field(name="🏆 Top Usuários", value=lines, inline=False)

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(StatsCog(bot))
