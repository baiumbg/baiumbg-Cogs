from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import pagify
import discord
from discord.ext import tasks
from bs4 import BeautifulSoup
from .market_item import MarketItem, MarketItemQuality
from .market_item_filter import MarketItemFilter, MarketItemPriceType
import requests
import re
import traceback

OPTION_MIN_GRADE_REGEX = re.compile(r"mingrade=(\d+)", re.IGNORECASE)
OPTION_MIN_UPGRADE_REGEX = re.compile(r"minupgrade=(\d+)", re.IGNORECASE)
OPTION_MIN_OPT_REGEX = re.compile(r"minopt=(\d+)", re.IGNORECASE)
OPTION_MAX_PRICE_REGEX = re.compile(r"maxprice=((\d*[.])?\d+)(k+|bon)")
OPTION_SELLER_REGEX = re.compile(r"seller=(.+)")

class Bless(commands.Cog):
    """Bless MU Online utilities."""

    def __init__(self, bot):
        default_member_config = {'watchlist': [], 'filter_id': 0}
        default_guild_config = {'notification_channel': 0}
        self.config = Config.get_conf(self, identifier=134621854878007301)
        self.config.register_member(**default_member_config)
        self.config.register_guild(**default_guild_config)
        self.bot = bot
        self.last_seen = []
        self.filters = {}
        self.watch_auctions.start()

    @tasks.loop(seconds=10.0, minutes=0.0, hours=0.0, count=None)
    async def watch_auctions(self):
        try:
            html = requests.get("https://mu.bless.gs/en/index.php?page=market&serv=server3")
        except Exception as e:
            print(e)
            return

        soup = BeautifulSoup(html.text, features="html.parser")
        item_rows = soup.find_all("tr", class_=re.compile(r"row-buyitem.*"))
        print(f"Retrieved market. # of items: {len(item_rows)}")
        i = 0
        for item in item_rows:
            row_columns = item.find_all("td")
            if "title" not in row_columns[1].a.attrs.keys():
                continue

            market_item = MarketItem(row_columns)
            if (market_item.serial, market_item.seller, market_item.price) in self.last_seen:
                break

            for guild_id, members in self.filters.items():
                guild = self.bot.get_guild(guild_id)
                for member_id, watchlist in members.items():
                    for item_filter in watchlist:
                        if item_filter.matches_item(market_item):
                            channel_id = await self.config.guild(guild).notification_channel()
                            channel = guild.get_channel(channel_id)
                            member = await guild.fetch_member(member_id)
                            await channel.send(f'{member.mention} an item has been found for you:\n```Name: {market_item.name}\nSeller: {market_item.seller}\nPrice: {market_item.price}{"bons" if market_item.price_type == MarketItemPriceType.BONS else "kk Zen"}```')

            self.last_seen.insert(i, (market_item.serial, market_item.seller, market_item.price))
            i += 1
            if len(self.last_seen) > 100:
                self.last_seen.pop()

    @watch_auctions.before_loop
    async def load_filters(self):
        await self.bot.wait_until_ready()

        print("[Bless] Starting to watch market.")
        raw_filters = await self.config.all_members()
        for _, members in raw_filters.items():
            for member, member_config in members.items():
                member_watchlist = [MarketItemFilter.from_dict(f) for f in member_config["watchlist"]]
                members[member] = member_watchlist

        self.filters = raw_filters

    @commands.guild_only()
    @commands.group(name="bless")
    async def bless(self, ctx):
        """A bunch of stuff for the Bless MU Online server."""

        pass

    @bless.command()
    async def watch(self, ctx, item_name : str, *options):
        """Registers a filter to match new market items against. Pings the filter owner if an item matches the filter.

        Item name must be in quotations if it has multiple words.
        Use "" if you don't care about item name.

        List of options:
        luck - self-explanatory
        normal - normal quality
        exc - excellent quality
        anc - ancient quality
        minopt=4 - minimum luck options
        mingrade=30 - minimum item grade
        minupgrade=11 - minimum item upgrade level
        maxprice=10bon, maxprice=10kkzen - maximum item price, bon format - {number}bon, zen format - {number}{kk or kkk}zen
        seller=Kopile - seller name
        dd - damage decrease
        ref - reflect
        zen - self-explanatory
        manaok - mana on kill (weapons)
        speed - self-explanatory
        mana - %mana
        dmg/20 - self-explanatory
        rate - def rate
        hpok - hp on kill (weapons)
        dmg - 2% dmg
        hp - self-explanatory
        excrate - excellent damage rate

        Examples:
        [p]bless watch "Thunder Hawk" exc minopt=4 luck dd ref
        [p]bless watch "" anc luck mingrade=30
        [p]bless watch Spyro anc minupgrade=11
        [p]bless watch Atlantis exc dmg excrate minupgrade=13
        [p]bless watch "Ring of Magic" hp ref dd
        """
        channel = await self.config.guild(ctx.guild).notification_channel()
        if channel == 0:
            await ctx.channel.send(f"This server's admin has not set a channel for notifications. See `{ctx.prefix}help bless setchannel`.")
            return

        filter_id = await self.config.member(ctx.author).filter_id()
        item_filter = MarketItemFilter(filter_id)
        item_filter.name = item_name

        for option in options:
            if option.lower() == "exc":
                item_filter.quality = MarketItemQuality.EXCELLENT
                continue

            if option.lower() == "anc":
                item_filter.quality = MarketItemQuality.ANCIENT
                continue

            if option.lower() == "normal":
                item_filter.quality = MarketItemQuality.NORMAL
                continue

            if option.lower() == "luck":
                item_filter.luck = True
                continue

            if option.lower() == "zen" or option.lower() == "manaok":
                item_filter.zen_or_mana = True
                continue

            if option.lower() == "ref" or option.lower() == "speed":
                item_filter.ref_or_speed = True
                continue

            if option.lower() == "mana" or option.lower() == "dmg/20":
                item_filter.mana_or_dmg_per_lvl = True
                continue

            if option.lower() == "rate" or option.lower() == "hpok":
                item_filter.def_rate_or_hp = True
                continue

            if option.lower() == "dd" or option.lower() == "dmg":
                item_filter.dd_or_dmg = True
                continue

            if option.lower() == "hp" or option.lower() == "excrate":
                item_filter.hp_or_exc_rate = True
                continue

            min_grade_match = OPTION_MIN_GRADE_REGEX.match(option)
            if min_grade_match:
                item_filter.grade = int(min_grade_match.group(1))
                continue

            min_upgrade_match = OPTION_MIN_UPGRADE_REGEX.match(option)
            if min_upgrade_match:
                item_filter.upgrade_level = int(min_upgrade_match.group(1))
                continue

            min_opt_match = OPTION_MIN_OPT_REGEX.match(option)
            if min_opt_match:
                item_filter.life = int(min_opt_match.group(1))
                continue

            max_price_match = OPTION_MAX_PRICE_REGEX.match(option)
            if max_price_match:
                if max_price_match.group(3).lower() == "bon":
                    item_filter.price_type = MarketItemPriceType.BONS
                    item_filter.price = float(max_price_match.group(1)) * (1000 ** (max_price_match.group(3).count("k") - 2))
                else:
                    item_filter.price_type = MarketItemPriceType.ZEN
                    item_filter.price = int(max_price_match.group(1))

                continue

            await ctx.channel.send(f"Unknown option or format: {option}")
            return

        if ctx.guild.id not in self.filters.keys():
            self.filters[ctx.guild.id] = {}

        if ctx.author.id not in self.filters[ctx.guild.id].keys():
            self.filters[ctx.guild.id][ctx.author.id] = []

        self.filters[ctx.guild.id][ctx.author.id].append(item_filter)
        await self.config.member(ctx.author).watchlist.set([f.to_dict() for f in self.filters[ctx.guild.id][ctx.author.id]])

        filter_id += 1
        await self.config.member(ctx.author).filter_id.set(filter_id)

        await ctx.channel.send(f"{ctx.author.mention} Added filter `{filter_id}`.")
        

    @bless.command()
    async def filters(self, ctx):
        channel = await self.config.guild(ctx.guild).notification_channel()
        if channel == 0:
            await ctx.channel.send(f"This server's admin has not set a channel for notifications. See `{ctx.prefix}help bless setchannel`.")
            return

        if not self.filters or not self.filters[ctx.guild.id] or not self.filters[ctx.guild.id][ctx.author.id]:
            await ctx.channel.send(f"{ctx.author.mention} You have not registered any item filters.")
            return
        
        for page in pagify("\n".join([str(f) for f in self.filters[ctx.guild.id][ctx.author.id]]), page_length=1993):
            await ctx.channel.send(f"```py\n{page}```")

    @bless.command()
    async def unwatch(self, ctx, id : int):
        channel = await self.config.guild(ctx.guild).notification_channel()
        if channel == 0:
            await ctx.channel.send(f"This server's admin has not set a channel for notifications. See `{ctx.prefix}help bless setchannel`.")
            return

        if not self.filters or not self.filters[ctx.guild.id] or not self.filters[ctx.guild.id][ctx.author.id]:
            await ctx.channel.send(f"{ctx.author.mention} Filter `{id}` not found.")
            return

        for i in range(0, len(self.filters[ctx.guild.id][ctx.author.id])):
            if self.filters[ctx.guild.id][ctx.author.id][i].id == id:
                del self.filters[ctx.guild.id][ctx.author.id][i]
                await self.config.member(ctx.author).watchlist.set([f.to_dict() for f in self.filters[ctx.guild.id][ctx.author.id]])

                await ctx.channel.send(f"{ctx.author.mention} Filter `{id}` removed.")
                return

        await ctx.channel.send(f"{ctx.author.mention} Filter `{id}` not found.")

    @bless.command()
    async def setchannel(self, ctx, channel : discord.TextChannel):
        await self.config.guild(ctx.guild).notification_channel.set(channel.id)

        await ctx.channel.send(f"{ctx.author.mention} Notification channel set to {channel.mention}.")

    @bless.command()
    async def channel(self, ctx):
        notification_channel = await self.config.guild(ctx.guild).notification_channel()
        await ctx.channel.send(f"{ctx.author.mention} Notification channel set to {ctx.guild.get_channel(notification_channel).mention}.")

    def cog_unload(self):
        self.watch_auctions.cancel()