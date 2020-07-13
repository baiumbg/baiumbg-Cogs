import requests
from bs4 import BeautifulSoup
import pprint
import re

set_subname_regex = re.compile(r'\(.*\)')

def clean(span_text):
    span_text = span_text.replace('\n', '').replace('\t', '')
    return set_subname_regex.sub('', span_text)

if __name__ == "__main__":
    response = requests.get('https://docs.median-xl.com/doc/items/sets')
    soup = BeautifulSoup(response.text)
    tables = soup.find_all('table')
    result = {}
    
    for table in tables:
        row = table.find_all('tr')[0]

        spans = row.td.find_all('span')
        set_name = clean(spans[0].text)
        for span in spans[1:]:
            if span.text.find('Set Bonus') != -1:
                break

            result[clean(span.text)] = set_name

    pprint.pprint(result, indent=4)