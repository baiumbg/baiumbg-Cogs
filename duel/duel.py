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

from redbot.core import checks, commands, Config, bank
from redbot.core.utils.chat_formatting import error, pagify, warning

from .items import DEFAULT_BODY_ARMORS, DEFAULT_BOOTS, DEFAULT_GLOVES, \
                  DEFAULT_HEALING_ITEMS, DEFAULT_HELMETS, DEFAULT_PANTS, \
                  DEFAULT_SHOULDERS, DEFAULT_WEAPONS, ARMOR_PIECES, \
                  ARMOR_PIECE_TO_BODY_PARTS, DEFAULT_EQUIPPED

__version__ = '1.6.0'


# Constants
TARGET_SELF = 'self'
TARGET_OTHER = 'target'

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

# TEMPLATES END

# Weights of distribution for biased selection of moves
WEIGHTED_MOVES = {'ATTACK': 1, 'HEAL': 0.1}


class Duel(commands.Cog):
    def __init__(self):
        self.underway = set()
        self.config = Config.get_conf(self, identifier=134621854878007297)
        default_member_config = {
            'stats': {
                'wins': 0,
                'losses': 0,
                'draws': 0
            },
            'equipped': DEFAULT_EQUIPPED,
            'inventory': []
        }
        default_guild_config = {
            'protected': [],
            'self_protect': False,
            'edit_posts': False,
            'items': {
                'helmet': DEFAULT_HELMETS,
                'body_armor': DEFAULT_BODY_ARMORS,
                'pants': DEFAULT_PANTS,
                'shoulders': DEFAULT_SHOULDERS,
                'gloves': DEFAULT_GLOVES,
                'boots': DEFAULT_BOOTS,
                'healing_item': DEFAULT_HEALING_ITEMS,
                'weapon': DEFAULT_WEAPONS
            },
            'initial_hp': 20,
            'max_rounds': 10
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
        highscore = ""
        place = 1
        members = {uid: server.get_member(uid) for uid, _ in topten}  # only look up once each
        names = {uid: m.display_name for uid, m in members.items()}
        max_name_len = max([len(n) for n in names.values()])

        # header
        highscore += '#'.ljust(len(str(top)) + 1)  # pad to digits in longest number
        highscore += 'Name'.ljust(max_name_len + 4)

        for stat in ['wins', 'losses', 'draws']:
            highscore += stat.ljust(8)

        highscore += '\n'

        for uid, config in topten:
            highscore += str(place).ljust(len(str(top)) + 1)  # pad to digits in longest number
            highscore += names[uid].ljust(max_name_len + 4)

            for stat in ['wins', 'losses', 'draws']:
                val = config['stats'][stat]
                highscore += '{}'.format(val).ljust(8)

            highscore += "\n"
            place += 1

        if len(highscore) < 1985:
            await ctx.send("```py\n" + highscore + "```")
        else:
            await ctx.send("The leaderboard is too big to be displayed. Try with a lower <top> parameter.")


    @checks.admin_or_permissions(administrator=True)
    @_duels.command(name="reset")
    async def _duels_reset(self, ctx):
        """
        Clears duel scores and equipment without resetting protection or editmode
        """

        await self.config.clear_all_members(ctx.guild)
        await ctx.send('Duel records cleared.')


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
                msg = 'After {0} rounds, {1.mention} wins with {1.hp} HP!'.format(i + 1, victor)
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
    @commands.group(name="duelshop", invoke_without_command=True)
    async def _duelshop(self, ctx):
        """
        Item purchasing/selling
        """

        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._duelshop_list)


    @_duelshop.command(name="list")
    async def _duelshop_list(self, ctx, category: str = None):
        """
        Shows all items (if no category was provided) currently in the shop
        """

        items = await self.config.guild(ctx.guild).items()
        msg = ''

        def sort_cost(item):
            return item['cost']

        def get_paddings(items):
            result = {}
            for field in items[0].keys():
                result[field] = len(HR_STATS[field]) + 1

            for item in items:
                for field in item.keys():
                    result[field] = max(result[field], len(str(item[field])) + 1)

            return result


        if category != None:
            if category not in items.keys():
                await ctx.send(f"Valid item categories: {', '.join(items.keys())}")
                return

            items = self.to_shop_items(items[category], category)
            paddings = get_paddings(items)
            msg = self.generate_header(paddings, category) + '\n'
            for item in sorted(items, key=sort_cost):
                msg += self.to_shop_row(item, paddings, category) + '\n'

            for page in pagify(msg, page_length=1993):
                await ctx.send(f'```py\n{page}```')

            return

        final_msg = ''
        for category in items.keys():
            msg = ''
            items[category] = self.to_shop_items(items[category], category)
            paddings = get_paddings(items[category])
            msg = self.generate_header(paddings, category) + '\n'
            for item in sorted(items[category], key=sort_cost):
                msg += self.to_shop_row(item, paddings, category) + '\n'

            final_msg += f"```py\n{msg}```"

        for page in pagify(final_msg, shorten_by=20, delims=['```py']):
            await ctx.send(page)


    @_duelshop.command(name="buy")
    async def _duelshop_buy(self, ctx, *, item_name):
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

        if not bank.can_spend(ctx.author, item['cost']):
            await ctx.send(f'You do not have enough {currency} to buy a **{item_name}**!')
            return

        await bank.withdraw_credits(ctx.author, item['cost'])
        inventory.append(item_name)
        await self.config.member(ctx.author).inventory.set(sorted(inventory))
        item_name_escaped = item_name if ' ' not in item_name else f'"{item_name}"'
        await ctx.send(f'You successfully bought a **{item_name}**! Equip it using `{ctx.prefix}duelinv equip {item_name_escaped}`.')

    @_duelshop.command(name="sell")
    async def _duelshop_sell(self, ctx, *, item_name):
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
    @commands.group(name="duelinv", invoke_without_command=True)
    async def _duelinv(self, ctx):
        """
        Inventory management
        """

        if ctx.invoked_subcommand is None:
            await ctx.invoke(self._duelinv_list)


    @_duelinv.command(name="list")
    async def _duelinv_list(self, ctx):
        """
        Shows your equipped items and your inventory
        """

        inventory = await self.get_inventory(ctx.author)
        equipped = await self.get_equipped_slots(ctx.author)
        inventory_str = 'None' if not len(inventory) else ', '.join(inventory)
        msg = f"{ctx.author.display_name}'s equipped items:\n{EQUIPPED.format(w = equipped['weapon'], h = equipped['helmet'], a = equipped['body_armor'], p = equipped['pants'], g = equipped['gloves'], b = equipped['boots'], s = equipped['shoulders'], heal = equipped['healing_item'])}"
        msg += f"{ctx.author.display_name}'s inventory:\n```{inventory_str}```"
        await ctx.send(msg)


    @_duelinv.command(name="equip")
    async def _duelinv_equip(self, ctx, *, item_name):
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


    @_duelinv.command(name="unequip")
    async def _duelinv_unequip(self, ctx, slot):
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
    @commands.group(name="duelset", invoke_without_command=True)
    async def _duelset(self, ctx):
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


    @_duelset.command(name="initial_hp")
    async def _duelset_initial_hp(self, ctx, initial_hp: int = None):
        """
        Change the HP players start with at the beginning of every duel
        """

        guild_config = await self.config.guild(ctx.guild).all()
        if initial_hp == None:
            await ctx.send(f"```http\ninitial_hp: {guild_config['initial_hp']}```")
            return

        guild_config['initial_hp'] = initial_hp
        await self.config.guild(ctx.guild).set(guild_config)
        await ctx.send(f"`initial_hp` set to `{initial_hp}`")


    @_duelset.command(name="max_rounds")
    async def _duelset_max_rounds(self, ctx, max_rounds: int = None):
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


    @_duelset.command(name="edit_posts")
    async def _duelset_edit_posts(self, ctx, edit_posts: bool = None):
        """
        Edit messages in-place instead of posting each move seperately
        """

        guild_config = await self.config.guild(ctx.guild).all()
        if edit_posts == None:
            await ctx.send(f"```http\nedit_posts: {guild_config['edit_posts']}```")
            return

        guild_config['edit_posts'] = edit_posts
        await self.config.guild(ctx.guild).set(guild_config)
        await ctx.send(f"`edit_posts` set to `{edit_posts}`")


    @_duelset.command(name="self_protect")
    async def _duelset_self_protect(self, ctx, self_protect: str = None):
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


    async def item_in_member_inventory(self, member, item_name):
        inventory = await self.get_inventory(member)
        for item in inventory:
            if item == item_name:
                return True

        return False


    async def item_equipped_by_member(self, member, item_name):
        equipped = await self.get_equipped(member)
        return item_name in equipped


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


    def to_shop_row(self, item, paddings, category):
        if category == 'weapon':
            return (f"{str(item['name']).ljust(paddings['name'])}"
                    f"{str(item['damage']).ljust(paddings['damage'])}"
                    f"{(str(int(item['hit_chance'] * 100)) + '%').ljust(paddings['hit_chance'])}"
                    f"{(str(int(item['crit_chance'] * 100)) + '%').ljust(paddings['crit_chance'])}"
                    f"{str(item['cost']).ljust(paddings['cost'])}")

        if category == 'healing_item':
            return (f"{str(item['name']).ljust(paddings['name'])}"
                    f"{str(item['healing']).ljust(paddings['healing'])}"
                    f"{str(item['cost']).ljust(paddings['cost'])}")

        return (f"{str(item['name']).ljust(paddings['name'])}"
                f"{str(item['armor']).ljust(paddings['armor'])}"
                f"{str(item['cost']).ljust(paddings['cost'])}"
        )


    def generate_header(self, paddings, category):
        if category == 'weapon':
            return (f"{HR_STATS['name'].ljust(paddings['name'])}"
                    f"{HR_STATS['damage'].ljust(paddings['damage'])}"
                    f"{HR_STATS['hit_chance'].ljust(paddings['hit_chance'])}"
                    f"{HR_STATS['crit_chance'].ljust(paddings['crit_chance'])}"
                    f"{HR_STATS['cost'].ljust(paddings['cost'])}\n"
                    f"{'-' * (paddings['name'] + paddings['damage'] + paddings['hit_chance'] + paddings['crit_chance'] + paddings['cost'])}")

        if category == 'healing_item':
            return (f"{HR_STATS['name'].ljust(paddings['name'])}"
                    f"{HR_STATS['healing'].ljust(paddings['healing'])}"
                    f"{HR_STATS['cost'].ljust(paddings['cost'])}\n"
                    f"{'-' * (paddings['name'] + paddings['healing'] + paddings['cost'])}")

        return (f"{HR_STATS['name'].ljust(paddings['name'])}"
                f"{HR_STATS['armor'].ljust(paddings['armor'])}"
                f"{HR_STATS['cost'].ljust(paddings['cost'])}\n"
                f"{'-' * (paddings['name'] + paddings['armor'] + paddings['cost'])}")

# UTILS END

def weighted_choice(choices):
    total = sum(w for c, w in choices.items())
    r = random.uniform(0, total)
    upto = 0

    for c, w in choices.items():
        if upto + w >= r:
            return c

        upto += w