from datetime import datetime
import scrapy
from upworkScraper.items import UpworkscraperItem


class JobspiderSpider(scrapy.Spider):
    name = "linkedinSpider"
    # allowed_domains = ["www.linkedin.com"]
    # start_urls = [
    #     "https://www.linkedin.com/jobs/search/?alertAction=viewjobs&currentJobId=3834542680&f_TPR=r86400&geoId=102748797&keywords=react%20js&location=&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&start=",
    #     ]
    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield scrapy.Request(url=url + '0', callback=self.parse_job)
            
    api_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=python&location=United%2BStates&geoId=103644278&trk=public_jobs_jobs-search-bar_search-submit&start=' 

    def start_requests(self):
        first_job_on_page = 0
        first_url = self.api_url + str(first_job_on_page)
        yield scrapy.Request(url=first_url, callback=self.parse_job, meta={'first_job_on_page': first_job_on_page})

    def parse_job(self, response):
        print("klllllllllllllll git herepppppppppppppppppppppppppppppppppppppppppp")   
        first_job_on_page = response.meta['first_job_on_page']
        jobs = response.css("li")
        num_jobs_returned = len(jobs)
        
        print("******* Num Jobs Returned *******")
        print(num_jobs_returned)
        print('*****')
        
        for job in jobs:
            job_item=UpworkscraperItem()
            job_item['title'] = job.css("h3::text").get(default='not-found').strip()
            job_item['link'] = job.css(".base-card__full-link::attr(href)").get(default='not-found').strip()
            job_item['job_listed'] = job.css('time::text').get(default='not-found').strip()

            job_item['company_name'] = job.css('h4 a::text').get(default='not-found').strip()
            job_item['company_link'] = job.css('h4 a::attr(href)').get(default='not-found')
            job_item['company_location'] = job.css('.job-search-card__location::text').get(default='not-found').strip()
            job_item["description"]=None
            job_item["skills"]  = None   
            job_item["posted_on"] = None
            job_item["category"]  =None
            job_item["fixed"]  = None
            job_item["range"]  = None
            job_item["sourse"]  = 'L'
            
            
            yield job_item

        if num_jobs_returned > 0:
            first_job_on_page = int(first_job_on_page) + 25
            next_url = self.api_url + str(first_job_on_page)
            yield scrapy.Request(url=next_url, callback=self.parse_job, meta={'first_job_on_page': first_job_on_page})
