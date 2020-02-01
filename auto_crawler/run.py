from scrapy.cmdline import execute

execute('scrapy crawl auto_ria -a car=bmw -a pages=20 -a size=100 -o cars.csv'.split())
