import csv
from datetime import datetime

from selenium import webdriver
from parser import parse_list, parse_car, parse


def fetch_page(driver, url):
    print(f'DOWNLOAD PAGE: {url}')
    driver.get(url)
    return driver.page_source


def process(driver, pages, size, brand='bmw'):
    driver.add_cookie({'name': 'ipp', 'value': str(size), 'domain': 'auto.ria.com', 'path': '/'})
    start_time = datetime.now()
    fieldnames = ['itemLink', 'markName', 'modelName', 'title', 'year', 'uah', 'category',  'phone', 'color', 'description', 'race', 'location', 'fuelName', 'gearboxName']

    list_pages = [f'https://auto.ria.com/car/{brand}/?page={i}&countpage={size}' for i in range(1, pages + 1)]
    list_resp = [fetch_page(driver, url) for url in list_pages]

    items_on_pages = [
        {'item': item, 'url': item['itemLink']}
        for url, page in zip(list_pages, list_resp) for item in parse(url, page, parse_list)
    ]
    for item in items_on_pages:
        page = fetch_page(driver, item['url'])
        detail_info = parse(item['url'], page, parse_car)
        item['item'].update(detail_info)

    with open('selenium.csv', 'w') as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()
        for item in items_on_pages:
            csv_writer.writerow(item['item'])

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print('Ellapsed time:', int(elapsed_time.total_seconds() * 1000), 'ms')


def app(pages, size, brand='bmw'):
    driver = webdriver.Chrome()
    driver.get('https://github.com/')
    try:
        process(driver=driver, pages=pages, size=size, brand=brand)
    except Exception as e:
        driver.close()
        driver.quit()
        raise e
    finally:
        driver.quit()


if __name__ == '__main__':
    pages = 1
    size = 10
    brand = 'bmw'
    app(pages, size, brand)
