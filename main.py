import logging
import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RAWG_API_KEY = os.getenv("RAWG_API_KEY")

if not DISCORD_TOKEN:
    print("ERRO: DISCORD_TOKEN não encontrado no arquivo .env", file=sys.stderr)
    sys.exit(1)

if not RAWG_API_KEY:
    print("ERRO: RAWG_API_KEY não encontrado no arquivo .env", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("bigcousin")


class BigCousin(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.logger = logger

    async def setup_hook(self):
        from database.connection import init_db
        await init_db()

        await self.load_extension("commands.profile")
        await self.load_extension("commands.games")
        await self.load_extension("commands.rate")
        await self.load_extension("commands.review")
        await self.load_extension("commands.backlog")
        await self.load_extension("commands.favorite")
        await self.load_extension("commands.help")
        await self.load_extension("commands.remove_game")

        await self.tree.sync()
        self.logger.info("Comandos sincronizados com o Discord")

    async def on_ready(self):
        self.logger.info(f"BigCousin conectado como {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="jogos | /profile",
            )
        )


bot = BigCousin()


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    from utils.errors import global_error_handler
    await global_error_handler(interaction, error)


if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Falha no login. Verifique se o DISCORD_TOKEN é válido.")
    except KeyboardInterrupt:
        logger.info("Bot encerrado pelo usuário.")
