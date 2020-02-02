import time
import csv
from selenium import webdriver
from own_crawlers.bs_parser import parse_list, parse_car


driver = webdriver.Chrome()
driver.get('https://github.com/')


def fetch_page(driver, url):
    driver.get(url)
    return driver.page_source


def process(pages, size, car='bmw'):
    driver.add_cookie({'name': 'ipp', 'value': str(size), 'domain': 'auto.ria.com', 'path': '/'})
    start_time = time.time()
    fieldnames = ['itemLink', 'location', 'race', 'fuelName', 'gearboxName', 'title', 'usd', 'eur', 'uah', 'phone',
                  'description', 'color', 'markName', 'modelName', 'category']
    list_pages = [
        fetch_page(driver, f'https://auto.ria.com/car/{car}/?page={i}&countpage={size}')
        for i in range(1, pages + 1)
    ]

    items_on_pages = [{'item': item, 'url': item['itemLink']} for page in list_pages for item in parse_list(page)]
    cars_pages = [fetch_page(driver, i['url']) for i in items_on_pages]

    for item, car in zip(items_on_pages, (parse_car(r) for r in cars_pages)):
        item['item'].update(car)

    with open('selenium.csv', 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        for item in items_on_pages:
            csv_writer.writerow(item['item'])

    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Work is done. Elapsed time: ', elapsed_time)

try:
    process(10, 10)
except Exception as e:
    driver.close()
    driver.quit()
    raise e
finally:
    driver.quit()

