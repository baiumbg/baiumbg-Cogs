from redbot.core import commands, checks, Config
from discord.ext import tasks

class LoopTest(commands.Cog):
    """Bless MU Online utilities."""
    def __init__(self, bot):
        self.bot = bot
        self.looptest.start()

    @tasks.loop(seconds=10.0)
    async def looptest(self):
        print("aaa")

    @looptest.before_loop
    async def looptest_before(self):
        await self.bot.wait_until_ready()
        print("before")

    def cog_unload(self):
        self.looptest.cancel()