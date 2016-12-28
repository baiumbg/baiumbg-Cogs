import urllib
import json
import discord

class TwitchMeems:
    """Replace twitch emotes with actual images"""

    def __init__(self, bot):
        self.meem_links = {}
        self.bot = bot
        emote_url = 'https://twitchemotes.com/api_cache/v2/images.json'
        bttv_url = 'https://api.betterttv.net/2/emotes'
        response = urllib.request.urlopen(emote_url)
        bttv_response = urllib.request.urlopen(bttv_url)
        emote_dump = json.loads(response.read().decode("utf-8"))
        bttv_dump = json.loads(bttv_response.read().decode("utf-8"))
        image_link = 'https://static-cdn.jtvnw.net/emoticons/v1/{0}/2.0'
        bttv_link = 'https://cdn.betterttv.net/emote/{0}/2x'
        for emote in emote_dump['images'].items():
            keyword = emote[1]['code']
            self.meem_links[keyword] = image_link.format(emote[0])
        for emote in bttv_dump['emotes']:
            keyword = emote['code']
            self.meem_links[keyword] = bttv_link.format(emote['id'])

    async def process_meem(self, message):
        if message.content.startswith('#'):
            keyword = message.content[1:]
            if keyword in self.meem_links.keys():
                meem_embed = discord.Embed()
                meem_embed.set_image(url=self.meem_links[keyword])
                channel = message.channel
                await self.bot.delete_message(message)
                await self.bot.send_message(channel, embed=meem_embed)

def setup(bot):
    meem_cog = TwitchMeems(bot)
    bot.add_listener(meem_cog.process_meem, 'on_message')
    bot.add_cog(meem_cog)
