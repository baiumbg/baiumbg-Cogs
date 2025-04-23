from .sfx import SFX

async def setup(bot):
    await bot.add_cog(SFX())