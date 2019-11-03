# Procedurally generated duel cog for Red-DiscordBot
# Copyright (c) 2016 Caleb Jonson
# Idea and rule system courtesy of Axas
# Additional moves suggested by OrdinatorStouff

import asyncio
import discord
from functools import partial
import math
import os
import random
import tabulate
import re

from redbot.core import checks, commands, Config, bank
from redbot.core.utils.chat_formatting import error, pagify, warning

from .items import DEFAULT_BODY_ARMORS, DEFAULT_BOOTS, DEFAULT_GLOVES, \
                  DEFAULT_HEALING_ITEMS, DEFAULT_HELMETS, DEFAULT_PANTS, \
                  DEFAULT_SHOULDERS, DEFAULT_WEAPONS, ARMOR_PIECES, \
                  ARMOR_PIECE_TO_BODY_PARTS, DEFAULT_EQUIPPED, DEFAULT_ITEMS

__version__ = '2.0.0'


# Constants
TARGET_SELF = 'self'
TARGET_OTHER = 'target'

HR_STATS = {
    'name': 'Item',
    'damage': 'Damage',
    'healing': 'Healing',
    'armor': 'Armor',
    'cost': 'Cost',
    'crit_chance': 'Crit Chance',
    'hit_chance': 'Hit Chance',
    'low': 'Low',
    'high': 'High',
    'verb': 'Verb',
    'preposition': 'Preposition',
    'template': 'Template'
}

MAX_ROWS_PER_CATEGORY = {
    'weapon': 12,
    'body_armor': 15,
    'gloves': 15,
    'boots': 15,
    'shoulders': 15,
    'pants': 15,
    'helmet': 15,
    'healing_item': 15
}

MAX_ROWS_PER_CATEGORY_EX = {
    'weapon': 8,
    'body_armor': 15,
    'gloves': 15,
    'boots': 15,
    'shoulders': 15,
    'pants': 15,
    'helmet': 15,
    'healing_item': 5
}

ITEM_FIELD_TYPES = {
    'low': int,
    'high': int,
    'crit_chance': float,
    'hit_chance': float,
    'name': str,
    'template': str,
    'verb': str,
    'preposition': str,
    'cost': int,
    'armor': int
}

EXPERIENCE_PER_LEVEL = {
    1: 100,
    2: 200,
    3: 350,
    4: 500,
    5: 700,
    6: 900,
    7: 1150,
    8: 1400,
    9: 1700,
    10: 2000
}

EDIT_ITEM_REGEX = re.compile(r'^([^,]+),([^,]+),([^,]+)$')
ADD_SLOT_REGEXES = {
    # name,cost,low,high,crit_chance,hit_chance,verb,preposition
    'weapon': re.compile(r'^([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+),([^,]+)$'),
    # name,cost,armor
    'helmet': re.compile(r'^([^,]+),([^,]+),([^,]+)$'),
    'gloves': re.compile(r'^([^,]+),([^,]+),([^,]+)$'),
    'boots': re.compile(r'^([^,]+),([^,]+),([^,]+)$'),
    'shoulders': re.compile(r'^([^,]+),([^,]+),([^,]+)$'),
    'body_armor': re.compile(r'^([^,]+),([^,]+),([^,]+)$'),
    # name,cost,low,high,template
    'healing_item': re.compile(r'^([^,]+),([^,]+),([^,]+),([^,]+),(.+)$')
}

def indicatize(w):
    if w[-2:] == 'ch' or w[-2:] == 'sh' or w[-2:] == 'ss' or w[-1] == 'x' or w[-1] == 'z':
        w += 'es'
    elif w[-1] == 'y':
        w = w[:-1] + 'ies'
    else:
        w += 's'

    return w


class Player:
    def __init__(self, cog, member, items, initial_hp):
        self.hp = initial_hp
        self.member = member
        self.mention = member.mention
        self.cog = cog
        self.weapon = items['weapon']
        self.armor = {
            'helmet': items['helmet'],
            'body_armor': items['body_armor'],
            'pants': items['pants'],
            'shoulders': items['shoulders'],
            'gloves': items['gloves'],
            'boots': items['boots']
        }
        self.healing_item = items['healing_item']

    # Using object in string context gives (nick)name
    def __str__(self):
        return self.member.display_name

    # helpers for stat functions
    async def _set_stat(self, stat, num):
        stats = await self.cog._get_stats(self)
        stats[stat] = num
        await self.cog._set_stats(self, stats)

    async def _get_stat(self, stat):
        stats = await self.cog._get_stats(self)
        return stats[stat]

    async def get_wins(self):
        return await self._get_stat('wins')

    async def set_wins(self, num):
        await self._set_stat('wins', num)

    async def get_losses(self):
        return await self._get_stat('losses')

    async def set_losses(self, num):
        await self._set_stat('losses', num)

    async def get_draws(self):
        return await self._get_stat('draws')

    async def set_draws(self, num):
        await self._set_stat('draws', num)


# TEMPLATES BEGIN
# {a} is attacker, {d} is defender/target, {o} is a randomly selected object,
# {v} is the verb associated with that object, {p} is a preposition associated
# with that verb, and {b} is a random body part.

ATTACK = "{a} {v} their {o} {p} {d}'s {b}!"
ATTACK_PROTECTED = "{a} attempts to {v} their {o} {p} {d}'s {b}, but they are completely protected by their {ap}!"
CRITICAL_ATTACK = "{a} {v} their {o} {p} {d}'s {b}! Critical hit!"
MISS = "{a} attempts to {v} their {o} {p} {d}'s {b}, but they miss!"
BOT = "{a} charges its laser aaaaaaaand... BZZZZZZT! {d} is now a smoking crater for daring to challenge the bot."

EQUIPPED = "```http\nWeapon: {w}\nHelmet: {h}\nBody armor: {a}\nPants: {p}\nShoulders: {s}\nGloves: {g}\nBoots: {b}\nHealing item: {heal}```"

HITS = ['deal', 'hit for']
RECOVERS = ['recover', 'gain', 'heal']

# TEMPLATES END

# Weights of distribution for biased selection of moves
WEIGHTED_MOVES = {'ATTACK': 1, 'HEAL': 0.1}


class RPG(commands.Cog):
    def __init__(self):
        self.underway = set()
        self.config = Config.get_conf(self, identifier=134621854878007299)
        default_member_config = {
            'stats': {
                'wins': 0,
                'losses': 0,
                'draws': 0
            },
            'equipped': DEFAULT_EQUIPPED,
            'inventory': [],
            'level': 1,
            'experience': 0
        }
        default_guild_config = {
            'protected': [],
            'self_protect': False,
            'edit_posts': False,
            'items': DEFAULT_ITEMS,
            'initial_hp': 20,
            'max_rounds': 10,
            'currency_per_win': 10
        }
        self.config.register_member(**default_member_config)
        self.config.register_guild(**default_guild_config)


    @commands.guild_only()
    @commands.group(name="protect", invoke_without_command=True)
    async def _protect(self, ctx, user: discord.Member = None):
        """
        Manage the protection list (adds items)
        """

        if ctx.invoked_subcommand is None and user is not None:
            await ctx.invoke(self._protect_user, user)
            return

        await ctx.send_help()


    @_protect.command(name="me")
    async def _protect_self(self, ctx):
        """
        Adds you to the duel protection list
        """

        server = ctx.message.guild
        self_protect = await self.config.guild(server).self_protect()
        author = ctx.message.author

        if await self.is_protected(author, member_only=True):
            await ctx.send("You're already in the protection list.")
            return
        elif self_protect is False:
            await ctx.send('Sorry, self-protection is currently disabled.')
            return
        elif type(self_protect) is int:
            if not await bank.can_spend(author, self_protect):
                await ctx.send("You don't have %i credits to spend." % self_protect)
                return

            try:
                await bank.withdraw_credits(author, self_protect)
            except Exception:
                await ctx.send(error("Transaction failed. Report to bot owner!"))
                return

        if await self.protect_common(author, True):
            await ctx.send("You have been successfully added to the protection list.")
        else:
            await ctx.send("Something went wrong adding you to the protection list.")


    @checks.mod_or_permissions(administrator=True)
    @_protect.command(name="user")
    async def _protect_user(self, ctx, user: discord.Member):
        """
        Adds a member to the protection list
        """

        if await self.protect_common(user, True):
            await ctx.send("%s has been successfully added to the protection list." % user.display_name)
        else:
            await ctx.send("%s is already in the protection list." % user.display_name)


    @checks.admin_or_permissions(administrator=True)
    @_protect.command(name="role")
    async def _protect_role(self, ctx, role: discord.Role):
        """
        Adds a role to the protection list
        """

        if await self.protect_common(role, True):
            await ctx.send("The %s role has been successfully added to the protection list." % role.name)
        else:
            await ctx.send("The %s role is already in the protection list." % role.name)


    @commands.guild_only()
    @commands.group(name="unprotect", invoke_without_command=True)
    async def _unprotect(self, ctx, user: discord.Member = None):
        """
        Manage the protection list (removes items)
        """

        if ctx.invoked_subcommand is None and user is not None:
            await ctx.invoke(self._unprotect_user, user)
            return

        await ctx.send_help()


    @checks.mod_or_permissions(administrator=True)
    @_unprotect.command(name="user")
    async def _unprotect_user(self, ctx, user: discord.Member):
        """
        Removes a member from the duel protection list
        """

        if await self.protect_common(user, False):
            await ctx.send("%s has been successfully removed from the protection list." % user.display_name)
        else:
            await ctx.send("%s is not in the protection list." % user.display_name)


    @checks.admin_or_permissions(administrator=True)
    @_unprotect.command(name="role")
    async def _unprotect_role(self, ctx, role: discord.Role):
        """
        Removes a role from the duel protection list
        """

        if await self.protect_common(role, False):
            await ctx.send("The %s role has been successfully removed from the protection list." % role.name)
        else:
            await ctx.send("The %s role is not in the protection list." % role.name)


    @_unprotect.command(name="me")
    async def _unprotect_self(self, ctx):
        """
        Removes you from the duel protection list
        """

        if await self.protect_common(ctx.message.author, False):
            await ctx.send("You have been removed from the protection list.")
        else:
            await ctx.send("You aren't in the protection list.")


    @commands.guild_only()
    @commands.command(name="protected", aliases=['protection'])
    async def _protection(self, ctx):
        """
        Displays the duel protection list
        """

        server = ctx.message.guild
        duelists = await self.config.guild(server).all()
        member_list = duelists["protected"]
        fmt = partial(self.format_display, server)

        if member_list:
            name_list = map(fmt, member_list)
            name_list = ["**Protected users and roles:**"] + sorted(name_list)
            delim = '\n'

            for page in pagify(delim.join(name_list), delims=[delim], escape_mass_mentions=True):
                await ctx.send(page)
        else:
            await ctx.send("The list is currently empty, add users or roles with `%sprotect` first." % ctx.prefix)


    @commands.guild_only()
    @commands.group(name="duels", invoke_without_command=True)
    async def _duels(self, ctx):
        """
        Duel leaderboards
        """

        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._duels_list)


    @_duels.command(name="list")
    @commands.cooldown(2, 60, discord.ext.commands.BucketType.user)
    async def _duels_list(self, ctx, top: int = 10):
        """
        Shows the duel leaderboard, defaults to top 10
        """

        server = ctx.message.guild
        member_configs = await self.config.all_members(server)

        if top < 1:
            top = 10

        def sort_wins(kv):
            _, v = kv
            return v['stats']['wins'] - v['stats']['losses']

        def stat_filter(kv):
            _, config = kv

            if type(config['stats']) is not dict:
                return False

            if config['stats']['wins'] == 0 and config['stats']['losses'] == 0 and config['stats']['draws'] == 0:
                return False

            return True

        # filter out extra data, TODO: store protected list seperately
        duel_stats = filter(stat_filter, member_configs.items())
        duels_sorted = sorted(duel_stats, key=sort_wins, reverse=True)

        if not duels_sorted:
            await ctx.send('No records to show.')
            return

        if len(duels_sorted) < top:
            top = len(duels_sorted)

        topten = duels_sorted[:top]
        place = 1
        members = {uid: server.get_member(uid) for uid, _ in topten}  # only look up once each
        names = {uid: m.display_name for uid, m in members.items()}
        header = ['#', 'Name', 'wins', 'losses', 'draws']
        table_rows = []
        msg = ''
        for uid, config in topten:
            table_rows.append([place, names[uid], config['stats']['wins'], config['stats']['losses'], config['stats']['draws']])
            place += 1

        msg = f'```py\n{tabulate.tabulate(table_rows, headers=header, tablefmt="fancy_grid")}```'
        if len(msg) < 1985:
            await ctx.send(msg)
        else:
            await ctx.send("The leaderboard is too big to be displayed. Try with a lower <top> parameter.")


    @commands.guild_only()
    @commands.command(name="duel")
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def _duel(self, ctx, user: discord.Member):
        """
        Duel another player
        """

        author = ctx.author
        server = ctx.guild
        channel = ctx.channel
        guild_config = await self.config.guild(server).all()
        currency = await bank.get_currency_name(ctx.guild)

        abort = True

        if channel.id in self.underway:
            await ctx.send("There's already a duel underway in this channel!")
        elif user == author:
            await ctx.send("You can't duel yourself, silly!")
        elif await self.is_protected(author):
            await ctx.send("You can't duel anyone while you're on the protected users list.")
        elif await self.is_protected(user):
            await ctx.send("%s is on the protected users list." % user.display_name)
        else:
            abort = False

        if abort:
            bucket = ctx.command._buckets.get_bucket(ctx.message)
            bucket._tokens += 1  # Sorry, Danny
            return

        p1_items = await self.get_equipped_full(author, ctx.guild)
        p2_items = await self.get_equipped_full(user, ctx.guild)
        p1 = Player(self, author, p1_items, guild_config['initial_hp'])
        p2 = Player(self, user, p2_items, guild_config['initial_hp'])
        self.underway.add(channel.id)

        try:
            order = [(p1, p2), (p2, p1)]
            random.shuffle(order)
            msg = ["%s challenges %s to a duel!" % (p1, p2)]
            msg.append("\nBy a coin toss, %s will go first." % order[0][0])
            msg_object = await ctx.send('\n'.join(msg))
            for i in range(guild_config['max_rounds']):
                if p1.hp <= 0 or p2.hp <= 0:
                    break
                for attacker, defender in order:
                    if p1.hp <= 0 or p2.hp <= 0:
                        break

                    if attacker.member == ctx.me:
                        move_msg = self.generate_action(attacker, defender, guild_config['initial_hp'], 'BOT')
                    else:
                        move_msg = self.generate_action(attacker, defender, guild_config['initial_hp'])

                    if guild_config['edit_posts']:
                        new_msg = '\n'.join(msg + [move_msg])
                        if len(new_msg) < 2000:
                            await self._robust_edit(msg_object, content=new_msg)
                            msg = msg + [move_msg]
                            await asyncio.sleep(1)
                            continue

                    msg_object = await ctx.send(move_msg)
                    msg = [move_msg]
                    await asyncio.sleep(1)

            if p1.hp != p2.hp:
                victor = p1 if p1.hp > p2.hp else p2
                loser = p1 if p1.hp < p2.hp else p2
                victor_wins = await victor.get_wins()
                loser_losses = await loser.get_losses()
                await victor.set_wins(victor_wins + 1)
                await loser.set_losses(loser_losses + 1)
                await bank.deposit_credits(victor.member, guild_config['currency_per_win'])
                msg = f"After {i + 1} rounds, {victor.mention} wins with {victor.hp} HP! They have been awarded with {guild_config['currency_per_win']} {currency}!"
                msg += '\nStats: '

                for p, end in ((victor, '; '), (loser, '.')):
                    msg += f'{p} has {await p.get_wins()} wins, {await p.get_losses()} losses, {await p.get_draws()} draws{end}'
            else:
                victor = None

                for p in [p1, p2]:
                    player_draws = await p.get_draws()
                    await p.set_draws(player_draws + 1)

                msg = 'After %d rounds, the duel ends in a tie!' % (i + 1)

            await ctx.send(msg)
        except Exception:
            raise
        finally:
            self.underway.remove(channel.id)


    @commands.guild_only()
    @commands.group(name="shop", invoke_without_command=True)
    async def _shop(self, ctx, category: str = None):
        """
        Item purchasing/selling
        """

        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._shop_list, category)
            return

        await ctx.send_help()


    @_shop.command(name="list")
    async def _shop_list(self, ctx, category: str = None):
        """
        Shows all items (if no category was provided) currently in the shop
        """

        items = await self.config.guild(ctx.guild).items()

        def sort_cost(item):
            return item['cost']

        if category != None:
            if category not in items.keys():
                await ctx.send(f"Valid item categories: {', '.join(items.keys())}")
                return

            final_msg = ''
            items = self.to_shop_items(items[category], category)
            table_rows = []
            for item in sorted(items, key=sort_cost):
                table_rows.append(self.to_shop_row(item, category))
                if len(table_rows) == MAX_ROWS_PER_CATEGORY[category]:
                    final_msg += f'```py\n{tabulate.tabulate(table_rows, headers = self.generate_header(category), tablefmt="fancy_grid")}```'
                    table_rows = []

            if len(table_rows) != 0:
                final_msg += f'```py\n{tabulate.tabulate(table_rows, headers = self.generate_header(category), tablefmt="fancy_grid")}```'

            for page in pagify(final_msg, delims=['```py'], page_length=1992):
                await ctx.send(page)

            return

        final_msg = ''
        for category in items.keys():
            items[category] = self.to_shop_items(items[category], category)
            table_rows = []
            for item in sorted(items[category], key=sort_cost):
                table_rows.append(self.to_shop_row(item, category))
                if len(table_rows) == MAX_ROWS_PER_CATEGORY[category]:
                    final_msg += f'```py\n{tabulate.tabulate(table_rows, headers = self.generate_header(category), tablefmt="fancy_grid")}```'
                    table_rows = []

            if len(table_rows) != 0:
                final_msg += f'```py\n{tabulate.tabulate(table_rows, headers = self.generate_header(category), tablefmt="fancy_grid")}```'

        for page in pagify(final_msg, delims=['```py'], page_length=1992):
            await ctx.send(page)


    @_shop.command(name="buy")
    async def _shop_buy(self, ctx, *, item_name):
        """
        Purchases an item and adds it to your inventory
        """

        currency = await bank.get_currency_name(ctx.guild)
        inventory = await self.config.member(ctx.author).inventory()

        if await self.item_equipped_by_member(ctx.author, item_name) or await self.item_in_member_inventory(ctx.author, item_name) or item_name in DEFAULT_EQUIPPED.values():
            await ctx.send('You already have that item in your inventory!')
            return

        _, item = await self.get_item(ctx.guild, item_name)
        if item == None:
            await ctx.send(f'Item **{item_name}** not found in shop!')
            return

        try:
            await bank.withdraw_credits(ctx.author, item['cost'])
        except ValueError:
            await ctx.send(f'You do not have enough {currency} to buy a **{item_name}**!')
            return

        inventory.append(item_name)
        await self.config.member(ctx.author).inventory.set(sorted(inventory))
        await ctx.send(f'You successfully bought a **{item_name}**! Equip it using `{ctx.prefix}inventory equip {item_name}`.')

    @_shop.command(name="sell")
    async def _shop_sell(self, ctx, *, item_name):
        """
        Sells an item from your inventory for half its purchase cost (unequips it, if it was equipped prior to selling)
        """

        slot, item = await self.get_item(ctx.guild, item_name)
        inventory = await self.get_inventory(ctx.author)
        equipped = await self.get_equipped_slots(ctx.author)
        currency = await bank.get_currency_name(ctx.guild)

        if item == None:
            await ctx.send("That item does not exist!")
            return

        if item_name == DEFAULT_EQUIPPED[slot]:
            await ctx.send('That item cannot be sold!')
            return

        if item_name not in inventory and equipped[slot] != item_name:
            await ctx.send(f"You don't own a **{item_name}**!")
            return

        if equipped[slot] == item_name:
            equipped[slot] = DEFAULT_EQUIPPED[slot]
            await self.config.member(ctx.author).equipped.set(equipped)
        elif item_name in inventory:
            inventory.remove(item_name)
            await self.config.member(ctx.author).inventory.set(inventory)

        resell_value = int(item['cost'] / 2)
        await bank.deposit_credits(ctx.author, resell_value)
        await ctx.send(f'**{item_name}** sold for {resell_value} {currency}!')


    @commands.guild_only()
    @commands.group(name="inventory", aliases=['inv'], invoke_without_command=True)
    async def _inventory(self, ctx):
        """
        Inventory management
        """

        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._inventory_list)


    @_inventory.command(name="list")
    async def _inventory_list(self, ctx):
        """
        Shows your equipped items and your inventory
        """

        inventory = await self.get_inventory(ctx.author)
        equipped = await self.get_equipped_slots(ctx.author)
        inventory_str = 'None' if not len(inventory) else ', '.join(inventory)
        msg = f"{ctx.author.display_name}'s equipped items:\n{EQUIPPED.format(w = equipped['weapon'], h = equipped['helmet'], a = equipped['body_armor'], p = equipped['pants'], g = equipped['gloves'], b = equipped['boots'], s = equipped['shoulders'], heal = equipped['healing_item'])}"
        msg += f"{ctx.author.display_name}'s inventory:\n```{inventory_str}```"
        await ctx.send(msg)


    @_inventory.command(name="equip")
    async def _inventory_equip(self, ctx, *, item_name):
        """
        Equips an item from your inventory
        """

        inventory = await self.get_inventory(ctx.author)
        equipped = await self.get_equipped_slots(ctx.author)
        slot, item = await self.get_item(ctx.guild, item_name)

        if item == None:
            await ctx.send("That item does not exist!")
            return

        if item_name == equipped[slot]:
            await ctx.send('That item is already equipped!')
            return

        if item_name not in inventory and item_name not in DEFAULT_EQUIPPED.values():
            await ctx.send(f"You don't own a **{item_name}**!")
            return

        if equipped[slot] != DEFAULT_EQUIPPED[slot]:
            inventory.append(equipped[slot])

        if item_name != DEFAULT_EQUIPPED[slot]:
            inventory.remove(item_name)

        equipped[slot] = item_name
        await self.config.member(ctx.author).equipped.set(equipped)
        await self.config.member(ctx.author).inventory.set(inventory)
        await ctx.send(f"**{item_name}** equipped!")


    @_inventory.command(name="unequip")
    async def _inventory_unequip(self, ctx, slot):
        """
        Unequips a slot and places the item in that slot in your inventory
        """

        if slot not in DEFAULT_EQUIPPED.keys():
            await ctx.send(f"Invalid slot name! Valid slot names:\n```{', '.join(DEFAULT_EQUIPPED.keys())}```")
            return

        inventory = await self.get_inventory(ctx.author)
        equipped = await self.get_equipped_slots(ctx.author)
        item_name = equipped[slot]

        if equipped[slot] == DEFAULT_EQUIPPED[slot]:
            await ctx.send('Your currently equipped item in that slot cannot be unequipped!')
            return

        inventory.append(equipped[slot])
        equipped[slot] = DEFAULT_EQUIPPED[slot]
        await self.config.member(ctx.author).equipped.set(equipped)
        await self.config.member(ctx.author).inventory.set(inventory)
        await ctx.send(f"**{item_name}** unequipped!")


    @commands.guild_only()
    @checks.admin_or_permissions(administrator=True)
    @commands.group(name="rpgset", invoke_without_command=True)
    async def _rpgset(self, ctx):
        """
        Manage cog settings
        """

        if ctx.invoked_subcommand == None:
            guild_config = await self.config.guild(ctx.guild).all()
            del guild_config['items']
            del guild_config['protected']
            msg = ''
            for k, v in guild_config.items():
                msg += f"{k}: {v}\n"

            for page in pagify(msg, page_length=1988):
                await ctx.send(f"```http\n{page}```")
            return


    @_rpgset.command(name="initial_hp")
    async def _rpgset_initial_hp(self, ctx, initial_hp: int = None):
        """
        Change the HP players start with at the beginning of every battle
        """

        guild_config = await self.config.guild(ctx.guild).all()
        if initial_hp == None:
            await ctx.send(f"```http\ninitial_hp: {guild_config['initial_hp']}```")
            return

        guild_config['initial_hp'] = initial_hp
        await self.config.guild(ctx.guild).set(guild_config)
        await ctx.send(f"`initial_hp` set to `{initial_hp}`")


    @_rpgset.command(name="max_rounds")
    async def _rpgset_max_rounds(self, ctx, max_rounds: int = None):
        """
        Change the maximum number of rounds before a duel is interrupted and a winner is announced
        """

        guild_config = await self.config.guild(ctx.guild).all()
        if max_rounds == None:
            await ctx.send(f"```http\nmax_rounds: {guild_config['max_rounds']}```")
            return

        guild_config['max_rounds'] = max_rounds
        await self.config.guild(ctx.guild).set(guild_config)
        await ctx.send(f"`max_rounds` set to `{max_rounds}`")


    @_rpgset.command(name="edit_posts")
    async def _rpgset_edit_posts(self, ctx, edit_posts: bool = None):
        """
        Edit duel messages in-place instead of posting each move seperately
        """

        guild_config = await self.config.guild(ctx.guild).all()
        if edit_posts == None:
            await ctx.send(f"```http\nedit_posts: {guild_config['edit_posts']}```")
            return

        guild_config['edit_posts'] = edit_posts
        await self.config.guild(ctx.guild).set(guild_config)
        await ctx.send(f"`edit_posts` set to `{edit_posts}`")


    @_rpgset.command(name="self_protect")
    async def _rpgset_self_protect(self, ctx, self_protect: str = None):
        """
        Enable, disable, or set the price of self-protection

        Valid options: "disable", "off", "false", "no", "free", or any number 0 or greater.
        """

        guild_config = await self.config.guild(ctx.guild).all()

        if self_protect == None:
            await ctx.send(f"```http\nself_protect: {guild_config['self_protect']}```")
            return

        self_protect = self_protect.lower().strip(' "`')

        if self_protect in ('disable', 'no', 'n', 'false', 'f', 'off'):
            self_protect = False
        elif self_protect in ('free', '0'):
            self_protect = True
        elif self_protect.isdecimal():
            self_protect = int(self_protect)
        else:
            await ctx.send_help()
            return

        guild_config['self_protect'] = self_protect
        await self.config.guild(ctx.guild).set(guild_config)
        await ctx.send(f"`self_protect` set to `{self_protect}`")


    @_rpgset.command(name="currency_per_win")
    async def _rpgset_currency_per_win(self, ctx, currency_per_win: int = None):
        """
        Change the amount of currency that is awarded to the winner after every duel
        """

        guild_config = await self.config.guild(ctx.guild).all()
        if currency_per_win == None:
            await ctx.send(f"```http\ncurrency_per_win: {guild_config['currency_per_win']}```")
            return

        guild_config['currency_per_win'] = currency_per_win
        await self.config.guild(ctx.guild).set(guild_config)
        await ctx.send(f"`currency_per_win` set to `{currency_per_win}`")


    @_rpgset.command(name="reset_players")
    async def _rpgset_reset_players(self, ctx):
        """
        Clears duel scores and equipment without resetting protection or editmode
        """

        await self.config.clear_all_members(ctx.guild)
        await ctx.send('Players reset.')


    @commands.guild_only()
    @checks.admin_or_permissions(administrator=True)
    @commands.group(name="items", invoke_without_command=True)
    async def _items(self, ctx, category: str = None):
        """
        Edit/add/delete duel items
        """

        if ctx.invoked_subcommand == None:
            await ctx.invoke(self._items_list, category)
            return

        await ctx.send_help()

    @_items.command(name="list")
    async def _items_list(self, ctx, category: str = None):
        """
        Lists all items for in a given category, or all if no category is given.

        Valid categories: `helmet`, `body_armor`, `pants`, `shoulders`, `gloves`, `boots`, `healing_item`, `weapon`
        """

        items = await self.config.guild(ctx.guild).items()
        if category != None:
            if category not in items.keys():
                await ctx.send(f"Valid item categories: {', '.join(items.keys())}")
                return

            final_msg = ''
            table_rows = []
            for item in items[category]:
                table_rows.append(item.values())
                if len(table_rows) == MAX_ROWS_PER_CATEGORY_EX[category]:
                    final_msg += f'```py\n{tabulate.tabulate(table_rows, headers = items[category][0].keys(), tablefmt="fancy_grid")}```'
                    table_rows = []

            if len(table_rows) != 0:
                final_msg += f'```py\n{tabulate.tabulate(table_rows, headers = items[category][0].keys(), tablefmt="fancy_grid")}```'

            for page in pagify(final_msg, delims=['```py'], page_length=1992):
                await ctx.send(page)

            return

        final_msg = ''
        for category in items.keys():
            table_rows = []
            for item in items[category]:
                table_rows.append(item.values())
                if len(table_rows) == MAX_ROWS_PER_CATEGORY_EX[category]:
                    final_msg += f'```py\n{tabulate.tabulate(table_rows, headers = items[category][0].keys(), tablefmt="fancy_grid")}```'
                    table_rows = []

            if len(table_rows) != 0:
                final_msg += f'```py\n{tabulate.tabulate(table_rows, headers = items[category][0].keys(), tablefmt="fancy_grid")}```'

        for page in pagify(final_msg, delims=['```py'], page_length=1992):
            await ctx.send(page)

        return


    @_items.command(name="add")
    async def _items_add(self, ctx, slot: str, *, item):
        """
        Add an item to this servers list of items

        Valid slots: `helmet`, `body_armor`, `pants`, `shoulders`, `gloves`, `boots`, `healing_item`, `weapon`

        Item formats:
         - helmet, body_armor, pants, shoulders, gloves, boots - `name,cost,armor`

           Example: `[p]items add body_armor diamond breastplate,1000,8`

         - weapon - `name,cost,minimum damage,maximum damage,critical chance,hit chance,verb,preposition`

           Example: `[p]items add weapon dick gun,1000,10,15,0.2,0.9,fire,at`

         - healing_item - `name,cost,minimum healing,maximum healing,template`

           Template macros: {a} - attacker, {d} - defender, {o} - item name

           Example: `[p]items add healing_item vampire teeth,1000,8,14,{a} gets hungry and decides to take a bite out of {d}'s neck using his {o}!`
        """

        if slot not in DEFAULT_ITEMS.keys():
            await ctx.send(f"Invalid slot name! Valid slot names: {', '.join(DEFAULT_ITEMS.keys())}")
            return

        match = re.match(ADD_SLOT_REGEXES[slot], item)
        if not match:
            await ctx.send(f"Invalid item format! Type `{ctx.prefix}help items add` for more information on the format of this command.")
            return

        items = await self.config.guild(ctx.guild).items()
        item_name, cost = match.group(1, 2)

        try:
            cost = int(cost)
        except ValueError:
            await ctx.send(f"`cost` must be an integer!")
            return

        if cost < 0:
            cost = 0

        _, item = await self.get_item(ctx.guild, item_name)

        if item != None:
            await ctx.send(f'Item **{item_name}** already exists! Use `{ctx.prefix}items edit` if you want to modify it.')
            return

        if slot == 'weapon':
            low, high, crit_chance, hit_chance, verb, preposition = match.group(3, 4, 5, 6, 7, 8)

            try:
                low = int(low)
            except ValueError:
                await ctx.send(f"`low` must be an integer!")
                return

            if low < 0:
                low = 0

            try:
                high = int(high)
            except ValueError:
                await ctx.send(f"`high` must be an integer!")
                return

            if high < 0:
                high = 0

            try:
                crit_chance = float(crit_chance)
            except ValueError:
                await ctx.send(f"`crit_chance` must be a floating-point number!")
                return

            if crit_chance > 1:
                crit_chance = 1.0
            elif crit_chance < 0:
                crit_chance = 0.0

            try:
                hit_chance = float(hit_chance)
            except ValueError:
                await ctx.send(f"`hit_chance` must be an floating-point number!")

            if hit_chance > 1:
                hit_chance = 1.0
            elif hit_chance < 0:
                hit_chance = 0.0

            if low > high:
                low, high = high, low

            item = {
                'name': item_name,
                'cost': cost,
                'low': low,
                'high': high,
                'crit_chance': crit_chance,
                'hit_chance': hit_chance,
                'verb': verb,
                'preposition': preposition
            }

        elif slot == 'healing_item':
            low, high, template = match.group(3, 4, 5)

            if low > high:
                low, high = high, low

            try:
                low = int(low)
            except ValueError:
                await ctx.send(f"`low` must be an integer!")
                return

            if low < 0:
                low = 0

            try:
                high = int(high)
            except ValueError:
                await ctx.send(f"`high` must be an integer!")
                return

            if high < 0:
                high = 0

            item = {
                'name': item_name,
                'cost': cost,
                'low': low,
                'high': high,
                'template': template
            }

        else:
            armor = match.group(3)

            try:
                armor = int(armor)
            except ValueError:
                await ctx.send(f"`armor` must be an integer!")
                return

            if armor < 0:
                armor = 0

            item = {
                'name': item_name,
                'cost': cost,
                'armor': armor
            }

        items[slot].append(item)
        await self.config.guild(ctx.guild).items.set(items)
        await ctx.send(f"**{item_name}** successfully added to this server's items!")

    @_items.command(name="edit")
    async def _items_edit(self, ctx, *, edit):
        """
        Edit a property of an item

        Edit format: `item name,property,new value`

        `helmet`, `body_armor`, `shoulders`, `boots`, `gloves`, `pants` properties:
         * `name` - string
         * `cost` - integer number
         * `armor` - integer number

        `weapon` properties:
         * `name` - string
         * `cost` - integer number
         * `low` - integer number
         * `high` - integer number
         * `crit_chance` - floating point number between 0.0 and 1.0
         * `hit_chance` - floating point number between 0.0 and 1.0
         * `verb` - string
         * `preposition` - string

        `healing_item` properites:
         * `name` - string
         * `cost` - integer number
         * `low` - integer number
         * `high` - integer number
         * `template` - string. Refer to `[p]items add` for more information on healing item templates.

        Examples:
        `[p]items edit iron cap,cost,200`
        `[p]items edit axe,name,huge axe`
        `[p]items edit nanites,high,10`
        """

        match = re.match(EDIT_ITEM_REGEX, edit)
        if not match:
            await ctx.send(f"Invalid edit format! Type `{ctx.prefix}items edit` for more information on the format of this command.")

        item_name, field, value = match.group(1, 2, 3)

        if item_name in DEFAULT_EQUIPPED.values():
            await ctx.send(f'Item `{item_name}` cannot be editted!')
            return

        _, item = await self.get_item(ctx.guild, item_name)
        if item == None:
            await ctx.send(f'Item `{item_name}` does not exist!')
            return

        try:
            value = ITEM_FIELD_TYPES[field](value)
        except ValueError:
            await ctx.send(f"Invalid value format! Type `{ctx.prefix}help items edit` for more information on item field formats.")
            return
        except KeyError:
            await ctx.send(f"Invalid field name! Check `{ctx.prefix}help items edit` for more information on item field names.")
            return

        await self.edit_item(ctx.guild, item_name, field, value)
        await ctx.send(f"`{field}` of `{item_name}` set to `{value}`.")


    @_items.command(name="delete")
    async def _items_delete(self, ctx, *, item_name):
        """
        Deletes an item and refunds all players that own that item for its full cost.
        """

        _, item = await self.get_item(ctx.guild, item_name)
        if item == None:
            await ctx.send(f'Item `{item_name}` does not exist!')
            return

        if item['name'] in DEFAULT_EQUIPPED.values():
            await ctx.send(f'Item `{item_name}` cannot be deleted!')
            return

        for member in ctx.guild.members:
            await self.refund_item(member, item)

        await self.delete_item(ctx.guild, item_name)
        await ctx.send(f'Item `{item_name}` deleted!')

    @_items.command(name="reset")
    async def _items_reset(self, ctx):
        """
        Resets this servers items to the default list of items.
        """

        await self.config.guild(ctx.guild).items.set(DEFAULT_ITEMS)
        await ctx.send('Items reset to default!')


    @commands.guild_only()
    @checks.admin_or_permissions(administrator=True)
    @commands.command(name="addexp")
    async def _addexp(self, ctx, amount: int, member: discord.Member = None):
        """
        Adds experience to a member (or yourself, if none specified).
        """

        member = ctx.author if member == None else member
        await ctx.send(f"Adding {amount} experience to {member.display_name}!")
        await self.add_experience(member, amount, ctx.channel)


    @commands.guild_only()
    @commands.command(name="level")
    async def _level(self, ctx, member: discord.Member = None):
        """
        Displays your (or another member's) experience, level and required experience to reach the next level.
        """

        member = ctx.author if member == None else member
        level, experience = await self.get_member_level(member)
        await ctx.send(f"{member.display_name}'s current level and experience:\n```http\nLevel: {level}\nExperience: {experience}\nExperience to next level: {EXPERIENCE_PER_LEVEL[level] - experience}```")


# UTILS BEGIN

    def format_display(self, server, id):
        if id.startswith('r'):
            role = discord.utils.get(server.roles, id=int(id[1:]))

            if role:
                return '@%s' % role.name
            else:
                return 'deleted role #%s' % id
        else:
            member = server.get_member(int(id))

            if member:
                return member.display_name
            else:
                return 'missing member #%s' % id


    async def is_protected(self, member: discord.Member, member_only=False) -> bool:
        protected = set(await self.config.guild(member.guild).protected())
        roles = set() if member_only else set('r' + str(r.id) for r in member.roles)
        return str(member.id) in protected or bool(protected & roles)


    async def protect_common(self, obj, protect=True):
        if not isinstance(obj, (discord.Member, discord.Role)):
            raise TypeError('Can only pass member or role objects.')

        server = obj.guild
        id = ('r' if type(obj) is discord.Role else '') + str(obj.id)

        protected = await self.config.guild(server).protected()

        if protect == (id in protected):
            return False
        elif protect:
            protected.append(id)
        else:
            protected.remove(id)

        await self.config.guild(server).protected.set(protected)
        return True


    async def _set_stats(self, user, stats):
        await self.config.member(user.member).stats.set(stats)


    async def _get_stats(self, user):
        return await self.config.member(user.member).stats()


    async def get_inventory(self, member):
        inventory = await self.config.member(member).inventory()
        return inventory


    async def get_equipped(self, member):
        equipped = await self.config.member(member).equipped()
        return [i for i in equipped.values()]


    async def get_equipped_slots(self, member):
        equipped = await self.config.member(member).equipped()
        return equipped


    async def get_equipped_full(self, member, guild):
        equipped = await self.config.member(member).equipped()
        result = {}
        for slot, item_name in equipped.items():
            _, item = await self.get_item_ex(guild, item_name, slot)
            result[slot] = item
        return result


    async def get_item(self, guild, item_name):
        items = await self.config.guild(guild).items()
        for slot, category_items in items.items():
            for item in category_items:
                if item['name'] == item_name:
                    return slot, item

        return None, None


    async def get_item_ex(self, guild, item_name, slot = None):
        if slot == None:
            return self.get_item(guild, item_name)

        items = await self.config.guild(guild).items()
        for item in items[slot]:
            if item['name'] == item_name:
                return slot, item

        return None, None


    async def edit_item(self, guild, item_name, field, value):
        items = await self.config.guild(guild).items()
        configs = await self.config.all_members(guild)
        editted = False
        for slot, category_items in items.items():
            for item in category_items:
                if item['name'] == item_name:
                    item[field] = value
                    editted = True
                    break
            if editted:
                break

        if editted:
            await self.config.guild(guild).items.set(items)

        if field != 'name':
            return

        for user_id, config in configs.items():
            equipped = {}
            update = False
            for slot, slot_item in config['equipped'].items():
                if slot_item == item_name:
                    slot_item = value
                    update = True
                equipped[slot] = slot_item

            if update:
                member = guild.get_member(user_id)
                await self.config.member(member).equipped.set(equipped)

            inventory = []
            update = False
            for inventory_item in config['inventory']:
                if inventory_item == item_name:
                    inventory_item = value
                    update = True
                inventory.append(inventory_item)

            if update:
                member = guild.get_member(user_id)
                await self.config.member(member).inventory.set(inventory)


    async def delete_item(self, guild, item_name):
        items = await self.config.guild(guild).items()
        result = dict.fromkeys(items, [])
        for slot, slot_items in items.items():
            result[slot] = [i for i in slot_items if i['name'] != item_name]

        await self.config.guild(guild).items.set(result)


    async def refund_item(self, member, item):
        member_config = await self.config.member(member).all()
        count = 0
        for slot, item_name in member_config['equipped'].items():
            if item_name == item['name']:
                member_config['equipped'][slot] = DEFAULT_EQUIPPED[slot]
                count += 1
                break

        while item['name'] in member_config['inventory']:
            member_config['inventory'].remove(item['name'])
            count += 1

        if count > 0:
            await self.config.member(member).set(member_config)
            await bank.deposit_credits(member, item['cost'] * count)


    async def item_in_member_inventory(self, member, item_name):
        inventory = await self.get_inventory(member)
        for item in inventory:
            if item == item_name:
                return True

        return False


    async def item_equipped_by_member(self, member, item_name):
        equipped = await self.get_equipped(member)
        return item_name in equipped


    async def add_experience(self, member, experience, channel):
        member_config = await self.config.member(member).all()
        new_experience = member_config['experience'] + experience
        max_level = max(EXPERIENCE_PER_LEVEL.keys())
        while new_experience >= EXPERIENCE_PER_LEVEL[member_config['level']] and member_config['level'] < max_level:
            new_experience -= EXPERIENCE_PER_LEVEL[member_config['level']]
            member_config['level'] += 1
            await channel.send(f"{member.mention} has leveled up to {member_config['level']}!")

        member_config['experience'] = new_experience
        member_config['experience'] = min(member_config['experience'], EXPERIENCE_PER_LEVEL[max_level])
        member_config['experience'] = max(member_config['experience'], 0)

        await self.config.member(member).set(member_config)


    async def get_member_level(self, member):
        member_config = await self.config.member(member).all()
        return member_config['level'], member_config['experience']


    def generate_action(self, attacker, defender, initial_hp, move_cat=None):
        # Select move category
        if not move_cat:
            move_cat = weighted_choice(WEIGHTED_MOVES)

        armor_slot = random.choice(ARMOR_PIECES)
        bodypart = random.choice(ARMOR_PIECE_TO_BODY_PARTS[armor_slot])
        armor_piece_name = defender.armor[armor_slot]['name']
        verb = indicatize(attacker.weapon['verb'])
        preposition = ''
        obj = attacker.weapon['name']
        target = defender
        if move_cat == 'ATTACK':
            move = ATTACK
            hp_delta = min(0, -random.randint(attacker.weapon['low'], attacker.weapon['high']) + defender.armor[armor_slot]['armor'])
            preposition = attacker.weapon['preposition']
            if hp_delta == 0:
                move = ATTACK_PROTECTED
                verb = attacker.weapon['verb']
            elif attacker.weapon['hit_chance'] < random.random():
                move = MISS
                verb = attacker.weapon['verb']
                hp_delta = 0
            elif attacker.weapon['crit_chance'] >= random.random():
                move = CRITICAL_ATTACK
                hp_delta = hp_delta * 2 - defender.armor[armor_slot]['armor']
        elif move_cat == 'HEAL':
            move = attacker.healing_item['template']
            target = attacker
            hp_delta = random.randint(attacker.healing_item['low'], attacker.healing_item['high'])
            obj = attacker.healing_item['name']
        else:
            move = BOT
            hp_delta = -initial_hp * 64

        msg = move.format(a=attacker, d=defender, o=obj, v=verb, b=bodypart, p=preposition, ap=armor_piece_name)
        if hp_delta == 0:
            pass
        else:
            target.hp += hp_delta
            if hp_delta > 0:
                s = random.choice(RECOVERS)
                msg += ' They %s %d HP (%d)' % (s, abs(hp_delta), target.hp)
            elif hp_delta < 0:
                s = random.choice(HITS)
                msg += ' They %s %d damage (%d)' % (s, abs(hp_delta), target.hp)

        return msg


    async def _robust_edit(self, msg, content=None, embed=None):
        try:
            await msg.edit(content=content, embed=embed)
        except discord.errors.NotFound:
            await msg.channel.send(content=content, embed=embed)
        except Exception:
            raise


    def to_shop_items(self, items, category):
        result = []
        if category == 'weapon':
            for item in items:
                item['damage'] = f"{item['low']}-{item['high']}"
                result.append(item)

            return result

        if category == 'healing_item':
            for item in items:
                item['healing'] = f"{item['low']}-{item['high']}"
                result.append(item)

            return result

        return items


    def to_shop_row(self, item, category):
        if category == 'weapon':
            return [item['name'], item['damage'], str(int(item['hit_chance'] * 100)) + '%', str(int(item['crit_chance'] * 100)) + '%', item['cost']]

        if category == 'healing_item':
            return [item['name'], item['healing'], item['cost']]

        return [item['name'], item['armor'], item['cost']]


    def generate_header(self, category):
        if category == 'weapon':
            return [HR_STATS['name'], HR_STATS['damage'], HR_STATS['hit_chance'], HR_STATS['crit_chance'], HR_STATS['cost']]

        if category == 'healing_item':
            return [HR_STATS['name'], HR_STATS['healing'], HR_STATS['cost']]

        return [HR_STATS['name'], HR_STATS['armor'], HR_STATS['cost']]

# UTILS END

def weighted_choice(choices):
    total = sum(w for c, w in choices.items())
    r = random.uniform(0, total)
    upto = 0

    for c, w in choices.items():
        if upto + w >= r:
            return c

        upto += w
