import scrapy
class UpworkscraperItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    description = scrapy.Field()
    posted_on=scrapy.Field()
    category=scrapy.Field()
    skills=scrapy.Field()
    fixed=scrapy.Field()
    range=scrapy.Field()
