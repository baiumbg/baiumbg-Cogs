from .duel import Duel

async def setup(bot):
    await bot.add_cog(Duel())