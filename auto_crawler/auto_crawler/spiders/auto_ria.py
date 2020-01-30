# -*- coding: utf-8 -*-
import scrapy


class AutoRiaSpider(scrapy.Spider):
    name = 'auto_ria'
    allowed_domains = ['auto.ria.com']
    start_urls = ['https://auto.ria.com/car/bmw/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start_requests(self):
        pages = self.pages or 1
        size = self.size or 10
        car = self.car or 'bmw'
        for i in range(1, int(pages) + 1):
            yield scrapy.Request(
                url=f'https://auto.ria.com/car/{car}/?page={i}&countpage={size}',
                callback=self.parse,
                cookies={'ipp': size}
            )

    def parse(self, response):
        all_cars = response.css('section.ticket-item.new__ticket.t')
        for car in all_cars:
            item = {
                'itemLink': car.css('div.content-bar a.m-link-ticket::attr(href)').extract_first(),
                'location': car.css('ul li.view-location::text').extract_first(default='').strip(),
                'race': car.xpath('.//ul/li/i[@class="icon-mileage"]/../text()').extract_first(default='').strip(),
                'fuelName': car.xpath('.//ul/li/i[@class="icon-fuel"]/../text()').extract_first(default='').strip(),
                'gearboxName': car.xpath('.//ul/li/i[@class="icon-transmission"]/../text()').extract_first(default='').strip(),
            }
            yield scrapy.Request(
                url=item['itemLink'],
                callback=self.parse_car,
                meta={'item': item}
            )

    def parse_car(self, response):
        item = response.meta['item']
        item['title'] = response.css('h1.head::attr(title)').extract_first()
        item['usd'] = response.css('div.price_value strong::text').extract_first()
        item['eur'] = response.css('span[data-currency="EUR"]::text').extract_first()
        item['uah'] = response.css('span[data-currency="UAH"]::text').extract_first()
        item['phone'] = response.css('div.phones_item span::attr(data-phone-number)').extract_first(default='')
        item['description'] = response.css('div#full-description::text').extract_first()
        item['color'] = response.xpath('.//span[@class="car-color"]/../text()').extract_first()
        item['markName'] = response.css('h1.head span[itemprop="brand"]::text').extract_first()
        item['modelName'] = response.css('h1.head span[itemprop="name"]::text').extract_first()
        item['category'] = response.css('div#description_v3 dl dd::text').extract_first(default='').strip()
        yield item
