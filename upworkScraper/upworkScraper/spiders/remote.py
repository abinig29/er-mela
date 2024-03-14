import scrapy
import dateparser
import json
from upworkScraper.items import UpworkscraperItem


class RemoteSpider(scrapy.Spider):
    name = "remote"
    allowed_domains = ["remote.co"]
    current_page = 1
    number_of_pages = 1
    urls = [
        "https://remote.co/remote-jobs/developer/page/",
        "https://remote.co/remote-jobs/design/page/",
        "https://remote.co/remote-jobs/it/"
    ]
    api_url = urls[0]

    def start_requests(self):
        for url in self.urls:
            self.api_url = url
            yield scrapy.Request(
                url=self.api_url + str(self.current_page) + "/",
                callback=self.parse_job,
            )
            self.current_page = 1
            self.number_of_pages = 1

    def parse_job(self, response):
        if self.number_of_pages == 1:
            self.number_of_pages += (
                len(response.css("nav div.pagination.number-pagination > a")) - 1
            )

        jobs = response.css("div.card-body.p-0 > a")
        for job in jobs:
                job_item=UpworkscraperItem()
                job_item['title'] = job.css(".font-weight-bold.larger::text").get().replace("\n", "").replace("&nbsp", ""),
                job_item['link'] ="https://remote.co/" + job.attrib["href"],
                job_item["posted_on"] = dateparser.parse(job.css("date::text").get().strip()).strftime(
                    "%Y-%m-%d"
                ),
                job_item["img"]  = job.css("div.row.no-gutters.align-items-center img").attrib["data-lazy-src"].strip()
                job_item['company_name'] = job.css(".m-0.text-secondary::text").get().strip().replace("\n", "").replace("  ", "").replace("|", ""),
                job_item['company_link'] = None
                job_item['company_location'] =  "Remote"
                job_item["description"]=None
                job_item["skills"]  = [c.get().replace("&nbsp", "") for c in job.css("span.badge.badge-success small::text")]   
                job_item["category"]  =None
                job_item["fixed"]  = None
                job_item["range"]  = None
                job_item["sourse"]  = 'R'   
                yield job_item
                
            
        
        if self.current_page < self.number_of_pages:
            self.current_page += 1
            yield scrapy.Request(
                url=self.api_url + str(self.current_page) + "/",
                callback=self.parse_job,
            )