from bs4 import BeautifulSoup as Bs
from parsel import Selector


def parse(url, page, func):
    print(f'PARSE PAGE: {url}')
    return func(page)


def parse_list(response):
    response = Selector(text=response)
    all_cars = response.css('section.ticket-item.new__ticket.t')
    for car in all_cars:
        item = {
            'itemLink': car.css('div.content-bar a.m-link-ticket::attr(href)').extract_first(),
            'location': car.css('ul li.view-location::text').extract_first(default='').strip(),
            'race': car.xpath('.//ul/li/i[@class="icon-mileage"]/../text()').extract_first(default='').strip(),
            'fuelName': car.xpath('.//ul/li/i[@class="icon-fuel"]/../text()').extract_first(default='').strip(),
            'gearboxName': car.xpath('.//ul/li/i[@class="icon-transmission"]/../text()').extract_first(
                default='').strip(),
        }
        yield item


def parse_car(response):
    response = Selector(text=response)
    item = {}
    year = response.css('h1.head::attr(title)').get().split(' ')[-1]
    if not year:
        title = response.css('h1.auto-head_title::text').get().split(' ')[-1]
    title = response.css('h1.head::attr(title)').extract_first()
    if not title:
        title = response.css('h1.auto-head_title::text').extract_first()
    item['title'] = title
    item['year'] = year
    # item['usd'] = response.css('div.price_value strong::text').extract_first()
    # item['eur'] = response.css('span[data-currency="EUR"]::text').extract_first()
    item['uah'] = response.css('span[data-currency="UAH"]::text').extract_first()
    item['phone'] = response.css('div.phones_item span::attr(data-phone-number)').extract_first(default='')
    item['description'] = response.css('div#full-description::text').extract_first()
    item['color'] = response.xpath('.//span[@class="car-color"]/../text()').extract_first()

    breadcrumbs = response.xpath('.//div[@itemtype="http://data-vocabulary.org/Breadcrumb"]/..')
    item['markName'] = breadcrumbs.xpath('.//a/@title').extract()[-1]
    item['modelName'] = breadcrumbs.xpath('span/text()').extract_first()

    item['category'] = response.css('div#description_v3 dl dd::text').extract_first(default='').strip()
    return item


def parse_list_bs(response):
    soup = Bs(response)
    all_cars = soup.select('section.ticket-item.new__ticket.t')
    for car in all_cars:
        item = {
            'itemLink': car.select_one('div.content-bar a.m-link-ticket').attrs['href'],
            'location': car.select_one('ul li.view-location').text.strip(),
            'race': car.select_one('ul li i.icon-mileage').parent.text.strip(),
            'fuelName': car.select_one('ul li i.icon-fuel').parent.text.strip(),
            'gearboxName': car.select_one('ul li i.icon-transmission').parent.text.strip(),
        }
        yield item


def parse_car_bs(response):
    soup = Bs(response)
    item = {
        'title': '',
        'usd': soup.select_one('div.price_value strong'),
        'eur': soup.select_one('span[data-currency="EUR"]'),
        'uah': soup.select_one('span[data-currency="UAH"]'),
        'phone': '',
        'description': soup.select_one('div#full-description'),
        'color': '',
        'markName': soup.select_one('h1.head span[itemprop="brand"]'),
        'modelName': soup.select_one('h1.head span[itemprop="name"]'),
        'category': soup.select_one('div#description_v3 dl dd'),
    }

    for k, v in item.items():
        try:
            item[k] = v.text if not isinstance(v, str) else v
        except Exception as e:
            item[k] = ''
    color = soup.select_one('span.car-color')
    title = soup.select_one('h1.head')
    phone = soup.select_one('div.phones_item span')

    item['color'] = color.parent.text if color else ''
    item['title'] = title.attrs.get('title') if title else ''
    item['phone'] = phone.attrs.get('data-phone-number') if phone else ''

    return item
