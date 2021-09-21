from .market_item import MarketItemQuality, MarketItemPriceType
import math
import textwrap

class MarketItemFilter():
    def __init__(self, id):
        self.id = id
        self.name = ""
        self.quality = MarketItemQuality.UNKNOWN
        self.grade = 0
        self.upgrade_level = 0
        self.life = 0
        self.luck = False
        self.zen_or_mana = False
        self.ref_or_speed = False
        self.mana_or_dmg_per_lvl = False
        self.def_rate_or_hp = False
        self.dd_or_dmg = False
        self.hp_or_exc_rate = False
        self.price = math.inf
        self.price_type = MarketItemPriceType.BONS
        self.seller = ""

    def __str__(self):
        s = f"ID: {self.id}"
        if self.name != "": s += f"\nItem name: {self.name}"
        if self.quality != MarketItemQuality.UNKNOWN: s += f"\nItem quality: {self.quality.name.lower()}"
        if self.grade > 0: s += f"\nMin grade: {self.grade}"
        if self.upgrade_level > 0: s += f"\nMin upgrade level: {self.upgrade_level}"
        if self.life > 0: s += f"\nMin life opt: {self.life}"
        if self.price != math.inf: s += f"\nMax price: {self.price}{'kk' if self.price_type == MarketItemPriceType.ZEN else 'bon'}"
        if self.seller != "": s += f"\nSeller: {self.seller}"

        if not self.luck and not self.zen_or_mana and not self.ref_or_speed and not self.mana_or_dmg_per_lvl and not self.def_rate_or_hp and not self.dd_or_dmg and not self.hp_or_exc_rate:
            return s

        s += "\nOpts: "
        
        opts = []
        if self.luck:
            opts.append("luck")

        if self.zen_or_mana:
            opts.append("zen/mana on kill")

        if self.ref_or_speed:
            opts.append("ref/speed")

        if self.mana_or_dmg_per_lvl:
            opts.append("mana/dmg/20")

        if self.def_rate_or_hp:
            opts.append("rate/hp on kill")

        if self.dd_or_dmg:
            opts.append("dd/dmg")

        if self.hp_or_exc_rate:
            opts.append("hp/exc rate")

        s += ", ".join(opts)

        return s

    def matches_item(self, market_item):
        if self.name != "" and self.name.lower() not in market_item.name.lower():
            return False

        if self.quality != MarketItemQuality.UNKNOWN and self.quality != market_item.quality:
            return False

        if self.grade > market_item.grade:
            return False

        if self.upgrade_level > market_item.upgrade_level:
            return False

        if self.life > market_item.life:
            return False

        if self.luck and not market_item.luck:
            return False

        if self.zen_or_mana and not market_item.zen_or_mana:
            return False

        if self.ref_or_speed and not market_item.ref_or_speed:
            return False

        if self.mana_or_dmg_per_lvl and not market_item.mana_or_dmg_per_lvl:
            return False

        if self.def_rate_or_hp and not market_item.def_rate_or_hp:
            return False

        if self.dd_or_dmg and not market_item.dd_or_dmg:
            return False

        if self.hp_or_exc_rate and not market_item.hp_or_exc_rate:
            return False

        if self.price_type != market_item.price_type:
            return False

        if self.price < market_item.price:
            return False

        if self.seller != "" and self.seller.lower() != market_item.seller.lower():
            return False

        return True

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name, 
            "quality": self.quality.value,
            "grade": self.grade,
            "upgrade_level": self.upgrade_level,
            "life": self.life,
            "luck": self.luck,
            "zen_or_mana": self.zen_or_mana,
            "ref_or_speed": self.ref_or_speed,
            "mana_or_dmg_per_lvl": self.mana_or_dmg_per_lvl,
            "def_rate_or_hp": self.def_rate_or_hp,
            "dd_or_dmg": self.dd_or_dmg,
            "hp_or_exc_rate": self.hp_or_exc_rate,
            "price": self.price,
            "price_type": self.price_type.value,
            "seller": self.seller
        }

    def from_dict(d):
        f = MarketItemFilter(d["id"])
        f.name = d["name"]
        f.quality = MarketItemQuality(d["quality"])
        f.grade = d["grade"]
        f.upgrade_level = d["upgrade_level"]
        f.life = d["life"]
        f.luck = d["luck"]
        f.zen_or_mana = d["zen_or_mana"]
        f.ref_or_speed = d["ref_or_speed"]
        f.mana_or_dmg_per_lvl = d["mana_or_dmg_per_lvl"]
        f.def_rate_or_hp = d["def_rate_or_hp"]
        f.dd_or_dmg = d["dd_or_dmg"]
        f.hp_or_exc_rate = d["hp_or_exc_rate"]
        f.price = d["price"]
        f.price_type = MarketItemPriceType(d["price_type"])
        f.seller = d["seller"]

        return f