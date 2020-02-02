import asyncio
import csv
import time
import aiohttp

from own_crawlers.bs_parser import parse_car, parse_list


async def fetch_page(session, url):
    async with session.get(url) as resp:
        return await resp.text()


async def bound_fetch(sem, session, url):
    async with sem:
        return await fetch_page(session, url)


class Crawler:

    def __init__(self, car='bmw', pages=10, size=10):
        self.car = car
        self.pages = pages
        self.size = size
        self.queue = asyncio.Queue()
        self.stat = {
            'start_time': 0,
            'download_time': 0,
            'elapsed_time': 0,
            'parse_time': 0,
            'end_time': 0,
        }
        self.sem = asyncio.Semaphore(1000)
        self.result = []
        self._item_to_scrap = 0

    async def crawl(self):
        self.stat['start_time'] = time.time()
        for i in range(1, self.pages + 1):
            await self.queue.put(f'https://auto.ria.com/car/{self.car}/?page={i}&countpage={self.size}')
            self._item_to_scrap += 1
        async with aiohttp.ClientSession(cookies={'ipp': str(self.size)}, connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            all_coro = asyncio.gather(*[self._worker(session) for _ in range(10)])
            await all_coro
        self.stat['end_time'] = time.time()
        self.stat['elapsed_time'] = self.stat['end_time'] - self.stat['start_time']

    def save(self):
        fieldnames = ['itemLink', 'location', 'race', 'fuelName', 'gearboxName', 'title', 'usd', 'eur', 'uah', 'phone',
                      'description', 'color', 'markName', 'modelName', 'category']
        with open('aiohttp.csv', 'w') as f:
            csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
            csv_writer.writeheader()
            for item in self.result:
                csv_writer.writerow(item)

    async def _worker(self, session):
        while True:
            item = await self.queue.get()
            self._item_to_scrap -= 1
            if isinstance(item, str):
                page = await bound_fetch(self.sem, session, item)
                items = parse_list(page)
                for item in items:
                    await self.queue.put(item)
                    self._item_to_scrap += 1
            elif isinstance(item, dict):
                page = await bound_fetch(self.sem, session, item['itemLink'])
                item.update(parse_car(page))
                self.result.append(item)
            if not self._item_to_scrap:
                return


c = Crawler(pages=20, size=100)
asyncio.run(c.crawl())
c.save()

print(c.stat)


