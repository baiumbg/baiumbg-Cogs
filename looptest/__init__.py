from .looptest import LoopTest

def setup(bot):
    bot.add_cog(LoopTest(bot))