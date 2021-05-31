from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import pagify
import discord
import random

class Penis(commands.Cog):
    """Penis related commands."""

    def __init__(self):
        default_config = {'king_dong': 134621854878007296}
        self._config = Config.get_conf(self, identifier=134621854878007300)
        self._config.register_global(**default_config)

    @commands.command()
    @checks.is_owner()
    async def set_king_dong(self, ctx, user: discord.Member):
        """Sets the king dong
        
        Totally not cheating because you rolled a 0 dick length."""

        await self._config.king_dong.set(user.id)

    @commands.command()
    async def penis(self, ctx, *users: discord.Member):
        """Detects user's penis length

        This is 100% accurate.
        Enter multiple users for an accurate comparison!"""

        dongs = {}
        msg = ""
        state = random.getstate()
        king_dong = await self._config.king_dong()

        for user in users:
            random.seed(user.id)

            if user.id == king_dong:
                dong_size = 40
            else:
                dong_size = random.randint(0, 30)

            dongs[user] = "8{}D".format("=" * dong_size)

        random.setstate(state)
        dongs = sorted(dongs.items(), key=lambda x: x[1])

        for user, dong in dongs:
            msg += "**{}'s size:**\n{}\n".format(user.display_name, dong)

        for page in pagify(msg):
            await ctx.send(page)