from .rpg import RPG

async def setup(bot):
    await bot.add_cog(RPG())