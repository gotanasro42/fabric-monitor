import requests
from bs4 import BeautifulSoup
import json
import datetime

# Konfigurácia kategórií
CATEGORIES = {
    'takoy': [
        {'name': 'Jersey Oskaro (Solid)', 'url': 'https://takoy.de/jersey-oskaro-6001?sort=top'},
        {'name': 'Dizajnový úplet (Design)', 'url': 'https://takoy.de/dizajnovy-uplet?sort=top'},
        {'name': 'Bavlna (Solid)', 'url': 'https://takoy.de/baunwollwebware-einfarbig?sort=top'},
        {'name': 'Softshell (Design)', 'url': 'https://takoy.de/softshell-bedruckt?sort=top'}
    ],
    'stoffe': [
        {'name': 'Jersey (Solid)', 'url': 'https://www.stoffe.de/stoffe/stoffarten/jersey-stoffe/?f_muster_684=695&sort=bestseller'},
        {'name': 'Jersey (Design)', 'url': 'https://www.stoffe.de/stoffe/stoffarten/jersey-stoffe/?f_muster_684=685&sort=bestseller'},
        {'name': 'Baumwolle (Solid)', 'url': 'https://www.stoffe.de/stoffe/stoffarten/baumwollstoffe/?f_muster_684=695&sort=bestseller'}
    ]
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def get_takoy_data(url, cat_name):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.content, 'html.parser')
    products = []
    # Takoy product selector (môže sa meniť podľa štruktúry webu)
    items = soup.select('.product-item')[:20] 
    for item in items:
        try:
            name = item.select_one('.product-name').text.strip()
            price_text = item.select_one('.price-new').text.replace('€', '').replace(',', '.').strip()
            price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))
            # Doprava Takoy: 5.90, nad 100 zdarma
            shipping = 0 if price >= 100 else 5.90
            products.append({
                'source': 'Takoy.de',
                'category': cat_name,
                'name': name,
                'price_1m': round(price, 2),
                'total_with_shipping': round(price + shipping, 2)
            })
        except: continue
    return products

def get_stoffe_data(url, cat_name):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.content, 'html.parser')
    products = []
    # Stoffe.de product selector
    items = soup.select('.product-tile')[:20]
    for item in items:
        try:
            name = item.select_one('.product-tile__name').text.strip()
            price_text = item.select_one('.price__value').text.replace('€', '').replace(',', '.').strip()
            price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))
            # Doprava Stoffe: 5.95, nad 50 zdarma
            shipping = 0 if price >= 50 else 5.95
            products.append({
                'source': 'Stoffe.de',
                'category': cat_name,
                'name': name,
                'price_1m': round(price, 2),
                'total_with_shipping': round(price + shipping, 2)
            })
        except: continue
    return products

all_data = []
for cat in CATEGORIES['takoy']:
    all_data.extend(get_takoy_data(cat['url'], cat['name']))
for cat in CATEGORIES['stoffe']:
    all_data.extend(get_stoffe_data(cat['url'], cat['name']))

output = {
    'last_update': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
    'products': all_data
}

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)