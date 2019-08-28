DEFAULT_WEAPONS = [
    {
        'name': 'fist',
        'cost': 0,
        'low': 1,
        'high': 3,
        'crit_chance': 0.05,
        'hit_chance': 0.9,
        'type': 'strength',
        'attack_template': "{a} drives their {o} into {d}'s {b} for {delta} damage!",
        'block_template': "{a} attempts to drive their {o} into {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} drives their {o} with all their might into {d}'s {b} and deal {delta} damage!",
        'miss_template': "{a} attempts to drive their {o} into {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'axe',
        'cost': 100,
        'low': 2,
        'high': 5,
        'crit_chance': 0.08,
        'hit_chance': 0.91,
        'type': 'strength',
        'attack_template': "{a} swings their {o} into {d}'s {b} for {delta} damage!",
        'block_template': "{a} swings their {o} at {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} swings their {o} with exceptional fury into {d}'s {b} and deal {delta} damage!",
        'miss_template': "{a} attempts to swing their {o} at {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'scimitar',
        'cost': 100,
        'low': 3,
        'high': 5,
        'crit_chance': 0.05,
        'hit_chance': 0.82,
        'type': 'strength',
        'attack_template': "{a} swings their {o} into {d}'s {b} for {delta} damage!",
        'block_template': "{a} swings their {o} at {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} swings their {o} with exceptional fury into {d}'s {b} and deal {delta} damage!",
        'miss_template': "{a} attempts to swing their {o} at {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'buzzsaw',
        'cost': 100,
        'low': 2,
        'high': 6,
        'crit_chance': 0.04,
        'hit_chance': 0.82,
        'type': 'strength',
        'attack_template': "{a} drives their {o} into {d}'s {b} for {delta} damage!",
        'block_template': "{a} tries to drive their {o} into {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} drives their {o} deep into {d}'s {b} and deal {delta} damage!",
        'miss_template': "{a} attempts to drive their {o} into {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'chainsaw',
        'cost': 200,
        'low': 4,
        'high': 6,
        'crit_chance': 0.05,
        'hit_chance': 0.9,
        'type': 'strength',
        'attack_template': "{a} swings their {o} at {d}'s {b} for {delta} damage!",
        'block_template': "{a} swings their {o} at {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} swings their {o} at {d}'s {b}, completely cutting it off! {d} takes {delta} damage!",
        'miss_template': "{a} attempts to swing their {o} at {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'broadsword',
        'cost': 300,
        'low': 8,
        'high': 10,
        'crit_chance': 0.04,
        'hit_chance': 0.64,
        'type': 'strength',
        'attack_template': "{a} swings their {o} at {d}'s {b} for {delta} damage!",
        'block_template': "{a} swings their {o} at {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} swings their {o} at {d}'s {b}, completely cutting it off! {d} takes {delta} damage!",
        'miss_template': "{a} attempts to swing their {o} at {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'falchion',
        'cost': 300,
        'low': 4,
        'high': 7,
        'crit_chance': 0.09,
        'hit_chance': 1,
        'type': 'strength',
        'attack_template': "{a} swings their {o} into {d}'s {b} for {delta} damage!",
        'block_template': "{a} swings their {o} at {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} swings their {o} with exceptional fury into {d}'s {b} and deal {delta} damage!",
        'miss_template': "{a} attempts to swing their {o} at {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'dagger',
        'cost': 100,
        'low': 1,
        'high': 3,
        'crit_chance': 0.72,
        'hit_chance': 1,
        'type': 'dexterity',
        'attack_template': "{a} swings their {o} at {d}'s {b} for {delta} damage!",
        'block_template': "{a} swings their {o} at {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} drives their {o} deep into {d}'s {b}. They deal {delta} damage!",
        'miss_template': "{a} attempts to drive their {o} into {d}'s {b}, but they completely miss!"
    },
    {
        'name': 'slingshot',
        'cost': 100,
        'low': 2,
        'high': 3,
        'crit_chance': 0.72,
        'hit_chance': 0.8,
        'type': 'dexterity',
        'attack_template': "{a} fires a pebble using their {o} at {d}'s {b} for {delta} damage!",
        'block_template': "{a} fires their {o} at {d}'s {b}, but the pebble is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} fires a large pebble using their {o} directly aimed at {d}'s {b}. It deals {delta} damage!",
        'miss_template': "{a} attempts to launch a pebble using their {o} at {d}'s {b}, but it completely misses!"
    },
    {
        'name': 'raygun',
        'cost': 200,
        'low': 2,
        'high': 6,
        'crit_chance': 0.18,
        'hit_chance': 1,
        'type': 'dexterity',
        'attack_template': "{a} shoots their {o} at {d}'s {b} for {delta} damage!",
        'block_template': "{a} shoots their {o} at {d}'s {b}, but the projectile is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} blows a hole through {d}'s {b} using their {o} and deal {delta} damage!",
        'miss_template': "{a} attempts to shoot their {o} at {d}'s {b}, but the projectile completely misses!"
    },
    {
        'name': 'flamethrower',
        'cost': 200,
        'low': 2,
        'high': 7,
        'crit_chance': 0,
        'hit_chance': 1,
        'type': 'dexterity',
        'attack_template': "{a} burns {d}'s {b} using their {o} for {delta} damage!",
        'block_template': "{a} tries to burn {d}'s {b} using their {o}, but the flames are completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} burns {d}'s {b} into a crisp using their {o} and deal {delta} damage!",
        'miss_template': "{a} attempts to burn {d}'s {b} using their {o}, but the flames completely miss!"
    },
    {
        'name': 'crossbow',
        'cost': 200,
        'low': 3,
        'high': 5,
        'crit_chance': 0.18,
        'hit_chance': 1,
        'type': 'dexterity',
        'attack_template': "{a} shoots their {o} into {d}'s {b} for {delta} damage!",
        'block_template': "{a} shoots their {o} into {d}'s {b}, but the arrow is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} completely pierces {d}'s {b} with an arrow from their {o} and deal {delta} damage!",
        'miss_template': "{a} attempts to shoot their {o} into {d}'s {b}, but the arrow completely misses!"
    },
    {
        'name': 'railgun',
        'cost': 300,
        'low': 5,
        'high': 7,
        'crit_chance': 0,
        'hit_chance': 1,
        'type': 'dexterity',
        'attack_template': "{a} shoots their {o} at {d}'s {b} for {delta} damage!",
        'block_template': "{a} shoots their {o} into {d}'s {b}, but the projectile is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} shoots a hole straight through {d}'s {b} with their {o} and deal {delta} damage!",
        'miss_template': "{a} attempts to shoot their {o} at {d}'s {b}, but the projectile completely misses!"
    },
    {
        'name': 'ballista',
        'cost': 300,
        'low': 5,
        'high': 7,
        'crit_chance': 0.1,
        'hit_chance': 0.91,
        'type': 'dexterity',
        'attack_template': "{a} shoots their {o} at {d}'s {b} for {delta} damage!",
        'block_template': "{a} shoots their {o} into {d}'s {b}, but the bolt is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} shoots a huge bolt straight through {d}'s {b} and deal {delta} damage!",
        'miss_template': "{a} attempts to shoot their {o} into {d}'s {b}, but the bolt completely misses!"
    },
    {
        'name': 'catapult',
        'cost': 300,
        'low': 4,
        'high': 7,
        'crit_chance': 0.21,
        'hit_chance': 0.9,
        'type': 'dexterity',
        'attack_template': "{a} hurls a boulder at {d}'s {b} using their {o} for {delta} damage!",
        'block_template': "{a} hurls a boulder at {d}'s {b} using their {o}, but it is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} completely smashes {d}'s {b} with a huge boulder from their {o}. They take {delta} damage!",
        'miss_template': "{a} attempts to hurl a boulder at {d}'s {b}, but it completely misses!"
    },
    {
        'name': 'cannon',
        'cost': 300,
        'low': 3,
        'high': 6,
        'crit_chance': 0.4,
        'hit_chance': 0.95,
        'type': 'dexterity',
        'attack_template': "{a} fires a cannonball at {d}'s {b} for {delta} damage!",
        'block_template': "{a} fires a cannonball at {d}'s {b}, but it is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} fires a cannonball at {d}'s {b}, completely obliterating it! {d} takes {delta} damage!",
        'miss_template': "{a} attempts to fire a cannonball at {d}'s {b}, but it completely misses!"
    },
    {
        'name': 'mortar',
        'cost': 300,
        'low': 2,
        'high': 5,
        'crit_chance': 0.73,
        'hit_chance': 1,
        'type': 'dexterity',
        'attack_template': "{a} fires an explosive shell at {d}'s {b} for {delta} damage!",
        'block_template': "{a} fires an explosive shell at {d}'s {b}, but it is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} fires an explosive shell at {d}'s {b}, utterly deleting it! {d} takes {delta} damage!",
        'miss_template': "{a} attempts to fire an explosive shell at {d}'s {b}, but it completely misses!"
    },
    {
        'name': 'naginata',
        'cost': 300,
        'low': 4,
        'high': 6,
        'crit_chance': 0.5,
        'hit_chance': 0.8,
        'type': 'dexterity',
        'attack_template': "{a} drives their {o} into {d}'s {b} for {delta} damage!",
        'block_template': "{a} tries to drive their {o} into {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} drives their {o} straight through {d}'s {b} and deal {delta} damage!",
        'miss_template': "{a} attempts to drive their {o} into {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'lance',
        'cost': 300,
        'low': 3,
        'high': 6,
        'crit_chance': 0.6,
        'hit_chance': 0.84,
        'type': 'dexterity',
        'attack_template': "{a} drives their {o} into {d}'s {b} for {delta} damage!",
        'block_template': "{a} tries to drive their {o} into {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} drives their {o} straight through {d}'s {b} and deal {delta} damage!",
        'miss_template': "{a} attempts to drive their {o} into {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'katana',
        'cost': 300,
        'low': 5,
        'high': 7,
        'crit_chance': 0.15,
        'hit_chance': 0.87,
        'type': 'dexterity',
        'attack_template': "{a} swings their {o} at {d}'s {b} for {delta} damage!",
        'block_template': "{a} swings their {o} at {d}'s {b}, but the attack is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} swings their {o} at {d}'s {b}, completely cutting it off! {d} takes {delta} damage!",
        'miss_template': "{a} attempts to swing their {o} at {d}'s {b}, but the attack completely misses!"
    },
    {
        'name': 'fireball spellbook',
        'cost': 100,
        'low': 3,
        'high': 4,
        'crit_chance': 0.05,
        'hit_chance': 0.93,
        'type': 'intelligence',
        'attack_template': "{a} opens up their {o} and launches a ball of flame at {d}'s {b}, dealing {delta} damage!",
        'block_template': "{a} opens up their {o} and launches a ball of flame at {d}'s {b}, but the spell is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} opens up their {o} and conjures up an enormous ball of fire, launching it with full force at {d}'s {b}! It deals {delta} damage!",
        'miss_template': "{a} opens up their {o} and launches a ball of flame at {d}'s {b}, but completely misses!"
    },
    {
        'name': 'magic wand',
        'cost': 100,
        'low': 3,
        'high': 5,
        'crit_chance': 0.09,
        'hit_chance': 0.79,
        'type': 'intelligence',
        'attack_template': "{a} fires a magical projectile from their {o} aimed at {d}'s {b}! It hits, dealing {delta} damage!",
        'block_template': "{a} fires a magical projectile from their {o} aimed at {d}'s {b}, but it's completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} fires a magical projectile from their {o} at the speed of light! It pierces through {d}'s {b}, dealing {delta} damage!",
        'miss_template': "{a} fires a magical projectile from their {o} aimed at {d}'s {b}, but it completely misses!"
    },
    {
        'name': 'lightning bolt spellbook',
        'cost': 200,
        'low': 1,
        'high': 8,
        'crit_chance': 0.1,
        'hit_chance': 0.95,
        'type': 'intelligence',
        'attack_template': "{a} opens up their {o} and sends a bolt of lightning straight into {d}'s {b}, dealing {delta} damage!",
        'block_template': "{a} opens up their {o} and sends a bolt of lightning straights into {d}'s {b}, but the spell is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} opens up their {o} and conjures up an enormous lightning storm, striking {d}'s {b} multiple times! The storm deals {delta} damage!",
        'miss_template': "{a} opens up their {o} and sends a bolt of lightning aimed at {d}'s {b}, but it completely misses!"
    },
    {
        'name': 'magic scepter',
        'cost': 200,
        'low': 3,
        'high': 5,
        'crit_chance': 0.24,
        'hit_chance': 0.95,
        'type': 'intelligence',
        'attack_template': "{a} fires a magical projectile from their {o} aimed at {d}'s {b}! It hits, dealing {delta} damage!",
        'block_template': "{a} fires a magical projectile from their {o} aimed at {d}'s {b}, but it's completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} fires a magical projectile from their {o} at the speed of light! It pierces through {d}'s {b}, dealing {delta} damage!",
        'miss_template': "{a} fires a magical projectile from their {o} aimed at {d}'s {b}, but it completely misses!"
    },
    {
        'name': 'bone spear spellbook',
        'cost': 300,
        'low': 4,
        'high': 7,
        'crit_chance': 0.3,
        'hit_chance': 0.85,
        'type': 'intelligence',
        'attack_template': "{a} opens up their spellbook and sends a conjured bone spear straight into {d}'s {b}, dealing {delta} damage!",
        'block_template': "{a} opens up their spellbook and sends a conjured bone spear straight into {d}'s {b}, but the spell is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} opens up their spellbook and conjures up an enormous bone spear, made out of mammoth bone, sending it straight through {d}'s {b}! It deals {delta} damage!",
        'miss_template': "{a} opens up their spellbook and sends a conjured bone spear aimed at {d}'s {b}, but it completely misses!"
    },
    {
        'name': 'magic staff',
        'cost': 300,
        'low': 5,
        'high': 8,
        'crit_chance': 0.05,
        'hit_chance': 0.88,
        'type': 'intelligence',
        'attack_template': "{a} fires a magical projectile from their {o} aimed at {d}'s {b}! It hits, dealing {delta} damage!",
        'block_template': "{a} fires a magical projectile from their {o} aimed at {d}'s {b}, but it's completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} fires a magical projectile from their {o} at the speed of light! It pierces through {d}'s {b}, dealing {delta} damage!",
        'miss_template': "{a} fires a magical projectile from their {o} aimed at {d}'s {b}, but it completely misses!"
    },
    {
        'name': 'necronomicon',
        'cost': 300,
        'low': 4,
        'high': 9,
        'crit_chance': 0.1,
        'hit_chance': 0.85,
        'type': 'intelligence',
        'attack_template': "{a} opens up their {o} and raises a nearby gremlin from the dead! It rushes towards {d}'s {b}, hitting them for {delta} damage!",
        'block_template': "{a} opens up their {o} and raises a nearby gremlin from the dead! It rushes towards {d}'s {b}, but its hit is completely blocked by {d}'s {ap}!",
        'crit_template': "Critical hit! {a} opens up their {o} and raises enormous bone golem from the nearby graveyard! It rushes towards {d} and absolutely decimates their {b}! {d} takes {delta} damage!",
        'miss_template': "{a} opens up their {o} and raises a nearby gremlin from the dead! It rushes towards {d}'s {b}, but completely misses its attack!"
    },
]

DEFAULT_HELMETS = [
    {
        'name': 'generic cap',
        'cost': 0,
        'armor': 0
    },
    {
        'name': 'leather cap',
        'cost': 20,
        'armor': 1
    },
    {
        'name': 'wooden cap',
        'cost': 40,
        'armor': 2
    },
    {
        'name': 'iron cap',
        'cost': 60,
        'armor': 3
    }
]

DEFAULT_BODY_ARMORS = [
    {
        'name': 'cloth vest',
        'cost': 0,
        'armor': 0
    },
    {
        'name': 'leather vest',
        'cost': 20,
        'armor': 1
    },
    {
        'name': 'wooden armor',
        'cost': 40,
        'armor': 2
    },
    {
        'name': 'iron breastplate',
        'cost': 60,
        'armor': 3
    }
]

DEFAULT_GLOVES = [
    {
        'name': 'cloth gloves',
        'cost': 0,
        'armor': 0
    },
    {
        'name': 'leather gloves',
        'cost': 20,
        'armor': 1
    },
    {
        'name': 'wooden gloves',
        'cost': 40,
        'armor': 2
    },
    {
        'name': 'iron gauntlets',
        'cost': 60,
        'armor': 3
    }
]

DEFAULT_BOOTS = [
    {
        'name': 'cloth sandals',
        'cost': 0,
        'armor': 0
    },
    {
        'name': 'leather boots',
        'cost': 20,
        'armor': 1
    },
    {
        'name': 'wooden boots',
        'cost': 40,
        'armor': 2
    },
    {
        'name': 'iron greaves',
        'cost': 60,
        'armor': 3
    }
]

DEFAULT_PANTS = [
    {
        'name': 'cloth leggings',
        'cost': 0,
        'armor': 0
    },
    {
        'name': 'leather leggings',
        'cost': 20,
        'armor': 1
    },
    {
        'name': 'wooden pants',
        'cost': 40,
        'armor': 2
    },
    {
        'name': 'iron tassets',
        'cost': 60,
        'armor': 3
    }
]

DEFAULT_SHOULDERS = [
    {
        'name': 'cloth shoulderpads',
        'cost': 0,
        'armor': 0
    },
    {
        'name': 'leather shoulderpads',
        'cost': 20,
        'armor': 1
    },
    {
        'name': 'wooden shoulderpads',
        'cost': 40,
        'armor': 2
    },
    {
        'name': 'iron pauldrons',
        'cost': 60,
        'armor': 3
    }
]

DEFAULT_HEALING_ITEMS = [
    {
        'name': 'apple',
        'cost': 0,
        'low': 2,
        'high': 3,
        'template': '{a} decides to take a bite out of their {o} instead of attacking. They heal for {delta}!'
    },
    {
        'name': 'morphine',
        'cost': 100,
        'low': 3,
        'high': 4,
        'template': '{a} decides to inject himself with some of their {o} instead of attacking. They heal for {delta}!'
    },
    {
        'name': 'cake',
        'cost': 100,
        'low': 2,
        'high': 5,
        'template': '{a} decides to eat some of their {o} instead of attacking. They heal for {delta}!'
    },
    {
        'name': 'joint',
        'cost': 200,
        'low': 4,
        'high': 6,
        'template': '{a} decides to smoke a fat {o} instead of attacking. They heal for {delta}!'
    },
    {
        'name': 'nanites',
        'cost': 200,
        'low': 3,
        'high': 7,
        'template': '{a} decides to inject himself with some of their {o} instead of attacking. They heal for {delta}!'
    },
    {
        'name': 'unicorn piss',
        'cost': 300,
        'low': 6,
        'high': 8,
        'template': '{a} decides to drink some of their {o} instead of attacking. They heal for {delta}!'
    },
    {
        'name': 'goon wine',
        'cost': 300,
        'low': 5,
        'high': 9,
        'template': '{a} decides to drink some of their {o} instead of attacking. They heal for {delta}!'
    }
]

ARMOR_PIECES = [
    'helmet',
    'shoulders',
    'body_armor',
    'pants',
    'gloves',
    'boots'
]

ARMOR_PIECE_TO_BODY_PARTS = {
    'helmet': [
        'head',
        'throat',
        'neck',
        'jugular',
        'forehead',
        'left eye',
        'right eye',
        'nose',
        'face'
    ],
    'shoulders': [
        'left shoulder',
        'right shoulder',
        'left humerus',
        'right humerus'
    ],
    'body_armor': [
        'ribcage',
        'spleen',
        'kidney',
        'abdomen',
        'chest',
        'stomach',
        'solar plexus'
    ],
    'pants': [
        'left leg',
        'right leg',
        'balls',
        'left knee',
        'right knee'
    ],
    'gloves': [
        'left wrist',
        'right wrist',
        'left palm',
        'right palm',
        'left thumb',
        'right thumb'
    ],
    'boots': [
        'left shin',
        'right shin',
        'left talus',
        'right talus',
        'left heel',
        'right heel',
        'left toe',
        'right toe'
    ]
}

DEFAULT_ITEMS = {
    'helmet': DEFAULT_HELMETS,
    'body_armor': DEFAULT_BODY_ARMORS,
    'pants': DEFAULT_PANTS,
    'shoulders': DEFAULT_SHOULDERS,
    'gloves': DEFAULT_GLOVES,
    'boots': DEFAULT_BOOTS,
    'healing_item': DEFAULT_HEALING_ITEMS,
    'weapon': DEFAULT_WEAPONS
}

DEFAULT_EQUIPPED = {
    'helmet': DEFAULT_HELMETS[0]['name'],
    'body_armor': DEFAULT_BODY_ARMORS[0]['name'],
    'pants': DEFAULT_PANTS[0]['name'],
    'shoulders': DEFAULT_SHOULDERS[0]['name'],
    'gloves': DEFAULT_GLOVES[0]['name'],
    'boots': DEFAULT_BOOTS[0]['name'],
    'healing_item': DEFAULT_HEALING_ITEMS[0]['name'],
    'weapon': DEFAULT_WEAPONS[0]['name']
}