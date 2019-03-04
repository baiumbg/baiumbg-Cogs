from redbot.core import commands, checks, Config
from redbot.core.utils.chat_formatting import pagify
import discord
import random
import requests
import re
import enum
from bs4 import BeautifulSoup
from .pastebin import PasteBin

class LoginError(enum.Enum):
    NONE = 0
    INCORRECT_USERNAME = 1,
    INCORRECT_PASSWORD = 2,
    LOGIN_ATTEMPTS_EXCEEDED = 3,
    UNKNOWN = 4

SU_ITEMS = [
    'Screen of Viz-Jaq\'Taar',
    'Razorspine',
    'Hratli\'s Craft',
    'Alchemist Apron',
    'Hepsheeba\'s Mantle',
    'Candlewake',
    'Skin of Kabraxis',
    'Icetomb',
    'Elemental Disciple',
    'Scales of the Serpent',
    'Robe of Steel',
    'Silks of the Victor',
    'Lacuni Cowl',
    'Shiverhood',
    'Metalhead',
    'Aidan\'s Lament',
    'Eyes of Septumos',
    'Gromotvod',
    'Royal Circlet',
    'Crown of the Black Rose',
    'Trang-Oul\'s Breath',
    'Gaze of the Dead',
    'Witch Drum',
    'Lightforge',
    'Shield of Hakan II',
    'Rainbow Fury',
    'Stone Guardian',
    'The Endless Loop',
    'Ashaera\'s Armor',
    'Nor Tiraj\'s Wisdom',
    'Lilith\'s Temptation',
    'Blackjade\'s Legacy',
    'Hammerfist',
    'Dacana\'s Fist',
    'Blind Anger',
    'Hellmouth',
    'Titan\'s Steps',
    'Shrill Sacrament',
    'Binding Treads',
    'Rodeo\'s Tramplers',
    'Karcheus\' Temptation',
    'Lionblood Crest',
    'Crown of Arnazeus',
    'Helepolis',
    'Vision of the Furies',
    'Impundulu',
    'Golden Chariot',
    'Silver Scorpion',
    'The Doom Gong of Xiansai',
    'Hexward',
    'Banner of Bitter Winds',
    'Rodeo\'s Hide',
    'Toraja\'s Champion',
    'Shadowtwin',
    'Bear Grin',
    'Eagle Eye',
    'Bul Kathos\' Temper',
    'Coldhunger',
    'Savage Hunter',
    'Forest Defender',
    'Phoenix Beak',
    'Nature\'s Orphan',
    'Bottled Will-o-Wisp',
    'Dark Guardian',
    'Hero\'s Fang',
    'Grim Silhouette',
    'Barghest\'s Howl',
    'Hivemind',
    'The Book of Kalen',
    'Orationis Tenebris',
    'Argentek\'s Tide',
    'Astreon\'s Citadel',
    'Ignis Demonia',
    'The Ritualist',
    'Dervish of Aranoch',
    'Bartuc\'s Curse',
    'Zann Prodigy',
    'Armor of the Old Religion',
    'The Xiphos',
    'Kraken\'s Cutlass',
    'Saber of the Stormsail',
    'Aeterna',
    'Aurumvorax',
    'Shadowsabre',
    'Qarak\'s Will',
    'Tylwulf\'s Betrayal',
    'Blacktongue',
    'Feltongue',
    'Grotesque Bite',
    'The Captain',
    'Nimmenjuushin',
    'Elder Law',
    'Dreamflange',
    'Firequeen',
    'Viper Mandate',
    'Legion',
    'Dead Lake\'s Lady',
    'Thunderbane',
    'Screaming Serpent',
    'Night\'s Embrace',
    'Lancea',
    'Steel Pillar',
    'Darkspite',
    'The Pride of Caldeum',
    'Bitter Harvest',
    'Bone Scalpel',
    'Frostneedle',
    'Plunderbird',
    'Meshif\'s Iron Parrot',
    'Warshrike',
    'Buzzbomb',
    'Lacerator',
    'Griefbringer',
    'Vizjerei\'s Folly',
    'Shamanka',
    'Aerin Nexus',
    'Xorine\'s Cane',
    'Spire of Kehjan',
    'Chillstring',
    'Gjallarhorn',
    'Fleshstinger',
    'Hellreach',
    'Ratbane',
    'Nihlathak\'s Bombard',
    'Horned Hunter',
    'Askarbydd',
    'Serenthia\'s Scorn',
    'Hellrain',
    'Twin Terrors',
    'Dreamweaver',
    'Legio Di Manes',
    'Frysturgard',
    'Kaskara of the Taan',
    'Talic the Unwilling',
    'The Pathless',
    'Esubane',
    'Skeld\'s Battlesong',
    'Cleaver of Mirrors',
    'Peace Warder',
    'Ord Rekar\'s Testament',
    'Yaggai\'s Sagaris',
    'Faerie Pyre',
    'Azgar\'s Mark',
    'Guardian of Scosglen',
    #'Hanfod Tân', Wrong encoding aahz :kek:
    'Reaper\'s Hand',
    'Karybdus\' Descent',
    'Dreamflayer',
    'Mente Scura',
    'Hwanin\'s Hwacha',
    'Nymyr\'s Shadow',
    'Manastorm',
    'Storm Focus',
    'The Pyre',
    'Darkfeast',
    'Herald of Pestilence',
    'Chober Chaber',
    'In Fero Salva',
    'Black Sun Spear',
    'Habacalva\'s Legacy',
    'Ghostmoon',
    'Bane of the Horadrim',
    'Gravetalon',
    'Leah\'s Vision',
    'Starhawk',
    'Maleficence'
]

SSU_ITEMS = [
    'Natalya\'s Deception',
    'The Petulant',
    'Scales of the Drake',
    'Hide of the Basilisk',
    'Arkaine\'s Valor',
    'Wolverine Skin',
    'Segnitia',
    'Auriel\'s Robe',
    'Strength Beyond Strength',
    'Goetia Plate',
    'Khazra Plate',
    'Skull of the Viz-Jaq\'taar',
    'Reapers',
    'Veil of Steel',
    'Undead Crown',
    'Dark Pact',
    'Soulsplitter',
    'Radiance',
    'Griffon\'s Eye',
    'Idol of Rygnar',
    'Black Masquerade',
    'The Flying Saucer',
    'Stormflyer',
    'Madawc Val Narian',
    'The Collector',
    'Celestial Barrier',
    'Lunar Eclipse',
    'Dementia',
    'Black Void',
    'Champion of the Triune',
    'Demonic Touch',
    'Rogue Foresight',
    'Facebreaker',
    'Lorekeeper',
    'Lamha Na Draoithe',
    'Spirit Walker',
    'Angel\'s Wrath',
    'Akarat\'s Trek',
    'Knight\'s Grace',
    'Rakkis\' Benediction',
    'Rainbow Maiden',
    'Deviant Crown',
    'Asgardsreia',
    'Danmaku',
    'Crimson Dream',
    'Hammerfall',
    'Eternal Bodyguard',
    'Zayl\'s Temptation',
    'Pawnstorm',
    'The Ancients\' Legacy',
    'Warmonger',
    'Voice of Arreat',
    'Boarfrost',
    'Lilith\'s Legion',
    'Greenwalker\'s Charge',
    'Sky Spirit',
    'Ranger\'s Disguise',
    'Homunculus',
    'Feardrinker',
    'The Sentinel\'s Sorrow',
    'Sinwar',
    'Blessed Wrath',
    'Veil of the Tainted Sun',
    'Mark of the Que-Hegan',
    'The Vanquisher',
    'The Last Crusader',
    'Herald of Zakarum',
    'Angelhost',
    'Cloak of the Outcast',
    'Adamantine Guard',
    'Frozen Heart',
    'Lachdanan\'s Visage',
    'Atanna Khan\'s Dress',
    'The Eviscerator',
    'Sherazade',
    'Alnair',
    'Sarandeshi Hellcaller',
    'Eternal Vigil',
    'Astral Blade',
    'Durandal the Blazing Sword',
    'Shadowfang',
    'Carsomyr',
    'The Grandfather',
    'Headsman',
    'The Colonel',
    'Dux Infernum',
    'Gotterdammerung',
    'Hammer of Jholm',
    'Solar Scion',
    'The Redeemer',
    'Battlemaiden',
    'Vizjerei Fury',
    'Moonfang',
    'Heartseeker',
    'The Retiarius',
    'Stormchaser',
    'Freakshow',
    'Wizardspike',
    'Black Razor',
    'Drow Valor',
    'Dark Nemesis',
    'Piranha Swarm',
    'Penumbra',
    'Deckard Cain\'s Heirloom',
    'Staff of Shadows',
    'Spire of Sarnakyle',
    'Absolute Zero',
    'Valthek\'s Command',
    'Etrayu',
    'Signal Fire',
    'Windforce',
    'Buriza-Do Kyanon',
    'Manticore Sting',
    'Athulua\'s Wrath',
    'Chasmstriker',
    'Panthera\'s Bite',
    'Titan\'s Revenge',
    'Sagittarius',
    'Mind Rake',
    'Zular Khan\'s Tempest',
    'Gladiator\'s Rage',
    'Berserrker',
    'Claw of the Spirit Wolf',
    'Colliding Fury',
    'Thunder King of Sescheron',
    'The King of Ents',
    'Eye of the Storm',
    'Mr. Painless',
    'The Biting Frost',
    'Soul Reaver',
    'Shadowfiend',
    'The Defiler',
    'Heart of Fire',
    'Advent of Hatred',
    'Stygian Fury',
    'Mad King\'s Spine',
    'Adjudicator',
    'The Angiris Star',
    'Malleus Maleficarum',
    'Venom Sting',
    'Jaguar\'s Grasp',
    'Holy Wars',
    'Mistress of Pain',
    'Glowing Vertigo',
    'Atanna\'s Key',
    'Galeona\'s Lash',
    'Steel Punisher',
    'Despondence'
]

SSSU_ITEMS = [
    'Tyrael\'s Might',
    'Azurewrath',
    'The Point of No Return',
    'Storm Blade',
    'The Searing Heat',
    'Desolation'
]

RINGS = [
    'Ras Algethi',
    'Seal of the Nephalem Kings',
    'Ouroboros',
    'Bad Mood',
    'Signet of the Gladiator',
    'Sigil of the 7 Deadly Sins',
    'Ring of Disengagement',
    'Xorine\'s Ring',
    'The Seal of Kharos',
    'Sigil of Tur Dulra',
    'Giant\'s Knuckle',
    'Empyrean Glory',
    'Elemental Band',
    'Ring of Truth',
    'Earth Rouser',
    'Bloodbond',
    'Der Nebelring',
    'Witchcraft',
    'Adrenaline Rush',
    'Black Hand Sigil',
    'Ripstar',
    'Empyrean Band',
    'Myokai\'s Path',
    'Ring of Regha',
    'Assur\'s Bane'
]

AMULETS = [
    'Niradyahk',
    'Vizjerei\'s Necklace',
    'Dyers Eve',
    'In For The Kill',
    'Lamen of the Archbishop',
    'Hangman',
    'Felblood',
    'The Dreamcatcher',
    'Locket of Dreams',
    'Black Dwarf',
    'Death Ward',
    'Gallowlaugh',
    'Khanduran Royal Pendant',
    'Fren Slairea',
    'Angel Heart',
    'Teganze Pendant',
    'The Tesseract',
    'Klaatu Barada Nikto',
    'Beads of the Snake Queen',
    'Quov Tsin\'s Talisman',
    'The Buried Hawk',
    'Scarab of Death',
    'Athulua\'s Oracle',
    'Witchmoon'
]

JEWELS = [
    'Heavenstone',
    'Arkenstone',
    'Atomus',
    'The Boulder',
    'Demonstone Blood',
    'Katamari',
    'Xepera Xeper Xeperu',
    'Inarius\' Rock',
    'Cornerstone of the World',
    'Storm Shard',
    'Zakarum Stoning Rock',
    'Borgin\'s Vigil',
    'Zann Esu\'s Stone',
    'Suicide Note',
    'Jewel of Luck',
    'Asheara\'s Cateye',
    'Farsight Globe'
]

QUIVERS = [
    'Bag of Tricks',
    'Locust Hive',
    'Lammergeier',
    'Plague Gland',
    'Kingsport\'s Signals',
    'Cindercone',
    'Devil\'s Dance',
    'Larzuk\'s Bandolier',
    'Hanabigami',
    'The Tranquilizer'
]

MOS = [
    'Larzuk\'s Round Shot',
    'Vizjun\'s Ball Bearing',
    'Nor Tiraj\'s Flaming Sphere',
    'The Demon Core',
    'Uldyssian\'s Spirit',
    'Orb of Annihilation',
    'Warbringer',
    'Ten Pin Striker',
    'Wrathspirit',
    'Idol of Stars',
    'Nagapearl',
    'The Moon Crystal',
    'Auriel\'s Focus',
    'Solitude',
    'Crystal of Tears',
    'Essence of Itherael',
    'Periapt of Life',
    'Lodestone',
    'Kara\'s Trinket',
    'Monsterball',
    'Heart of Frost',
    'Relic of Yaerius',
    'The Endless Light',
    'Explorer\'s Globe',
    'The Perfect Sphere',
    'Marksman\'s Eye',
    'Zayl\'s Soul Orb',
    'Farnham\'s Lost Marble',
    'Eye of Malic',
    'Apple of Discord'
]

CHARMS = [
    'Sunstone of the Twin Seas',
    'Sacred Sunstone',
    'Shadow Vortex',
    'Worldstone Orb',
    'Caoi Dulra Fruit',
    'Soulstone Shard',
    'Eye of Divinity',
    'Nexus Crystal',
    'The Butcher\'s Tooth',
    'Optical Detector',
    'Laser Focus Crystal',
    'Sacred Worldstone Key',
    'Scroll of Kings',
    'Visions of Akarat',
    'Moon of the Spider',
    'Horazon\'s Focus',
    'The Black Road',
    'Legacy of Blood',
    'Fool\'s Gold',
    'Spirit Trance Herb',
    'Idol of Vanity',
    'Azmodan\'s Heart',
    'Weather Control',
    'Silver Seal of Ureh',
    'Crystalline Flame Medallion',
    'Soul of Kabraxis',
    'Eternal Bone Pile',
    'Book of Lies',
    'Dragon Claw',
    'The Ancient Repositories',
    'Xazax\'s Illusion',
    'Astrogha\'s Venom Stinger',
    'The Sleep',
    'Neutrality Pact',
    'Glorious Book of Median',
    'Rathma\'s Supremacy',
    'Vial of Elder Blood',
    'Six Angel Bag',
    'Hammer of the Taan Judges',
    'Zakarum\'s Ear',
    'Sunstone of the Gods',
    'Umbaru Treasure',
    'Corrupted Wormhole',
    'Demonsbane',
    'Lylia\'s Curse',
    'Cold Fusion Schematics',
]

TROPHIES = [
    'Akarat Trophy',
    'Black Road Trophy',
    'Astrogha Trophy',
    'Legacy of Blood Trophy',
    'The Lord of Sin Trophy',
    'Lord Aldric Jitan Trophy',
    'Archbishop Lazarus Trophy',
    'Viz-jun Trophy',
    'Cathedral of Light Trophy',
    'Quov Tsin Trophy',
    'Duncraig Trophy',
    'Rathma Square Trophy',
    'Judgement Day Trophy',
    'Tran Athulua Trophy',
    'Kingdom of Shadow Trophy',
    'Uldyssian Trophy',
    'Triune Trophy'
]

SHRINE_VESSELS = [
    'Creepy Vessel',
    'Sacred Vessel',
    'Quiet Vessel',
    'Hidden Vessel',
    'Tainted Vessel',
    'Ornate Vessel',
    'Fascinating Vessel',
    'Intimidating Vessel',
    'Weird Vessel',
    'Trinity Vessel',
    'Spiritual Vessel',
    'Eerie Vessel',
    'Enchanted Vessel',
    'Shimmering Vessel',
    'Magical Vessel',
    'Abandoned Vessel'
]

VESSEL_TO_SHRINE = {
    'Creepy Vessel': 'Creepy Shrine',
    'Sacred Vessel': 'Sacred Shrine',
    'Quiet Vessel': 'Quiet Shrine',
    'Hidden Vessel': 'Hidden Shrine',
    'Tainted Vessel': 'Tainted Shrine',
    'Ornate Vessel': 'Ornate Shrine',
    'Fascinating Vessel': 'Fascinating Shrine',
    'Intimidating Vessel': 'Intimidating Shrine',
    'Weird Vessel': 'Weird Shrine',
    'Trinity Vessel': 'Trinity Shrine',
    'Spiritual Vessel': 'Spiritual Shrine',
    'Eerie Vessel': 'Eerie Shrine',
    'Enchanted Vessel': 'Enchanted Shrine',
    'Shimmering Vessel': 'Shimmering Shrine',
    'Magical Vessel': 'Magical Shrine',
    'Abandoned Vessel': 'Abandoned Shrine'
}

IGNORED_ITEMS = [
    'Apple',
    'Horadric Cube',
    'Minor Healing Potion',
    'Light Healing Potion',
    'Healing Potion',
    'Greater Healing Potion',
    'Super Healing Potion',
    'Minor Mana Potion',
    'Light Mana Potion',
    'Mana Potion',
    'Greater Mana Potion',
    'Super Mana Potion',
    'Rejuvenation Potion',
    'Full Rejuvenation Potion',
    'Ring',
    'Amulet',
    'Catalyst of Disenchantment',
    'Catalyst of Learning',
    'Signet of Gold',
    'Greater Signet of Gold',
    'Large Axe (1)',
    'Quilted Armor (1)'
]

RUNEWORDS = [
  'Dawn',
  'Shark',
  'Enyo',
  'Azrael',
  'Void',
  'Oblivion',
  'Berith',
  'Gehenna',
  'Triune',
  'Adramelech',
  'Archangel',
  'Shattered Stone',
  'Banshee',
  'Amok',
  'Shockwave',
  'Hornet',
  'Balance',
  'Nyx',
  'Hive',
  'Phantom',
  'Curse',
  'Typhaon',
  'Stardust',
  'Dead Man\'s Breath',
  'Thammuz',
  'Python',
  'Cyclops',
  'Tynged',
  'Tartarus',
  'Araboth',
  'Tombstone',
  'Faseroptic',
  'Urada',
  'Minefield',
  'Instinct',
  'Sabertooth',
  'Midas\' Touch',
  'Myrmidon',
  'Asymptomatic',
  'Endor',
  'Atlacamani',
  'Seed of Conflict',
  'Solarion',
  'King\'s Blood',
  'Rattus',
  'Malicicle',
  'Demhe',
  'Arachnophilia',
  'Calypso',
  'Neurogenesis',
  'Pax Mystica',
  'Hadad',
  'Summanus',
  'Akhenaten',
  'Ljosalf',
  'Aes Dana',
  'Elverfolk',
  'Erilaz',
  'Zodiac',
  'Kyrie',
  'Hand of Frost',
  'Prophecy',
  'Bane',
  'Judas',
  'Path',
  'Jokulmorder',
  'Gabriel',
  'Durga',
  'Galdr',
  'Apostasy',
  'Oris\' Herald',
  'Raid',
  'Hastata',
  'Haste',
  'Hastilude',
  'Hastur',
  'Hastin',
  'Fleshbane',
  'Patriot',
  'Chrysopelea',
  'Dajjal',
  'Quantum',
  'Myriad',
  'Naiad',
  'Burlesque',
  'Tau',
  'Dead Star',
  'Cheetah',
  'Fennec',
  'Manitou',
  'Raptor',
  'Thundercloud',
  'Kodiak',
  'Dragon Seed',
  'Aspect',
  'Corsair',
  'Ice Breaker',
  'Eris',
  'Colliding Worlds',
  'Manta',
  'Cecaelia',
  'Arnazeus Pinnacle',
  'Aegina',
  'Titanomachia',
  'Sankara',
  'Rusalka',
  'Evanescence',
  'Freybug',
  'Flame',
  'Scar',
  'Firefly',
  'Trishula',
  'Herfjotur',
  'Stalactite',
  'Specter',
  'Askari Device',
  'Shedim',
  'Carabosse',
  'Fiend',
  'Riot',
  'Judge',
  'Choronzon',
  'Anarchy',
  'Hail',
  'Nahemah',
  'Joker',
  'Perfection',
  'Khattak',
  'Shamo',
  'Hieros Gamos',
  'Lataif-as-Sitta',
  'Oniwaka',
  'Blooddancer',
  'Ram',
  'Essus',
  'Thunderbird',
  'Gharaniq',
  'Savitr',
  'Skarn',
  'Anak',
  'Khan',
  'Lahmu',
  'Kahless',
  'Gilgamesh',
  'El\'druin',
  'Wolfsangel',
  'Soldier of Light',
  'Peacock',
  'Lynx',
  'Sylvanshine',
  'Tarqeq',
  'Cernunnos',
  'Raudna',
  'Dirge',
  'Amphibian',
  'Ocean',
  'Samhain',
  'Augur',
  'Lincos',
  'Laadan',
  'Lojban',
  'Loxian',
  'Hermanubis',
  'Fiacla-Gear\'s Weathervane',
  'Black Cat',
  'Mantra',
  'Lemuria',
  'Chthon',
  'Eventide',
  'Inti',
  'Leviathan',
  'Tzeentch',
  'Bartuc\'s Eye',
  'Loa',
  'Jinx',
  'Misery',
  'Seid',
  'Roc',
  'Mkodos',
  'Cut',
  'Deep Water',
  'Eurynome',
  'Ladon',
  'Hali',
  'Dagda',
  'Santa Compana',
  'Styx',
  'Xazax',
  'Koan',
  'Ghoul',
  'Dead Ringer',
  'Ngozi',
  'Semhazai',
  'Krypteia',
  'Doomguard',
  'Genie',
  'Atlantis',
  'Aether',
  'Crucible',
  'Kronos',
  'Rhea',
  'Force of Mind',
  'Ensi',
  'Nehushtan',
  'Resheph',
  'Taqiyya',
  'Orisha',
  'Rex Deus',
  'Jaguar',
  'Hadriel\'s Protector',
  'Jihad',
  'Intifada',
  'Lammasu',
  'Quaoar',
  'Takfir',
  'Brahman',
  'Oriflamme',
  'Skilt en Vriend',
  'Judgement',
  'Circe',
  'Ker',
  'Vertigo',
  'Gravastar',
  'Kabbalah',
  'Hestia',
  'Kallisti',
  'Sauron',
  'Helgrotha',
  'Inanna',
  'Brocken',
  'Grace',
  'Khany',
  'Shaula',
  'Sway of the Stars',
  'Dark Exile',
  'Rebel',
  'Lumen Arcana',
  'Paaliaq',
  'Victory\n(Median XL - 6 years)',
  'Thelema',
  'Cathedral',
  'Mirage',
  'Dragonheart',
  'Erawan',
  'Unity',
  'Linga Sharira',
  'Pygmalion',
  'Eternal\nMedian 2005-2012\nThanks everyone!',
  'Hellfire Plate',
  'Summit',
  'Cannonball',
  'Ra',
  'Alchemy',
  'Dreadlord',
  'Bogspitter',
  'Eidolon',
  'Amanita',
  'Thundercap',
  'Checkmate',
  'Sphinx',
  'Lily',
  'Eulenspiegel',
  'Wintermute',
  'Indigo',
  'Rathma\'s Blessing',
  'Geas',
  'Pharaoh',
  'Nomad',
  'Goddess',
  'Kodo',
  'Wall of Fire',
  'Avatar',
  'Derweze',
  'Khalim\'s Protector',
  'Rainbow',
  'Prodigy',
  'Fuse',
  'Pulsa Dinura',
  'Truce',
  'Dyaus Pita',
  'Ahriman',
  'Nero',
  'Lysra',
  'Iblis',
  'Mercy',
  'Brawl',
  'Kali',
  'Aiwass',
  'Skald',
  'Icarus',
  'Drekavac',
  'Snowsquall',
  'Retribution',
  'Knave',
  'Epicenter',
  'Outlaw',
  'Ginfaxi',
  'Craton',
  'Megalith',
  'Nephilim',
  'Hibagon',
  'Riptide',
  'Wind Runner',
  'Stata Mater',
  'Bona Dea',
  'Amaterasu',
  'Siegfried',
  'Cambion',
  'Lohengrin',
  'Unicorn',
  'Shaheeda',
  'Eaglehorn Mask',
  'Edda',
  'Lion',
  'Eloi',
  'Nix',
  'Ea',
  'Eos',
  'Heart of Skovos',
  'Afrit',
  'Rahab',
  'Iambe',
  'Ligeia',
  'Dar-Al-Harb',
  'Scorched Earth',
  'Orchid',
  'Shadowsteps',
  'Algiz',
  'Nasrudin',
  'Ekam',
  'Fawkes',
  'Sagarmatha',
  'Morthwyrtha',
  'Wodziwob',
  'Greisen',
  'Force Shock',
  'Enmerkar',
  'Warpath',
  'Gauntlet',
  'Huracan',
  'E-Engur-A',
  'Tonatiuh',
  'Triune\'s Blessing',
  'Aegipan',
  'Nezha',
  'Natha',
  'Norma',
  'Grove',
  'Slyph',
  'Nigra',
  'Nature\'s Grace',
  'Cube',
  'Warlock',
  'Nahual',
  'Lorelei',
  'Quimbanda',
  'Wyrm',
  'Hecatomb',
  'Twisted Mind',
  'Ilmatar',
  'Hierodule',
  'Crusade',
  'Surya',
  'Malakbel',
  'Rotundjere',
  'Battle Rage',
  'Asmodai',
  'Sangreal',
  'Zohar',
  'Asclepion',
  'Amaymon',
  'Myrrhbearer',
  'Lightwell',
  'Lyrannikin',
  'Kundalini',
  'Demeter',
  'Curandera',
  'Astarte',
  'Oracle',
  'Vanity',
  'Comaetho',
  'Venefica',
  'Cassilda',
  'Space Dementia',
  'Dawn',
  'Shark',
  'Enyo',
  'Azrael',
  'Void',
  'Banshee',
  'Amok',
  'Shockwave',
  'Hornet',
  'Balance',
  'Nyx',
  'Hive',
  'Thammuz',
  'Python',
  'Cyclops',
  'Instinct',
  'Myrmidon',
  'Endor',
  'King\'s Blood',
  'Demhe',
  'Pax Mystica',
  'Hadad',
  'Summanus',
  'Akhenaten',
  'Ljosalf',
  'Prophecy',
  'Bane',
  'Judas',
  'Path',
  'Raid',
  'Hastata',
  'Haste',
  'Patriot',
  'Chrysopelea',
  'Dajjal',
  'Quantum',
  'Cheetah',
  'Fennec',
  'Manitou',
  'Aspect',
  'Corsair',
  'Ice Breaker',
  'Aegina',
  'Titanomachia',
  'Scar',
  'Firefly',
  'Shedim',
  'Carabosse',
  'Fiend',
  'Riot',
  'Judge',
  'Khattak',
  'Shamo',
  'Ram',
  'Essus',
  'Thunderbird',
  'Gharaniq',
  'Peacock',
  'Lynx',
  'Sylvanshine',
  'Ocean',
  'Samhain',
  'Augur',
  'Lincos',
  'Black Cat',
  'Mantra',
  'Lemuria',
  'Chthon',
  'Loa',
  'Jinx',
  'Misery',
  'Deep Water',
  'Eurynome',
  'Ladon',
  'Koan',
  'Ghoul',
  'Genie',
  'Atlantis',
  'Aether',
  'Ensi',
  'Nehushtan',
  'Resheph',
  'Jihad',
  'Intifada',
  'Lammasu',
  'Quaoar',
  'Circe',
  'Ker',
  'Vertigo',
  'Gravastar',
  'Inanna',
  'Brocken',
  'Rebel',
  'Lumen Arcana',
  'Paaliaq',
  'Victory\n(Median XL - 6 years)',
  'Thelema',
  'Cathedral',
  'Mirage',
  'Natasha\'s Legacy',
  'Summit',
  'Cannonball',
  'Ra',
  'Alchemy',
  'Sphinx',
  'Lily',
  'Geas',
  'Pharaoh',
  'Nomad',
  'Goddess',
  'Rainbow',
  'Prodigy',
  'Fuse',
  'Iblis',
  'Mercy',
  'Brawl',
  'Kali',
  'Aiwass',
  'Epicenter',
  'Outlaw',
  'Ginfaxi',
  'Craton',
  'Stata Mater',
  'Bona Dea',
  'Amaterasu',
  'Siegfried',
  'Edda',
  'Afrit',
  'Rahab',
  'Iambe',
  'Ligeia',
  'Algiz',
  'Nasrudin',
  'Ekam',
  'Fawkes',
  'Enmerkar',
  'Warpath',
  'Aegipan',
  'Nezha',
  'Natha',
  'Cube',
  'Warlock',
  'Ilmatar',
  'Hierodule',
  'Asmodai',
  'Sangreal',
  'Zohar',
  'Lyrannikin',
  'Kundalini',
  'Demeter',
  'Curandera'
]

TRADE_POST_SETS_SECTION = '''[color=#00FF00][size=24]Sets[/size][/color]
[hr][/hr]
{items}'''

TRADE_POST_SU_SECTION = '''[color=#804000][size=24]SU[/size][/color]
[hr][/hr]
{items}
'''

TRADE_POST_SSU_SECTION = '''[color=#804000][size=24]SSU[/size][/color]
[hr][/hr]
{items}
'''

TRADE_POST_SSSU_SECTION = '''[color=#804000][size=24]SSSU[/size][/color]
[hr][/hr]
{items}
'''

TRADE_POST_RUNEWORDS_SECTION = '''[color=#808080][size=24]Runewords[/size][/color]
[hr][/hr]
{items}
'''

TRADE_POST_RAQMOJ_SECTION = '''[color=#804000][size=24]Rings/Amulets/Quivers/MOs/Jewels[/size][/color]
[hr][/hr]
{items}
'''

TRADE_POST_BASES_SECTION = '''[color=#808080][size=24]Bases[/size][/color]
[hr][/hr]
{items}
'''

TRADE_POST_CHARMS_SECTION = '''[color=#FF7F50][size=24]Charms[/size][/color]
[hr][/hr]
{items}
'''

TRADE_POST_TROPHIES_SECTION = '''[color=#FFA500][size=24]Trophies[/size][/color]
[hr][/hr]
{items}
'''

TRADE_POST_MISC_SECTION = '''[color=#FFFFFF][size=24]Misc[/size][/color]
[hr][/hr]
{items}
'''

TRADE_POST_TEMPLATE = '''[color=#FFFF00][size=26]Selling[/size][/color]
[hr][/hr]
{items}
'''

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
            'pastebin_api_key': ''
        }
        self._config = Config.get_conf(self, identifier=134621854878007298)
        self._config.register_global(**default_config)

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
        if not config['pastebin_api_key']:
            await ctx.send(f'Pastebin API key hasn\'t been configured yet. Configure one using `{ctx.prefix}mxl config pastebin_api_key`.')
            return

        if not config['armory_username']:
            await ctx.send(f'Armory account hasn\'t been configured yet. Configure one using `{ctx.prefix}mxl config armory_username/armory_password`.')
            return

        sets = {}
        su = {}
        ssu = {}
        sssu = {}
        amulets = {}
        rings = {}
        jewels = {}
        mos = {}
        quivers = {}
        runewords = {}
        rw_bases = {}
        shrine_bases = {}
        charms = {}
        trophies = {}
        shrines = {}
        other = {}
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
            self._scrape_items(item_dump, sets, su, ssu, sssu, amulets, rings, jewels, mos, quivers, runewords, rw_bases, shrine_bases, charms, trophies, shrines, other)

        if not sets and not su and not ssu and not sssu and not amulets and not rings and not jewels and not mos and not quivers and not runewords and not rw_bases and not shrine_bases and not charms and not shrines and not other:
            await ctx.send('No items found.')
            return

        post = self._generate_trade_post(sets, su, ssu, sssu, amulets, rings, jewels, mos, quivers, runewords, rw_bases, shrine_bases, charms, trophies, shrines, other)
        pastebin_link = await self._create_pastebin(post, f'MXL trade post for characters: {", ".join(characters)}')
        channel = ctx.author.dm_channel or await ctx.author.create_dm()
        if pastebin_link:
            await channel.send(f'Dump successful. Here you go: {pastebin_link}')
            return

        await ctx.send('Couldn\'t create the trade post pastebin - 24h limit is probably reached. Check your DMs.')
        for page in pagify(post):
            await channel.send(embed=discord.Embed(description=page))

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

    def _scrape_items(self, item_dump, sets, su, ssu, sssu, amulets, rings, jewels, mos, quivers, runewords, rw_bases, shrine_bases, charms, trophies, shrines, other):
        for item in item_dump:
            if item.th:
                continue

            item_name = item.span.text
            set_match = re.search('\[([^\]]+)', item.span.text)

            if item_name in IGNORED_ITEMS:
                continue

            if set_match:
                set_name = set_match.group(1)
                item_name = item_name.split('[')[0].strip()

                if set_name not in sets:
                    sets[set_name] = {}

                if item_name not in sets[set_name]:
                    sets[set_name][item_name] = 0

                sets[set_name][item_name] += 1

                continue

            if item_name in SU_ITEMS:
                if item_name not in su:
                    su[item_name] = 0

                su[item_name] += 1
                continue

            if 'Hanfod' in item_name:
                if 'Hanfod Tân' not in su:
                    su['Hanfod Tân'] = 0

                su['Hanfod Tân'] += 1
                continue

            if item_name == 'Jewel':
                if 'Jewel' not in other:
                    other['Jewel'] = 0

                other['Jewel'] += 1
                continue

            if item_name in SSU_ITEMS:
                if item_name not in ssu:
                    ssu[item_name] = 0

                ssu[item_name] += 1
                continue

            if item_name in SSSU_ITEMS:
                if item_name not in sssu:
                    sssu[item_name] = 0

                sssu[item_name] += 1
                continue

            if item_name in RUNEWORDS:
                if item_name not in runewords:
                    runewords[item_name] = 0

                runewords[item_name] += 1
                continue

            if item_name in AMULETS:
                if item_name not in amulets:
                    amulets[item_name] = 0

                amulets[item_name] += 1
                continue

            if item_name in RINGS:
                if item_name not in rings:
                    rings[item_name] = 0

                rings[item_name] += 1
                continue

            if item_name in JEWELS:
                if item_name not in jewels:
                    jewels[item_name] = 0

                jewels[item_name] += 1
                continue

            if item_name in QUIVERS:
                if item_name not in quivers:
                    quivers[item_name] = 0

                quivers[item_name] += 1
                continue

            if item_name in MOS:
                if item_name not in mos:
                    mos[item_name] = 0

                mos[item_name] += 1
                continue

            if item.span['class'][0] == 'color-white' or item.span['class'][0] == 'color-blue':
                dict_entry = item_name + ' [eth]' if '[ethereal]' in item.text else ''.join(item_name.split('Superior '))
                if dict_entry not in rw_bases:
                    rw_bases[dict_entry] = 0

                rw_bases[dict_entry] += 1
                continue

            if item.span['class'][0] == 'color-yellow':
                if item_name not in shrine_bases:
                    shrine_bases[item_name] = 0

                shrine_bases[item_name] += 1
                continue

            if item_name in CHARMS:
                if item_name not in charms:
                    charms[item_name] = 0

                charms[item_name] += 1
                continue

            shrine_match = re.search('Shrine \(([^\)]+)', item_name)
            if shrine_match:
                shrine_name = item_name.split('(')[0].strip()
                amount = int(shrine_match.group(1))
                if shrine_name not in shrines:
                    shrines[shrine_name] = 0

                shrines[shrine_name] += amount / 10
                continue

            if item_name in SHRINE_VESSELS:
                vessel_amount = int((re.search('Quantity: ([0-9]+)', item.find(class_='color-grey').text)).group(1))
                shrine_name = VESSEL_TO_SHRINE[item_name]
                if shrine_name not in shrines:
                    shrines[shrine_name] = 0

                shrines[shrine_name] += vessel_amount
                continue

            if item_name == 'Arcane Cluster':
                crystals_amount = int((re.search('Quantity: ([0-9]+)', item.find(class_='color-grey').text)).group(1))
                if 'Arcane Crystal' not in other:
                    other['Arcane Crystal'] = 0

                other['Arcane Crystal'] += crystals_amount
                continue

            AC_shards_match = re.search('Shards \(([^\)]+)', item_name)
            if AC_shards_match:
                amount = int(AC_shards_match.group(1)) / 5
                if 'Arcane Crystal' not in other:
                    other['Arcane Crystal'] = 0

                other['Arcane Crystal'] += amount
                continue

            if item_name in TROPHIES:
                if item_name not in trophies:
                    trophies[item_name] = 0

                trophies[item_name] += 1
                continue

            if item_name not in other:
                other[item_name] = 0

            other[item_name] += 1

    def _generate_trade_post(self, sets, su, ssu, sssu, amulets, rings, jewels, mos, quivers, runewords, rw_bases, shrine_bases, charms, trophies, shrines, other):
        items = ''
        sets_str = ''
        for set_name, set_items in sets.items():
            sets_str += f'[u][color=#00FF00]{set_name}[/color][/u]\n'
            for item, amount in set_items.items():
                sets_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

            sets_str += '\n'

        if sets_str:
            items += TRADE_POST_SETS_SECTION.format(items = sets_str)

        su_str = ''
        for item, amount in su.items():
            su_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if su_str:
            items += TRADE_POST_SU_SECTION.format(items = su_str)

        ssu_str = ''
        for item, amount in ssu.items():
            ssu_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if ssu_str:
            items += TRADE_POST_SSU_SECTION.format(items = ssu_str)

        sssu_str = ''
        for item, amount in sssu.items():
            sssu_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if sssu_str:
            items += TRADE_POST_SSSU_SECTION.format(items = sssu_str)

        runewords_str = ''
        for item, amount in runewords.items():
            runewords_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if runewords_str:
            items += TRADE_POST_RUNEWORDS_SECTION.format(items = runewords_str)

        raqmoj_str = ''
        for item, amount in rings.items():
            raqmoj_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if rings:
            raqmoj_str += '\n'

        for item, amount in amulets.items():
            raqmoj_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if amulets:
            raqmoj_str += '\n'

        for item, amount in quivers.items():
            raqmoj_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if quivers:
            raqmoj_str += '\n'

        for item, amount in mos.items():
            raqmoj_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if mos:
            raqmoj_str += '\n'

        for item, amount in jewels.items():
            raqmoj_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if raqmoj_str:
            items += TRADE_POST_RAQMOJ_SECTION.format(items = raqmoj_str)

        bases_str = ''
        for item, amount in rw_bases.items():
            bases_str += f'[color=#808080]{item}[/color] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        for item, amount in shrine_bases.items():
            bases_str += f'[color=#FFFF00]{item}[/color] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if bases_str:
            items += TRADE_POST_BASES_SECTION.format(items = bases_str)

        charms_str = ''
        for item, amount in charms.items():
            charms_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if charms_str:
            items += TRADE_POST_CHARMS_SECTION.format(items = charms_str)

        trophies_str = ''
        for item, amount in trophies.items():
            trophies_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if trophies_str:
            items += TRADE_POST_TROPHIES_SECTION.format(items = trophies_str)

        other_str = ''
        for item, amount in shrines.items():
            other_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if shrines:
            other_str += '\n'

        for item, amount in other.items():
            other_str += f'[item]{item}[/item] x{amount}\n' if amount > 1 else f'[item]{item}[/item]\n'

        if other_str:
            items += TRADE_POST_MISC_SECTION.format(items = other_str)

        return TRADE_POST_TEMPLATE.format(items = items)

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
