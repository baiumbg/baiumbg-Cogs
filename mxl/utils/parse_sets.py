import requests
from bs4 import BeautifulSoup

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
        print(spans[0])
        print(spans[1])
        print(spans[2])
        print(spans[3])
        print(spans[4])
        print(spans[5])
        set_name = clean(spans[0].text)
        result[clean(spans[1].text)] = set_name
        result[clean(spans[2].text)] = set_name
        result[clean(spans[3].text)] = set_name
        result[clean(spans[4].text)] = set_name
        result[clean(spans[5].text)] = set_name

    print(str(result))