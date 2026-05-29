import discord
from discord import app_commands
from discord.ext import commands

from database.connection import async_session
from services.analytics_service import log_event
from services.user_service import get_or_create_user, get_user_stats
from utils.embeds import profile_embed


class ProfileCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="profile",
        description="Mostra seu perfil de jogos com estatísticas, favoritos e backlog",
    )
    async def profile(self, interaction: discord.Interaction, usuario: discord.Member = None):
        await interaction.response.defer()

        target = usuario or interaction.user

        async with async_session() as session:
            user = await get_or_create_user(session, target)
            stats = await get_user_stats(session, user.discord_id)

        embed = profile_embed({
            "user": user,
            "stats": stats,
        })

        await log_event("profile", interaction.user.id, interaction.guild_id)

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCog(bot))
