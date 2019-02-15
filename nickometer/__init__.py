from .nickometer import Nickometer

def setup(bot):
    n = Nickometer()
    bot.add_cog(n)