import requests
from bs4 import BeautifulSoup
import pprint

def clean(span_text):
    span_text = span_text.replace('\n', '')
    return span_text.replace('\t', '')

if __name__ == "__main__":
    response = requests.get('https://docs.median-xl.com/doc/items/sets')
    soup = BeautifulSoup(response.text)
    tables = soup.find_all('table')
    result = {}
    
    for table in tables:
        row = table.find_all('tr')[1]

        spans = row.td.find_all('span')
        set_name = clean(spans[0].text)
        for span in spans[1:]:
            if span.text.find('Set Bonus') != -1:
                break

            result[clean(span.text)] = set_name

    pprint.pprint(result, indent=4)