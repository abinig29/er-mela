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
    company_name=scrapy.Field()
    company_link=scrapy.Field()
    company_location=scrapy.Field()
    sourse=scrapy.Field()
    img=scrapy.Field()


