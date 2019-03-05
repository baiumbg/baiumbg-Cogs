import dataclasses
from .constants import TRADE_POST_SETS_SECTION, TRADE_POST_SU_SECTION, TRADE_POST_SSU_SECTION,\
                       TRADE_POST_SSSU_SECTION, TRADE_POST_RUNEWORDS_SECTION, TRADE_POST_RAQMOJ_SECTION,\
                       TRADE_POST_BASES_SECTION, TRADE_POST_CHARMS_SECTION, TRADE_POST_TROPHIES_SECTION,\
                       TRADE_POST_MISC_SECTION, TRADE_POST_TEMPLATE
from typing import Set, Dict

@dataclasses.dataclass
class Item:
    name: str
    characters: Set[str] = dataclasses.field(default_factory=set)
    amount: float = 0

    def __hash__(self):
        return hash(self.name)

    def increment(self, character, amount = 1):
        self.amount += amount
        self.characters.add(character)

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
    other: Dict[str, Item] = dataclasses.field(default_factory=dict)

    def __bool__(self):
        return bool(self.sets or self.su or self.ssu or self.sssu or self.amulets or \
               self.rings or self.jewels or self.mos or self.quivers or \
               self.runewords or self.rw_bases or self.shrine_bases or \
               self.charms or self.trophies or self.shrines or self.other)

    def increment_set_item(self, set_name, item_name, character):
        self.sets.setdefault(set_name, Set(name=set_name)).items.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_su(self, item_name, character):
        self.su.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_ssu(self, item_name, character):
        self.ssu.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_sssu(self, item_name, character):
        self.sssu.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_amulet(self, item_name, character):
        self.amulets.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_ring(self, item_name, character):
        self.rings.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_jewel(self, item_name, character):
        self.jewels.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_mo(self, item_name, character):
        self.mos.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_quiver(self, item_name, character):
        self.quivers.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_rw(self, item_name, character):
        self.runewords.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_rw_base(self, item_name, character):
        self.rw_bases.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_shrine_base(self, item_name, character):
        self.shrine_bases.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_charm(self, item_name, character):
        self.charms.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_trophy(self, item_name, character):
        self.trophies.setdefault(item_name, Item(name=item_name)).increment(character)

    def increment_shrine(self, item_name, character, amount = 1):
        self.shrines.setdefault(item_name, Item(name=item_name)).increment(character, amount)

    def increment_other(self, item_name, character, amount = 1):
        self.other.setdefault(item_name, Item(name=item_name)).increment(character, amount)

    def to_trade_post(self):
        items_section = ''
        sets_str = ''
        for set_ in sorted(self.sets.values(), key=lambda k: k.name):
            sets_str += f'[u][color=#00FF00]{set_.name}[/color][/u]\n'
            for item in sorted(set_.items.values(), key=lambda k: k.name):
                sets_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

            sets_str += '\n'

        if sets_str:
            items_section += TRADE_POST_SETS_SECTION.format(items = sets_str)

        su_str = ''
        for item in sorted(self.su.values(), key=lambda k: k.name):
            su_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if su_str:
            items_section += TRADE_POST_SU_SECTION.format(items = su_str)

        ssu_str = ''
        for item in sorted(self.ssu.values(), key=lambda k: k.name):
            ssu_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if ssu_str:
            items_section += TRADE_POST_SSU_SECTION.format(items = ssu_str)

        sssu_str = ''
        for item in sorted(self.sssu.values(), key=lambda k: k.name):
            sssu_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if sssu_str:
            items_section += TRADE_POST_SSSU_SECTION.format(items = sssu_str)

        runewords_str = ''
        for item in sorted(self.runewords.values(), key=lambda k: k.name):
            runewords_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if runewords_str:
            items_section += TRADE_POST_RUNEWORDS_SECTION.format(items = runewords_str)

        raqmoj_str = ''
        for item in sorted(self.rings.values(), key=lambda k: k.name):
            raqmoj_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if self.rings:
            raqmoj_str += '\n'

        for item in sorted(self.amulets.values(), key=lambda k: k.name):
            raqmoj_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if self.amulets:
            raqmoj_str += '\n'

        for item in sorted(self.quivers.values(), key=lambda k: k.name):
            raqmoj_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if self.quivers:
            raqmoj_str += '\n'

        for item in sorted(self.mos.values(), key=lambda k: k.name):
            raqmoj_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if self.mos:
            raqmoj_str += '\n'

        for item in sorted(self.jewels.values(), key=lambda k: k.name):
            raqmoj_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if raqmoj_str:
            items_section += TRADE_POST_RAQMOJ_SECTION.format(items = raqmoj_str)

        bases_str = ''
        for item in sorted(self.rw_bases.values(), key=lambda k: k.name):
            bases_str += f'[color=#808080]{item.name}[/color] x{item.amount}\n' if item.amount > 1 else f'[color=#808080]{item.name}[/color]\n'

        for item in sorted(self.shrine_bases.values(), key=lambda k: k.name):
            bases_str += f'[color=#FFFF00]{item.name}[/color] x{item.amount}\n' if item.amount > 1 else f'[color=#FFFF00]{item.name}[/color]\n'

        if bases_str:
            items_section += TRADE_POST_BASES_SECTION.format(items = bases_str)

        charms_str = ''
        for item in sorted(self.charms.values(), key=lambda k: k.name):
            charms_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if charms_str:
            items_section += TRADE_POST_CHARMS_SECTION.format(items = charms_str)

        trophies_str = ''
        for item in sorted(self.trophies.values(), key=lambda k: k.name):
            trophies_str += f'[color=#FF7F50]{item.name}[/color] x{item.amount}\n' if item.amount > 1 else f'[color=#FF7F50]{item.name}[/color]\n'

        if trophies_str:
            items_section += TRADE_POST_TROPHIES_SECTION.format(items = trophies_str)

        other_str = ''
        for item in sorted(self.shrines.values(), key=lambda k: k.name):
            other_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if self.shrines:
            other_str += '\n'

        for item in sorted(self.other.values(), key=lambda k: k.name):
            other_str += f'[item]{item.name}[/item] x{item.amount}\n' if item.amount > 1 else f'[item]{item.name}[/item]\n'

        if other_str:
            items_section += TRADE_POST_MISC_SECTION.format(items = other_str)

        return TRADE_POST_TEMPLATE.format(items = items_section)