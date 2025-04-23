from .nickometer import Nickometer

async def setup(bot):
    n = Nickometer()
    await bot.add_cog(n)