import asyncio
import csv
import time
import aiohttp

from bs_parser import parse_car, parse_list


async def fetch_page(url):
    cookies = {'ipp': 100}
    async with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.get(url) as resp:
            return await resp.text()


async def process(pages, size):
    start_time = time.time()
    fieldnames = ['itemLink', 'location', 'race', 'fuelName', 'gearboxName', 'title', 'usd', 'eur', 'uah', 'phone', 'description', 'color', 'markName', 'modelName', 'category']
    list_pages_to_fetch = [fetch_page(f'https://auto.ria.com/car/bmw/?page={i}&countpage={size}') for i in range(1, pages + 1)]
    list_pages = await asyncio.gather(*list_pages_to_fetch)

    items_on_pages = [{'item': item, 'url': item['itemLink']} for page in list_pages for item in parse_list(page)]
    items_on_pages = list(zip(*[items_on_pages[i::100] for i in range(100)]))
    for items in items_on_pages:
        list_car_pages_to_fetch = [fetch_page(i['url']) for i in items]
        cars_pages = await asyncio.gather(*list_car_pages_to_fetch)

        for item, car in zip(items, (parse_car(r) for r in cars_pages)):
            item['item'].update(car)

    with open('aiohttp.csv', 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        for items in items_on_pages:
            for item in items:
                csv_writer.writerow(item['item'])

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Work is done. Elapsed time: ',  elapsed_time)


asyncio.run(process(20, 100))

