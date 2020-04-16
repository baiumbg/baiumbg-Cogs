import dataclasses
from typing import Set, Dict, List
import imgkit
import os
import tempfile
import random
import flickrapi
import hashlib
import enum
import asyncio
import functools

class PostGenerationErrors(enum.Enum):
    IMAGE_UPLOAD_FAILED = 1,
    UNKNOWN = 2

class PostTemplateArguments(dict):
    def __init__(self, *arg, **kwarg):
        super(PostTemplateArguments, self).__init__(*arg, **kwarg)
        self.missing_keys = set()

    def __missing__(self, key):
        self.missing_keys.add(key)
        return ''

@dataclasses.dataclass
class Item:
    name: str
    characters: List = dataclasses.field(default_factory=list)
    amount: float = 0
    html: List = dataclasses.field(default_factory=list)

    def __hash__(self):
        return hash(self.name)

    def increment(self, character, html, amount = 1):
        self.amount += amount
        self.characters.append(character)
        self.html.append(html)

@dataclasses.dataclass
class Set:
    name: str
    items: Dict[str, Item] = dataclasses.field(default_factory=dict)

@dataclasses.dataclass
class ItemDump:
    sets: Dict[str, Set] = dataclasses.field(default_factory=dict)
    su: Dict[str, Item] = dataclasses.field(default_factory=dict)
    ssu: Dict[str, Item] = dataclasses.field(default_factory=dict)
    sssu: Dict[str, Item] = dataclasses.field(default_factory=dict)
    amulets: Dict[str, Item] = dataclasses.field(default_factory=dict)
    rings: Dict[str, Item] = dataclasses.field(default_factory=dict)
    jewels: Dict[str, Item] = dataclasses.field(default_factory=dict)
    mos: Dict[str, Item] = dataclasses.field(default_factory=dict)
    quivers: Dict[str, Item] = dataclasses.field(default_factory=dict)
    runewords: Dict[str, Item] = dataclasses.field(default_factory=dict)
    rw_bases: Dict[str, Item] = dataclasses.field(default_factory=dict)
    shrine_bases: Dict[str, Item] = dataclasses.field(default_factory=dict)
    charms: Dict[str, Item] = dataclasses.field(default_factory=dict)
    trophies: Dict[str, Item] = dataclasses.field(default_factory=dict)
    shrines: Dict[str, Item] = dataclasses.field(default_factory=dict)
    crafted: Dict[str, Item] = dataclasses.field(default_factory=dict)
    other: Dict[str, Item] = dataclasses.field(default_factory=dict)

    def __bool__(self):
        return bool(self.sets or self.su or self.ssu or self.sssu or self.amulets or \
               self.rings or self.jewels or self.mos or self.quivers or \
               self.runewords or self.rw_bases or self.shrine_bases or \
               self.charms or self.trophies or self.shrines or self.other)

    def increment_set_item(self, set_name, item_name, character, html):
        self.sets.setdefault(set_name, Set(name=set_name)).items.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_su(self, item_name, character, html):
        self.su.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_ssu(self, item_name, character, html):
        self.ssu.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_sssu(self, item_name, character, html):
        self.sssu.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_amulet(self, item_name, character, html):
        self.amulets.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_ring(self, item_name, character, html):
        self.rings.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_jewel(self, item_name, character, html):
        self.jewels.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_mo(self, item_name, character, html):
        self.mos.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_quiver(self, item_name, character, html):
        self.quivers.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_rw(self, item_name, character, html):
        self.runewords.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_rw_base(self, item_name, character, html):
        self.rw_bases.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_shrine_base(self, item_name, character, html):
        self.shrine_bases.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_charm(self, item_name, character, html):
        self.charms.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_trophy(self, item_name, character, html, amount = 1):
        self.trophies.setdefault(item_name, Item(name=item_name)).increment(character, html, amount)

    def increment_shrine(self, item_name, character, html, amount = 1):
        self.shrines.setdefault(item_name, Item(name=item_name)).increment(character, html, amount)

    def increment_crafted(self, item_name, character, html):
        self.crafted.setdefault(item_name, Item(name=item_name)).increment(character, html)

    def increment_other(self, item_name, character, html, amount = 1):
        self.other.setdefault(item_name, Item(name=item_name)).increment(character, html, amount)

    async def to_trade_post(self, post_template, flickr_client, css_file, user_config, flickr_cache, thread_pool):
        sets_str = ''
        cache_update = {}
        loop = asyncio.get_running_loop()
        for set_ in sorted(self.sets.values(), key=lambda k: k.name):
            sets_str += f'[u][color=#00FF00]{set_.name}[/color][/u]\n'
            for item in sorted(set_.items.values(), key=lambda k: k.name):
                sets_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

            sets_str += '\n'

        su_str = ''
        for item in sorted(self.su.values(), key=lambda k: k.name):
            su_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        ssu_str = ''
        for item in sorted(self.ssu.values(), key=lambda k: k.name):
            ssu_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        sssu_str = ''
        for item in sorted(self.sssu.values(), key=lambda k: k.name):
            sssu_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        runewords_str = ''
        for item in sorted(self.runewords.values(), key=lambda k: k.name):
            runewords_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        crafted_str = ''
        for item in sorted(self.crafted.values(), key=lambda k: k.name):
            crafted_str += f'[color=#FAAA23]{item.name}[/color] x{item.amount}\n' if item.amount > 1 else f'[color=#FAAA23]{item.name}[/color]\n'

            if user_config['generate_crafted_images']:
                crafted_str += '[spoil]\n'

                for tag in item.html:
                    if tag.find(class_='gear_img'):
                        tag.img.extract()
                    else:
                        tag.img['src'] = f'https://tsw.vn.cz/acc/{tag.img["src"]}'
                        tag.span.extract()

                    tag.div['style'] = 'display: block; white-space: nowrap;'

                    hash_md5 = hashlib.md5()
                    hash_md5.update(str(tag).encode())
                    item_md5 = hash_md5.hexdigest()
                    if item_md5 in flickr_cache:
                        crafted_str += f'[img]{flickr_cache[item_md5]}[/img]'
                        continue

                    if item_md5 in cache_update:
                        crafted_str += f'[img]{cache_update[item_md5]}[/img]'
                        continue

                    image_file = os.path.join(tempfile.gettempdir(), ''.join(random.choice('0123456789ABCDEF') for i in range(12)) + '.png')
                    await loop.run_in_executor(thread_pool, functools.partial(imgkit.from_string, str(tag), image_file, css=css_file, options={'width': '0', 'xvfb': ''}))

                    image_id = ''
                    image_link = ''
                    try:
                        image_id = flickr_client.upload(image_file).photoid[0].text
                        image_link = flickr_client.photos.getSizes(photo_id=image_id).sizes[0].size[-1]['source']
                    except:
                        return None, cache_update, PostGenerationErrors.IMAGE_UPLOAD_FAILED, None
                    finally:
                        os.remove(image_file)

                    crafted_str += f'[img]{image_link}[/img]\n'
                    cache_update[item_md5] = image_link

                crafted_str += '[/spoil]\n'

        rings_str = ''
        for item in sorted(self.rings.values(), key=lambda k: k.name):
            rings_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        amulets_str = ''
        for item in sorted(self.amulets.values(), key=lambda k: k.name):
            amulets_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        quivers_str = ''
        for item in sorted(self.quivers.values(), key=lambda k: k.name):
            quivers_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        mos_str = ''
        for item in sorted(self.mos.values(), key=lambda k: k.name):
            mos_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        jewels_str = ''
        for item in sorted(self.jewels.values(), key=lambda k: k.name):
            jewels_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        rw_bases_str = ''
        for item in sorted(self.rw_bases.values(), key=lambda k: k.name):
            rw_bases_str += f'[color=#808080]{item.name}[/color] x{item.amount}\n' if item.amount > 1 else f'[color=#808080]{item.name}[/color]\n'

        shrine_bases_str = ''
        for item in sorted(self.shrine_bases.values(), key=lambda k: k.name):
            shrine_bases_str += f'[color=#FFFF00]{item.name}[/color] x{item.amount}\n' if item.amount > 1 else f'[color=#FFFF00]{item.name}[/color]\n'

        charms_str = ''
        for item in sorted(self.charms.values(), key=lambda k: k.name):
            charms_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        trophies_str = ''
        for item in sorted(self.trophies.values(), key=lambda k: k.name):
            trophies_str += f'[color=#FF7F50]{item.name}[/color] x{item.amount}\n' if item.amount > 1 else f'[color=#FF7F50]{item.name}[/color]\n'

        shrines_str = ''
        for item in sorted(self.shrines.values(), key=lambda k: k.name):
            item.amount = round(item.amount, 1) if item.amount % 1 else int(item.amount)
            shrines_str += f'[color=#FAAA23]{item.name}[/color] x{item.amount}\n' if item.amount != 1 else f'[color=#FAAA23]{item.name}[/color]\n'

        misc_str = ''
        for item in sorted(self.other.values(), key=lambda k: k.name):
            item.amount = round(item.amount, 1) if item.amount % 1 else int(item.amount)
            misc_str += f'{item.name} x{item.amount}\n' if item.amount != 1 else f'{item.name}\n'

        template_args = PostTemplateArguments(
            sets = sets_str,
            su = su_str,
            ssu = ssu_str,
            sssu = sssu_str,
            rws = runewords_str,
            crafted = crafted_str,
            rings = rings_str,
            amulets = amulets_str,
            quivers = quivers_str,
            mos = mos_str,
            jewels = jewels_str,
            rw_bases = rw_bases_str,
            shrine_bases = shrine_bases_str,
            charms = charms_str,
            trophies = trophies_str,
            shrines = shrines_str,
            misc = misc_str
        )

        return post_template.format_map(template_args), cache_update, None, template_args.missing_keys
