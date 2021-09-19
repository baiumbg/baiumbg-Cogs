from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import pagify
import discord
import random
import asyncio

class Bless(commands.Cog):
    """Bless MU Online utilities."""

    def __init__(self, bot):
        default_user_config = {'watchlist': []}
        self._config = Config.get_conf(self, identifier=134621854878007301)
        self._config.register_user(**default_user_config)
        self._bot = bot

    async def watch_auctions():
        while True:
            print("Watching...")
            await asyncio.sleep(10)

    @self.bot.event
    async def on_ready():
        self.bot.loop.create_task(self.watch_auctions())