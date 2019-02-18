from redbot.core import commands
import discord
import random
import requests
import re
from bs4 import BeautifulSoup

class MXL(commands.Cog):
    """Median XL utilities."""

    def __init__(self):
        self.auctions_endpoint = 'https://forum.median-xl.com/api.php?mode=tradecenter'

    @commands.guild_only()
    @commands.group(name="mxl")
    async def mxl(self, ctx):
        """A bunch of stuff for the Median XL Diablo II mod."""

        pass

    @mxl.group(name="auctions", invoke_without_command=True)
    async def auctions(self, ctx):
        """MXL auction utilities."""

        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.auctions_list)

    @auctions.command(name="list")
    @commands.cooldown(1, 60, discord.ext.commands.BucketType.user)
    async def auctions_list(self, ctx):
        """
        Prints all the currently active auctions.

        If there are more than 5 active auctions, prints them in a DM instead.
        """
        api_response = requests.get(self.auctions_endpoint)
        if api_response.status_code != 200:
            await ctx.send('Couldn\'t contact the MXL API. Try again later.')
            return

        embeds = self._get_auction_embeds(api_response.json()['auctions'])
        if not embeds:
            await ctx.send('There are no active auctions at the moment.')
            return

        channel = ctx.channel
        if len(embeds) > 5:
            channel = ctx.author.dm_channel or await ctx.author.create_dm()

        for embed in embeds:
            await channel.send(embed=embed)

    @auctions.command(name="search")
    async def auctions_search(self, ctx, *, title: str):
        """
        Searches the titles of the currently active auctions and prints the results.

        If there are more than 5 results, prints them in a DM instead.
        """
        api_response = requests.get(self.auctions_endpoint)
        if api_response.status_code != 200:
            await ctx.send('Couldn\'t contact the MXL API. Try again later.')
            return

        embeds = self._get_auction_embeds(api_response.json()['auctions'])
        matching_auctions = [embed for embed in embeds if re.search(title, embed.title, re.IGNORECASE)]
        if not matching_auctions:
            await ctx.send('There are no active auctions that match that description at the moment.')
            return

        channel = ctx.channel
        if len(matching_auctions) > 5:
            channel = ctx.author.dm_channel or await ctx.author.create_dm()

        for embed in matching_auctions:
            await channel.send(embed=embed)

    def _get_auction_embeds(self, raw_auctions):
        embeds = []
        for auction in raw_auctions:
            soup = BeautifulSoup(auction)
            current_bid = soup.find(class_='coins').text
            number_of_bids = soup.div.div.find(title='Bids').next_sibling.strip()
            title = soup.h4.text
            time_left = soup.span.text.strip()
            started_by = soup.find(class_='username').text
            description = f'Started by: {started_by}\nCurrent bids: {number_of_bids}\nCurrent bid: {current_bid} TG\nTime left: {time_left}'
            image = soup.find(title='Image')
            embed = discord.Embed(title=title, description=description)
            if image is not None:
                embed.set_image(url=image['data-featherlight'])
            embeds.append(embed)

        return embeds