from bs4 import BeautifulSoup as Bs


def parse_list(response):
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


def parse_car(response):
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
