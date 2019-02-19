from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import pagify
import discord
import random
import requests
import re
import enum
from bs4 import BeautifulSoup

class LoginError(enum.Enum):
    NONE = 0
    INCORRECT_USERNAME = 1,
    INCORRECT_PASSWORD = 2,
    UNKNOWN = 3

class MXL(commands.Cog):
    """Median XL utilities."""

    def __init__(self):
        self.auctions_endpoint = 'https://forum.median-xl.com/api.php?mode=tradecenter'
        self.login_endpoint = 'https://forum.median-xl.com/ucp.php?mode=login'
        self.tradecenter_enpoint = 'https://forum.median-xl.com/tradegold.php'

        default_config = {
            'username': '',
            'password': '',
            'cookies': {
                'MedianXL_u': '',
                'MedianXL_k': '',
                'MedianXL_sid': ''
            }
        }
        self._config = Config.get_conf(self, identifier=134621854878007298)
        self._config.register_guild(**default_config)

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

    @mxl.group(name="config")
    @checks.mod()
    async def config(self, ctx):
        """Configures cookie contents for bypassing the MXL trade center login."""

        pass

    @config.command(name="username")
    async def username(self, ctx, username: str = None):
        """Gets/sets the contents of the MedianXL_k cookie."""

        if username is None:
            current_username = await self._config.guild(ctx.guild).username()
            await ctx.send(f'Current username: {current_username}')
            return

        await self._config.guild(ctx.guild).username.set(username)
        await ctx.channel.send('MXL username set successfully.')

    @config.command(name="password")
    async def password(self, ctx, password: str = None):
        """Gets/sets the contents of the MedianXL_sid cookie."""

        if password is None:
            channel = ctx.author.dm_channel or await ctx.author.create_dm()
            current_password = await self._config.guild(ctx.guild).password()
            await channel.send(f'Current password: {current_password}')
            return

        await self._config.guild(ctx.guild).password.set(password)
        await ctx.message.delete()
        await ctx.channel.send('MXL password set successfully.')

    @mxl.command(name="pricecheck", aliases=["pc"])
    async def pricecheck(self, ctx, *, item: str):
        config = await self._config.guild(ctx.guild).all()

        def not_logged_in_function(tag):
            return 'We\'re sorry' in tag.text

        def no_transactions_found(tag):
            return 'No transactions found.' in tag.text

        def escape_underscore(text):
            return text.replace('_', '\\_')

        pricecheck_response = requests.post(self.tradecenter_enpoint, data={'search': item, 'submit': ''}, cookies=config['cookies'])
        dom = BeautifulSoup(pricecheck_response.text)
        if dom.find(not_logged_in_function):
            error, config = await self._login(ctx.guild)
            if error == LoginError.INCORRECT_USERNAME:
                await self.send(f'Incorrect forum username. Please set a valid one using `[p]mxl config username`.')
                return
            elif error == LoginError.INCORRECT_PASSWORD:
                await self.send(f'Incorrect forum password. Please set the proper one using `[p]mxl config password`.')
                return
            elif error == LoginError.UNKNOWN:
                await self.send('Unknown error during login.')
                return

            pricecheck_response = requests.post(self.tradecenter_enpoint, data={'search': item, 'submit': ''}, cookies=config['cookies'])
            dom = BeautifulSoup(pricecheck_response)
            if dom.find(not_logged_in_function):
                await ctx.send('Couldn\'t login to the forums. Please report this to the plugin author.')
                return

        if not dom.tbody.find(no_transactions_found):
            await ctx.send('No results found.')
            return

        pc_results_raw = [item for item in dom.tbody.contents if item != '\n']
        message = ''
        for result in pc_results_raw:
            columns = [column for column in result.contents if column != '\n']
            message += f'--------------------------\n**Transaction note**: {escape_underscore(columns[3].text)}\n**From**: {escape_underscore(columns[0].a.text)}\n**To**: {escape_underscore(columns[2].a.text)}\n**TG**: {columns[1].div.text}\n**Date**: {columns[4].text}\n'

        for page in pagify(message, delims=['--------------------------']):
            embed = discord.Embed(title=f'Auctions for {item}', description=page)
            await ctx.send(embed=embed)

    async def _login(self, guild):
        config = await self._config.guild(guild).all()
        session_id = requests.get(self.tradecenter_enpoint).cookies['MedianXL_sid']
        login_response = requests.post(self.login_endpoint, data={'username': config['username'], 'password': config['password'], 'autologin': 'on', 'login': 'Login', 'sid': session_id})
        dom = BeautifulSoup(login_response.text)
        error = dom.find(class_='error')
        if error is None:
            config['cookies'] = {
                'MedianXL_sid': login_response.history[0].cookies['MedianXL_sid'],
                'MedianXL_k': login_response.history[0].cookies['MedianXL_k'],
                'MedianXL_u': login_response.history[0].cookies['MedianXL_u']
            }
            await self._config.guild(guild).set(config)
            return LoginError.NONE, config

        if 'incorrect username' in error.text:
            return LoginError.INCORRECT_USERNAME, None

        if 'incorrect password' in error.text:
            return LoginError.INCORRECT_PASSWORD, None

        return LoginError.UNKNOWN, None


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