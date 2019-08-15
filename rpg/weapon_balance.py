from items import DEFAULT_WEAPONS

if __name__ == "__main__":
    for weapon in DEFAULT_WEAPONS:
        average_damage = (weapon['high'] + weapon['low']) / 2
        avg_hit = (average_damage * 2 * weapon['crit_chance'] + average_damage * (1 - weapon['crit_chance'])) * weapon['hit_chance']
        print(f"Name: {weapon['name']}\nAverage damage: {avg_hit}\n")