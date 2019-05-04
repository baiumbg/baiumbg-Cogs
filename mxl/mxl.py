from redbot.core import commands, checks, Config, data_manager
from redbot.core.utils.chat_formatting import pagify
import discord
import random
import requests
import re
import enum
import flickrapi
from bs4 import BeautifulSoup
from .pastebin import PasteBin
from .constants import SU_ITEMS, SSU_ITEMS, SSSU_ITEMS, SETS, AMULETS, RINGS, JEWELS,\
                       MOS, RUNEWORDS, IGNORED_ITEMS, SHRINE_VESSELS,\
                       VESSEL_TO_SHRINE, QUIVERS, CHARMS, TROPHIES, ORANGE_IGNORED_ITEMS
from .dclasses import ItemDump, PostGenerationErrors

class LoginError(enum.Enum):
    NONE = 0
    INCORRECT_USERNAME = 1,
    INCORRECT_PASSWORD = 2,
    LOGIN_ATTEMPTS_EXCEEDED = 3,
    UNKNOWN = 4

class MXL(commands.Cog):
    """Median XL utilities."""

    def __init__(self):
        self.auctions_endpoint = 'https://forum.median-xl.com/api.php?mode=tradecenter'
        self.tradecenter_enpoint = 'https://forum.median-xl.com/tradegold.php'
        self.forum_login_endpoint = 'https://forum.median-xl.com/ucp.php?mode=login'
        self.forum_logout_endpoint = 'https://forum.median-xl.com/ucp.php?mode=logout&sid={}'
        self.armory_login_endpoint = 'https://tsw.vn.cz/acc/login.php' # POST
        self.armory_logout_endpoint = 'https://tsw.vn.cz/acc/logout.php' # GET
        self.armory_index_endpoint = 'https://tsw.vn.cz/acc/index.php'
        self.armory_character_endpoint = 'https://tsw.vn.cz/acc/char.php?name={}'
        self.item_css = (data_manager.bundled_data_path(self) / 'item_style.css').as_posix()
        self.flickr_client = None

        default_config = {
            'forum_username': '',
            'forum_password': '',
            'forum_cookies': {
                'MedianXL_u': '',
                'MedianXL_k': '',
                'MedianXL_sid': ''
            },
            'armory_username': '',
            'armory_password': '',
            'armory_cookies': {
                'PHPSESSID': ''
            },
            'pastebin_api_key': '',
            'flickr_api_key': '',
            'flickr_api_secret': '',
            'flickr_cache': {}
        }

        default_member_config = {
            'generate_crafted_images': False,
            'crafted_as_base': False
        }
        self._config = Config.get_conf(self, identifier=134621854878007298)
        self._config.register_global(**default_config)
        self._config.register_member(**default_member_config)

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
    @checks.is_owner()
    async def config(self, ctx):
        """Configures forum account login details for item pricechecking."""

        pass

    @config.command(name="forum_username")
    async def forum_username(self, ctx, username: str = None):
        """Gets/sets the username to be used to log into the forums."""

        if username is None:
            current_username = await self._config.forum_username()
            await ctx.send(f'Current username: {current_username}')
            return

        await self._config.forum_username.set(username)
        await ctx.channel.send('MXL username set successfully.')

    @config.command(name="forum_password")
    async def forum_password(self, ctx, password: str = None):
        """Gets/sets the password to be used to log into the forums."""

        if password is None:
            channel = ctx.author.dm_channel or await ctx.author.create_dm()
            current_password = await self._config.forum_password()
            await channel.send(f'Current password: {current_password}')
            return

        await self._config.forum_password.set(password)
        await ctx.message.delete()
        await ctx.channel.send('MXL password set successfully.')

    @config.command(name="armory_username")
    async def armory_username(self, ctx, username: str = None):
        """Gets/sets the username to be used to log into the armory."""

        if username is None:
            current_username = await self._config.armory_username()
            await ctx.send(f'Current username: {current_username}')
            return

        await self._config.armory_username.set(username)
        await ctx.channel.send('MXL armory username set successfully.')

    @config.command(name="armory_password")
    async def armory_password(self, ctx, password: str = None):
        """Gets/sets the password to be used to log into the armory."""

        if password is None:
            channel = ctx.author.dm_channel or await ctx.author.create_dm()
            current_password = await self._config.armory_password()
            await channel.send(f'Current password: {current_password}')
            return

        await self._config.armory_password.set(password)
        await ctx.message.delete()
        await ctx.send('MXL armory password set successfully.')

    @config.command(name="pastebin_api_key")
    async def pastebin_api_key(self, ctx, key: str = None):
        """Gets/sets the API key to be used when creating pastebins."""

        if key is None:
            channel = ctx.author.dm_channel or await ctx.author.create_dm()
            current_api_key = await self._config.pastebin_api_key()
            await channel.send(f'Current API key: {current_api_key}')
            return

        await self._config.pastebin_api_key.set(key)
        await ctx.send('PasteBin API key set successfully.')

    @config.command(name="flickr_api_key")
    async def flickr_api_key(self, ctx, api_key: str = None):
        """Gets/sets the flickr API key."""

        if api_key is None:
            channel = ctx.author.dm_channel or await ctx.author.create_dm()
            current_api_key = await self._config.flickr_api_key()
            await channel.send(f'Current flickr API key: {current_api_key}')
            return

        await self._config.flickr_api_key.set(api_key)
        await ctx.message.delete()
        await ctx.send('Flickr API key set successfully.')

    @config.command(name="flickr_api_secret")
    async def flickr_api_secret(self, ctx, api_secret: str = None):
        """Gets/sets the flickr API secret."""

        if api_secret is None:
            channel = ctx.author.dm_channel or await ctx.author.create_dm()
            current_api_secret = await self._config.flickr_api_secret()
            await channel.send(f'Current flickr API key: {current_api_secret}')
            return

        await self._config.flickr_api_secret.set(api_secret)
        await ctx.message.delete()
        await ctx.send('Flickr API secret set successfully.')

    @mxl.group(name="uconfig", invoke_without_command=True)
    async def uconfig(self, ctx):
        """Configures user options."""

        if ctx.invoked_subcommand is None:
            user_config = await self._config.member(ctx.author).all()
            config_str = ''
            for key, value in user_config.items():
                config_str += f'{key}: {str(value)}\n'
            await ctx.send(f'Your current config:\n```py\n{config_str}```')
            return

    @uconfig.command(name="crafted_as_base")
    async def crafted_as_base(self, ctx, enabled: bool):
        """Crafted items are counted as base items when enabled."""

        await self._config.member(ctx.author).crafted_as_base.set(enabled)
        await ctx.send(f'crafted_as_base {"enabled" if enabled else "disabled"}.')

    @uconfig.command(name="generate_crafted_images")
    async def generate_crafted_images(self, ctx, enabled: bool):
        """
        Images are generated for every crafted item in the supplied characters' inventories when enabled.

        No effect if `crafted_as_base` is enabled.
        Warning: Do not use with large amounts of crafted items - the command will most likely fail and will make the bot reconnect to Discord.
        """
        await self._config.member(ctx.author).generate_crafted_images.set(enabled)
        await ctx.send(f'generate_crafted_images {"enabled" if enabled else "disabled"}.')

    @mxl.command(name="pricecheck", aliases=["pc"])
    async def pricecheck(self, ctx, *, item: str):
        """
        Checks all TG transactions for the provided item/string.

        Note: Only looks at the first 25 results.
        """

        config = await self._config.all()
        if not config['forum_username']:
            await ctx.send(f'No forum account is currently configured for this server. Use `{ctx.prefix}mxl config` to set one up.')
            return

        def not_logged_in_function(tag):
            return 'We\'re sorry' in tag.text

        def no_transactions_found(tag):
            return 'No transactions found.' in tag.text

        def escape_underscore(text):
            return text.replace('_', '\\_')

        pricecheck_response = requests.post(self.tradecenter_enpoint, data={'search': item, 'submit': ''}, cookies=config['forum_cookies'])
        dom = BeautifulSoup(pricecheck_response.text, 'html.parser')
        if dom.find(not_logged_in_function):
            error, config = await self._forum_login()
            if error == LoginError.INCORRECT_USERNAME:
                await ctx.send(f'Incorrect forum username. Please set a valid one using `{ctx.prefix}mxl config username`.')
                return
            elif error == LoginError.INCORRECT_PASSWORD:
                await ctx.send(f'Incorrect forum password. Please set the proper one using `{ctx.prefix}mxl config password`.')
                return
            elif error == LoginError.LOGIN_ATTEMPTS_EXCEEDED:
                await ctx.send(f'Maximum login attempts exceeded. Please login to the forum manually (with the configured account) and solve the CAPTCHA.')
                return
            elif error == LoginError.UNKNOWN:
                await ctx.send('Unknown error during login.')
                return

            pricecheck_response = requests.post(self.tradecenter_enpoint, data={'search': item, 'submit': ''}, cookies=config['forum_cookies'])
            dom = BeautifulSoup(pricecheck_response.text, 'html.parser')
            if dom.find(not_logged_in_function):
                await ctx.send('Couldn\'t login to the forums. Please report this to the plugin author.')
                return

        if dom.tbody.find(no_transactions_found):
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


    @mxl.group(name="logout")
    @checks.is_owner()
    async def logout(self, ctx):
        """Logs out the current forum/armory session."""

        pass

    @logout.command(name="forum")
    async def logout_forum(self, ctx):
        """
        Logs out the current forum session.

        Use if you want to change the forum user.
        """

        config = await self._config.all()
        if not config['forum_cookies']['MedianXL_sid']:
            await ctx.send('Not logged in.')
            return

        logout_response = requests.get(self.forum_logout_endpoint.format(config['forum_cookies']['MedianXL_sid']), cookies=config['forum_cookies'])
        dom = BeautifulSoup(logout_response.text, 'html.parser')
        if dom.find(title='Login'):
            config['forum_cookies'] = {
                'MedianXL_u': '',
                'MedianXL_k': '',
                'MedianXL_sid': ''
            }
            await self._config.set(config)
            await ctx.send('Forum account logged out successfully.')
            return

        if dom.find(title='Logout'):
            await ctx.send('Forum logout attempt was unsuccessful.')
            return

        await ctx.send('Unknown error during forum logout.')

    @logout.command(name="armory")
    async def logout_armory(self, ctx):
        """
        Logs out the current armory session.

        Use if you want to change the armory user.
        """

        config = await self._config.all()
        if not config['armory_cookies']['PHPSESSID']:
            await ctx.send('Not logged in.')
            return

        logout_response = requests.get(self.armory_logout_endpoint, cookies=config['armory_cookies'])
        dom = BeautifulSoup(logout_response.text, 'html.parser')
        if not dom.find(action='login.php'):
            await ctx.send('Unknown error during armory logout.')

        config['armory_cookies']['PHPSESSID'] = ''
        await self._config.set(config)
        await ctx.send('Armory account logged out successfully.')
        return

    @mxl.group(name="armory")
    async def armory(self, ctx):
        """TSW (not)armory utilities."""

        pass

    @armory.command(name="dump")
    async def armory_dump(self, ctx, *characters):
        """Dumps all the items of the supplied characters.

        Dumps the supplied character's items (stash, inventory, cube, equipped) into a formated string to be posted on the forums.
        The characters must be publicly viewable - log into http://tsw.vn.cz/acc/ to configure visibility.
        """

        config = await self._config.all()
        user_config = await self._config.member(ctx.author).all()
        if not config['pastebin_api_key']:
            await ctx.send(f'Pastebin API key hasn\'t been configured yet. Configure one using `{ctx.prefix}mxl config pastebin_api_key`.')
            return

        if not config['armory_username']:
            await ctx.send(f'Armory account hasn\'t been configured yet. Configure one using `{ctx.prefix}mxl config armory_username/armory_password`.')
            return

        if not config['flickr_api_key'] or not config['flickr_api_secret'] and self.flickr_client is None:
            await ctx.send(f'Flickr API key/secret hasn\'t been configured yet. Configure using `{ctx.prefix}mxl config flickr_api_key/flickr_api_secret`.')
            return

        if not self.flickr_client:
            self.flickr_client = flickrapi.FlickrAPI(config['flickr_api_key'], config['flickr_api_secret'], format='xmlnode')

        if not self.flickr_client.token_valid(perms='write'):
            await ctx.send(f'Missing flickr client token. Use `{ctx.prefix}mxl flickr` to configure one.')
            return

        items = ItemDump()
        for character in characters:
            character_response = requests.get(self.armory_character_endpoint.format(character), cookies=config['armory_cookies'])
            dom = BeautifulSoup(character_response.text, 'html.parser')
            if dom.find(action='login.php'):
                error, config = await self._armory_login()
                if error:
                    await ctx.send('Incorrect armory username/password or armory is not reachable.')
                    return
                character_response = requests.get(self.armory_character_endpoint.format(character), cookies=config['armory_cookies'])
                dom = BeautifulSoup(character_response.text, 'html.parser')

            if 'not allowed' in dom.h1.text:
                await ctx.send(f'{character}\'s armory is private - skipping. Please log into the armory and make it publicly viewable to dump its items.')
                continue

            item_dump = dom.find_all(class_='item-wrapper')
            self._scrape_items(item_dump, items, character, user_config)

        if not items:
            await ctx.send('No items found.')
            return

        post, cache_update, generation_error = items.to_trade_post(self.flickr_client, self.item_css, user_config, config['flickr_cache'])
        if cache_update:
            current_cache = await self._config.flickr_cache()
            await self._config.flickr_cache.set({**cache_update, **current_cache})

        if generation_error == PostGenerationErrors.IMAGE_UPLOAD_FAILED:
            await ctx.send('An error occurred while uploading an item\'s image to flickr. Try again later.')
            return
        elif generation_error == PostGenerationErrors.UNKNOWN:
            await ctx.send('An unknown error occurred while generating your trade post. Try again later.')
            return

        pastebin_link = await self._create_pastebin(post, f'MXL trade post for characters: {", ".join(characters)}')
        channel = ctx.author.dm_channel or await ctx.author.create_dm()
        if pastebin_link:
            await channel.send(f'Dump successful. Here you go: {pastebin_link}')
            return

        await ctx.send('Couldn\'t create the trade post pastebin - 24h limit is probably reached. Check your DMs.')
        for page in pagify(post):
            await channel.send(embed=discord.Embed(description=page))

    @mxl.command(name="flickr")
    @checks.is_owner()
    async def flickr(self, ctx, verify_code: str = None):
        """
        Connects a Flickr account that will be used when uploading images.

        Use `[p]mxl flickr <code>` when you have obtained the code from the link that the bot sends you.
        """
        config = await self._config.all()

        if not config['flickr_api_key'] or not config['flickr_api_secret'] and self.flickr_client is None:
            await ctx.send(f'Flickr API key/secret hasn\'t been configured yet. Configure using `{ctx.prefix}mxl config flickr_api_key/flickr_api_secret`.')
            return

        if not self.flickr_client:
            self.flickr_client = flickrapi.FlickrAPI(config['flickr_api_key'], config['flickr_api_secret'], format='xmlnode')

        if self.flickr_client.token_valid(perms='write'):
            await ctx.send(f'Flickr already authenticated.')
            return

        if verify_code:
            self.flickr_client.get_access_token(verify_code)
            await ctx.send('Flickr authenticated successfully.')
            return

        self.flickr_client.get_request_token(oauth_callback='oob')
        authorize_url = self.flickr_client.auth_url(perms='write')
        channel = ctx.author.dm_channel or await ctx.author.create_dm()
        await channel.send(f'Click here to authorize flickr: {authorize_url}')

    @mxl.group(name="flickrcache")
    @checks.is_owner()
    async def flickr_cache(self, ctx):
        """Manages the flickr image cache."""

        pass

    @flickr_cache.command(name="clear")
    async def flickr_cache_clear(self, ctx):
        """
        Clears the flickr image cache.

        This will not delete the images from the connected flickr account - you have to do that manually.
        """

        await self._config.flickr_cache.set({})
        await ctx.send('Flickr cache cleared successfully.')

    @flickr_cache.command(name="list")
    async def flickr_cache_list(self, ctx):
        """Lists the currrent flickr cache in a DM."""

        flickr_cache = await self._config.flickr_cache()
        flickr_cache_msg = f'{"HTML MD5".ljust(32)} Image link\n'
        for md5, link in flickr_cache.items():
            flickr_cache_msg += f'{md5} {link}\n'

        channel = ctx.author.dm_channel or await ctx.author.create_dm()
        for page in pagify(flickr_cache_msg, page_length=1992):
            await channel.send(f'```py\n{page}```')

    async def _forum_login(self):
        config = await self._config.all()
        session_id = requests.get(self.tradecenter_enpoint).cookies['MedianXL_sid']
        login_response = requests.post(self.forum_login_endpoint, data={'username': config['forum_username'], 'password': config['forum_password'], 'autologin': 'on', 'login': 'Login', 'sid': session_id})
        dom = BeautifulSoup(login_response.text, 'html.parser')
        error = dom.find(class_='error')
        if error is None:
            config['forum_cookies'] = {
                'MedianXL_sid': login_response.history[0].cookies['MedianXL_sid'],
                'MedianXL_k': login_response.history[0].cookies['MedianXL_k'],
                'MedianXL_u': login_response.history[0].cookies['MedianXL_u']
            }
            await self._config.set(config)
            return LoginError.NONE, config

        if 'incorrect username' in error.text:
            return LoginError.INCORRECT_USERNAME, None

        if 'incorrect password' in error.text:
            return LoginError.INCORRECT_PASSWORD, None

        if 'maximum allowed number of login attempts' in error.text:
            return LoginError.LOGIN_ATTEMPTS_EXCEEDED, None

        return LoginError.UNKNOWN, None

    async def _armory_login(self):
        config = await self._config.all()
        session_id = requests.get(self.armory_index_endpoint).cookies['PHPSESSID']
        login_response = requests.post(self.armory_login_endpoint, data={'user': config['armory_username'], 'pass': config['armory_password']}, cookies={'PHPSESSID': session_id})
        dom = BeautifulSoup(login_response.text, 'html.parser')
        if not dom.contents:
            config['armory_cookies'] = {
                'PHPSESSID': session_id
            }
            await self._config.set(config)
            return False, config

        return True, None

    def _scrape_items(self, item_dump, items, character, user_config):
        for item in item_dump:
            # For multi-line charm names
            # Note: May need updating in the near future
            if item.font.br:
                item.font.br.extract()

            item_name = item.font.text
            set_match = re.search('\[([^\]]+)', item.font.text)

            if item_name in IGNORED_ITEMS:
                continue

            if set_match:
                set_name = set_match.group(1)
                item_name = item_name.split('[')[0].strip()
                items.increment_set_item(set_name, item_name, character, item.parent.parent)
                continue

            if item.span['class'][0] == 'color-green' and item_name in SETS.keys():
                set_name = SETS[item_name]
                items.increment_set_item(set_name, item_name, character, item.parent.parent)
                continue

            if item_name in SU_ITEMS:
                items.increment_su(item_name, character, item.parent.parent)
                continue

            if 'Hanfod' in item_name:
                items.increment_su('Hanfod Tân', character, item.parent.parent)
                continue

            if item_name == 'Jewel':
                items.increment_other('Jewel', character, item.parent.parent)
                continue

            if item_name in SSU_ITEMS:
                items.increment_ssu(item_name, character, item.parent.parent)
                continue

            if item_name in SSSU_ITEMS:
                items.increment_sssu(item_name, character, item.parent.parent)
                continue

            if item_name in RUNEWORDS:
                items.increment_rw(item_name, character, item.parent.parent)
                continue

            if item_name in AMULETS:
                items.increment_amulet(item_name, character, item.parent.parent)
                continue

            if item_name in RINGS:
                items.increment_ring(item_name, character, item.parent.parent)
                continue

            if item_name in JEWELS:
                items.increment_jewel(item_name, character, item.parent.parent)
                continue

            if item_name in QUIVERS:
                items.increment_quiver(item_name, character, item.parent.parent)
                continue

            if item_name in MOS:
                items.increment_mo(item_name, character, item.parent.parent)
                continue

            if item.span['class'][0] == 'color-white' or item.span['class'][0] == 'color-blue':
                base_name = item_name + ' [eth]' if 'Ethereal' in item.text else ''.join(item_name.split('Superior '))
                items.increment_rw_base(base_name, character, item.parent.parent)
                continue

            if item.span['class'][0] == 'color-yellow':
                items.increment_shrine_base(item_name, character, item.parent.parent)
                continue

            if item_name in CHARMS:
                items.increment_charm(item_name, character, item.parent.parent)
                continue

            shrine_match = re.search('Shrine \(([^\)]+)', item_name)
            if shrine_match:
                shrine_name = item_name.split('(')[0].strip()
                amount = int(shrine_match.group(1)) / 10
                items.increment_shrine(shrine_name, character, item.parent.parent, amount)
                continue

            if item_name in SHRINE_VESSELS:
                vessel_amount = int((re.search('Quantity: ([0-9]+)', item.find(class_='color-grey').text)).group(1))
                shrine_name = VESSEL_TO_SHRINE[item_name]
                items.increment_shrine(shrine_name, character, item.parent.parent, vessel_amount)
                continue

            if item_name == 'Arcane Cluster':
                crystals_amount = int((re.search('Quantity: ([0-9]+)', item.find(class_='color-grey').text)).group(1))
                items.increment_other('Arcane Crystal', character, item.parent.parent, crystals_amount)
                continue

            # TODO: Update when Aahz fixes runestone formatting
            if item_name == ')':
                item_name = f'Depleted Riftstone ({item.span.contents[1].text})'
                items.increment_other(item_name, character, item.parent.parent)

            AC_shards_match = re.search('Shards \(([^\)]+)', item_name)
            if AC_shards_match:
                amount = int(AC_shards_match.group(1)) / 5
                items.increment_other('Arcane Crystal', character, item.parent.parent, amount)
                continue

            if item.span['class'][0] == 'color-orange' and item_name not in ORANGE_IGNORED_ITEMS and item_name not in TROPHIES:
                if user_config['crafted_as_base']:
                    items.increment_shrine_base(item_name, character, item.parent.parent)
                    continue

                items.increment_crafted(item_name, character, item.parent.parent)
                continue

            if item_name in TROPHIES:
                items.increment_trophy(item_name, character, item.parent.parent)
                continue

            items.increment_other(item_name, character, item.parent.parent)

    async def _create_pastebin(self, text, title=None):
        api_key = await self._config.pastebin_api_key()
        pb = PasteBin(api_key)
        pb_link = pb.paste(text, name=title, private='1', expire='1D')
        return None if 'Bad API request' in pb_link or 'Post limit' in pb_link else pb_link

    def _get_auction_embeds(self, raw_auctions):
        embeds = []
        for auction in raw_auctions:
            soup = BeautifulSoup(auction, 'html.parser')
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
