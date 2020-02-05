from scrapy.cmdline import execute

execute('scrapy crawl auto_ria -a car=bmw -a pages=2 -a size=10 -o cars.csv'.split())
