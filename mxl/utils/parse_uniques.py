import requests
from bs4 import BeautifulSoup
import pprint

def clean(span_text):
    span_text = span_text.replace('\n', '')
    return span_text.replace('\t', '')

def all_items_before_amulets(tag):
    return tag.name == 'table' and tag.find_previous_sibling('p').text.find('Amulets') == -1 \
        and tag.find_previous_sibling('p').text.find('Rings') == -1 \
        and tag.find_previous_sibling('p').text.find('Jewels') == -1 \
        and tag.find_previous_sibling('p').text.find('Arrow Quivers') == -1 \
        and tag.find_previous_sibling('p').text.find('Crossbow Quivers') == -1

def p_contains(string):
    def contains(tag):
        return tag.name == 'p' and string in tag.text
    return contains

def parse_items(soup, category, result):
    table = soup.find(p_contains(category)).find_next_sibling()
    for row in table.find_all('tr'):
        for cell in row.find_all('td')[1:]:
            item_name_element = cell.find(class_='item-unique')
            if not item_name_element:
                continue

            item_name = clean(item_name_element.text)
            result.append(item_name)

if __name__ == "__main__":
    response_sacred = requests.get('https://docs.median-xl.com/doc/items/sacreduniques')
    response_tiered = requests.get('https://docs.median-xl.com/doc/items/tiereduniques')
    soup_sacred = BeautifulSoup(response_sacred.text)
    soup_tiered = BeautifulSoup(response_tiered.text)

    uniques = [[], [], []]
    amulets = []
    rings = []
    jewels = []
    quivers = []
    tables = soup_sacred.find_all(all_items_before_amulets)
    for table in tables:
        #print(table)
        row = table.find_all('tr')[1]

        idx = 0
        for cell in row.find_all('td')[1:]:
            item_name_element = cell.find(class_='item-unique')
            if not item_name_element:
                continue

            item_name = clean(item_name_element.text)
            uniques[idx].append(item_name)
            idx += 1

    parse_items(soup_sacred, 'Amulets', amulets)
    parse_items(soup_tiered, 'Amulets', amulets)
    parse_items(soup_sacred, 'Rings', rings)
    parse_items(soup_tiered, 'Rings', rings)
    parse_items(soup_sacred, 'Jewels', jewels)
    parse_items(soup_tiered, 'Jewels', jewels)
    parse_items(soup_sacred, 'Arrow Quivers', quivers)
    parse_items(soup_tiered, 'Arrow Quivers', quivers)
    parse_items(soup_sacred, 'Crossbow Quivers', quivers)
    parse_items(soup_tiered, 'Crossbow Quivers', quivers)

    # Samael items
    uniques[0].append('Maleficence')
    uniques[1].append('Despondence')
    uniques[2].append('Desolation')
    amulets.append('Celestial Sigil')

    # Other
    rings.append('Sigil of the 7 Deadly Sins')
    rings.append('Assur\'s Bane')

    print('--------------------\nSU\n--------------------')
    pprint.pprint(uniques[0], indent=4)
    print('--------------------\nSSU\n--------------------')
    pprint.pprint(uniques[1], indent=4)
    print('--------------------\nSSSU\n--------------------')
    pprint.pprint(uniques[2], indent=4)
    print('--------------------\nAmulets\n--------------------')
    pprint.pprint(amulets, indent=4)
    print('--------------------\nRings\n--------------------')
    pprint.pprint(rings, indent=4)
    print('--------------------\nJewels\n--------------------')
    pprint.pprint(jewels, indent=4)
    print('--------------------\nQuivers\n--------------------')
    pprint.pprint(quivers, indent=4)