import asyncio
import csv
import time
import aiohttp

from parser import parse_car, parse_list


async def fetch_page(session, url):
    async with session.get(url) as resp:
        return await resp.text()


async def bound_fetch(sem, session, url):
    async with sem:
        return await fetch_page(session, url)


async def process(pages, size, brand='bmw'):
    start_time = time.time()
    sem = asyncio.Semaphore(1000)
    fieldnames = ['itemLink', 'location', 'race', 'fuelName', 'gearboxName', 'title', 'usd', 'eur', 'uah', 'phone', 'description', 'color', 'markName', 'modelName', 'category']
    async with aiohttp.ClientSession(cookies={'ipp': str(size)}, connector=aiohttp.TCPConnector(ssl=False)) as session:
        list_pages_to_fetch = [bound_fetch(sem, session, f'https://auto.ria.com/car/{brand}/?page={i}&countpage={size}') for i in range(1, pages + 1)]
        list_pages = await asyncio.gather(*list_pages_to_fetch)
    print('Download list pages: ', time.time() - start_time)
    items_on_pages = [{'item': item, 'url': item['itemLink']} for page in list_pages for item in parse_list(page)]

    dt = time.time()
    async with aiohttp.ClientSession() as session:
        list_car_pages_to_fetch = [bound_fetch(sem, session, i['url']) for i in items_on_pages]
        cars_pages = await asyncio.gather(*list_car_pages_to_fetch)
    print('Download items: ', time.time() - dt)
    cars_pages = [parse_car(r) for r in cars_pages]
    for item, car in zip(items_on_pages, cars_pages):
        item['item'].update(car)

    end_time = time.time()
    elapsed_time = end_time - start_time
    with open('aiohttp.csv', 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        for item in items_on_pages:
            csv_writer.writerow(item['item'])
    print('Work is done. Elapsed time: ',  elapsed_time)


def app(pages, size, brand='bmw'):

    asyncio.run(process(pages=pages, size=size, brand=brand))


if __name__ == '__main__':
    app(10, 10, 'bmw')

