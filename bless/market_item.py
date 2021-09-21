from bs4 import BeautifulSoup
from enum import Enum
import re

MARKET_PRICE_ZEN_REGEX = re.compile(r"((\d*[.])?\d+) (k* )?Zen.")
MARKET_PRICE_BONS_REGEX = re.compile(r"(\d+) Bon.")
MARKET_ITEM_NAME_REGEX = re.compile(r"overinfo-name.*")
MARKET_ITEM_GRADE_REGEX = re.compile(r"Grade: (\d+)")
MARKET_ITEM_UPGRADE_LEVEL_REGEX = re.compile(r"\+(\d+)")
MARKET_ITEM_ARMOR_LIFE_REGEX = re.compile(r"Additional defense \+(\d+)")
MARKET_ITEM_WEAPON_LIFE_REGEX = re.compile(r"Additional Dmg \+(\d+)")
MARKET_ITEM_SERIAL_REGEX = re.compile(r"Serial: (\d+)")
OPTION_ZEN_TEXT = "Increase Zen from monsters +40%"
OPTION_MANA_ON_KILL_TEXT = "Increase Mana after monster +Mana/8"
OPTION_REF_TEXT = "Reflect Damage +5%"
OPTION_SPEED_TEXT = "Increase Attacking(Wizardry)speed +7"
OPTION_MANA_TEXT = "Increase Max Mana +4%"
OPTION_WIZARDRY_DMG_PER_LVL_TEXT = "Increase Wizardry Damage +level/20"
OPTION_DMG_PER_LVL_TEXT = "Increase Damage +level/20"
OPTION_HP_ON_KILL_TEXT = "Increase Life after monster +Life/8"
OPTION_DEF_RATE_TEXT = "Defense success rate +10%"
OPTION_DD_TEXT = "Damage Decrease +4%"
OPTION_WIZ_DMG_TEXT = "Increase Wizardry Damage +2%"
OPTION_DMG_TEXT = "Increase Damage +2%"
OPTION_HP_TEXT = "Increase Max HP +4%"
OPTION_EXC_RATE = "Excellent Damage rate +10%"

class MarketItemQuality(Enum):
    UNKNOWN = 0
    NORMAL = 1
    EXCELLENT = 2
    ANCIENT = 3

class MarketItemPriceType(Enum):
    UNKNOWN = 0
    BONS = 1
    ZEN = 2

class MarketItem:
    def __init__(self, row_columns):
        #row_columns = item_soup.find_all("td") # [0] - category, [1] - item, [2] - seller, [3] - price
        tooltip_soup = BeautifulSoup(row_columns[1].a["title"], features="html.parser")

        name_div = tooltip_soup.find("div", class_=MARKET_ITEM_NAME_REGEX)
        self.name = name_div.text
        if "exc" in name_div["class"][0]:
            self.quality = MarketItemQuality.EXCELLENT
        elif "anc" in name_div["class"][0]:
            self.quality = MarketItemQuality.ANCIENT
        else:
            self.quality = MarketItemQuality.NORMAL
        
        grade_match = MARKET_ITEM_GRADE_REGEX.match(tooltip_soup.text)
        self.grade = int(grade_match.group(1)) if grade_match else 0

        upgrade_level_match = MARKET_ITEM_UPGRADE_LEVEL_REGEX.match(self.name)
        self.upgrade_level = int(upgrade_level_match.group(1)) if upgrade_level_match else 0

        armor_life_match = MARKET_ITEM_ARMOR_LIFE_REGEX.match(tooltip_soup.text)
        if armor_life_match:
            self.life = int(armor_life_match.group(1))
        else:
            weapon_life_match = MARKET_ITEM_WEAPON_LIFE_REGEX.match(tooltip_soup.text)
            if weapon_life_match:
                self.life = int(weapon_life_match.group(1))
            else:
                self.life = 0

        self.luck = tooltip_soup.find("div", class_="overinfo-luck-info") is not None

        exc_options_div = tooltip_soup.find("div", class_="overinfo-exc-info")
        if exc_options_div:
            self.zen_or_mana = OPTION_ZEN_TEXT in exc_options_div.text or OPTION_MANA_ON_KILL_TEXT in exc_options_div.text
            self.ref_or_speed = OPTION_REF_TEXT in exc_options_div.text or OPTION_SPEED_TEXT in exc_options_div.text
            self.mana_or_dmg_per_lvl = OPTION_MANA_TEXT in exc_options_div.text or OPTION_WIZARDRY_DMG_PER_LVL_TEXT in exc_options_div.text or OPTION_DMG_PER_LVL_TEXT in exc_options_div.text
            self.def_rate_or_hp = OPTION_DEF_RATE_TEXT in exc_options_div.text or OPTION_HP_ON_KILL_TEXT in exc_options_div.text
            self.dd_or_dmg = OPTION_DD_TEXT in exc_options_div.text or OPTION_WIZ_DMG_TEXT in exc_options_div.text or OPTION_DMG_TEXT in exc_options_div.text
            self.hp_or_exc_rate = OPTION_HP_TEXT in exc_options_div.text or OPTION_EXC_RATE in exc_options_div.text
        else:
            self.zen_or_mana = False
            self.ref_or_speed = False
            self.mana_or_dmg_per_lvl = False
            self.def_rate_or_hp = False
            self.dd_or_dmg = False
            self.hp_or_exc_rate = False

        price_bons_match = MARKET_PRICE_BONS_REGEX.match(row_columns[3].text)
        if price_bons_match:
            self.price = float(price_bons_match.group(1))
            self.price_type = MarketItemPriceType.BONS
        else:
            price_zen_match = MARKET_PRICE_ZEN_REGEX.match(row_columns[3].text)
            power = price_zen_match.group(3).count("k") - 2 if price_zen_match.group(3) else -2
            self.price = float(price_zen_match.group(1)) * (1000 ** power)
            self.price_type = MarketItemPriceType.ZEN

        self.seller = row_columns[2].text
        serial_match = MARKET_ITEM_SERIAL_REGEX.match(tooltip_soup.find_all("div")[-1].text)
        self.serial = serial_match.group(1) if serial_match else ""

    def __str__(self):
        return f"[{', '.join([str(a) for a in self.__dict__])}]"