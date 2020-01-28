import csv
import time
import requests

from bs_parser import parse_list, parse_car


def process(pages, size):
    start_time = time.time()
    fieldnames = ['itemLink', 'location', 'race', 'fuelName', 'gearboxName', 'title', 'usd', 'eur', 'uah', 'phone',
                  'description', 'color', 'markName', 'modelName', 'category']
    list_pages = [
        requests.get(f'https://auto.ria.com/car/bmw/?page={i}&countpage={size}', cookies={'ipp': str(size)})
        for i in range(1, pages + 1)
    ]

    items_on_pages = [{'item': item, 'url': item['itemLink']} for page in list_pages for item in parse_list(page.content)]
    cars_pages = [requests.get(i['url']) for i in items_on_pages]

    for item, car in zip(items_on_pages, (parse_car(r.content) for r in cars_pages)):
        item['item'].update(car)

    with open('request.csv', 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        for item in items_on_pages:
            csv_writer.writerow(item['item'])

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Work is done. Elapsed time: ', elapsed_time)

process(10, 10)