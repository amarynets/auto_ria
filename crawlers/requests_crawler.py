import csv
from datetime import datetime

import requests

from parser import parse_list, parse_car, parse


def fetch_page(url, cookies=None):
    if not cookies:
        cookies = {}
    print(f'DOWNLOAD PAGE: {url}')
    response = requests.get(url, cookies)
    return response


def process(pages, size, brand='bmw'):
    start_time = datetime.now()
    fieldnames = ['itemLink', 'location', 'race', 'fuelName', 'gearboxName', 'title', 'usd', 'eur', 'uah', 'phone',
                  'description', 'color', 'markName', 'modelName', 'category']

    list_pages = [f'https://auto.ria.com/car/{brand}/?page={i}&countpage={size}' for i in range(1, pages + 1)]
    list_resp = [fetch_page(url, cookies={'ipp': str(size)}) for url in list_pages]

    items_on_pages = [
        {'item': item, 'url': item['itemLink']}
        for url, page in zip(list_pages, list_resp) for item in parse(url, page.content.decode(), parse_list)
    ]
    for item in items_on_pages:
        page = fetch_page(item['url'])
        detail_info = parse(item['url'], page.content.decode(), parse_car)
        item['item'].update(detail_info)

    with open('request.csv', 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        for item in items_on_pages:
            csv_writer.writerow(item['item'])

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print('Work is done. Elapsed time: ', elapsed_time)


def app(pages, size, brand='bmw'):
    process(pages=pages, size=size, brand=brand)


if __name__ == '__main__':
    pages = 1
    size = 10
    brand = 'bmw'
    app(pages, size, brand)
