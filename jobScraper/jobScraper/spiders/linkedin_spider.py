from datetime import datetime, timedelta
import scrapy
from jobScraper.items import JobScraperItem
from fake_useragent import UserAgent


class LinkedinSpider(scrapy.Spider):
    name = "linkedinSpider"
    
    allowed_domains = ["www.linkedin.com"]
    ua = UserAgent()
    user_agent = ua.random
    headers = {"User-Agent": user_agent}
    api_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=software%2Bengineering%2C%2BWeb%2Bdevelopment%2C%2Bfrontend%2C%2Bbackend&location=remote&geoId=&start="

    def start_requests(self):
        first_job_on_page = 0
        first_url = self.api_url + str(first_job_on_page)
        ua = UserAgent()
        user_agent = ua.random
        headers = {"User-Agent": user_agent}
        yield scrapy.Request(
            url=first_url,
            headers=headers,
            callback=self.parse_job,
            meta={"first_job_on_page": first_job_on_page},
        )

    def parse_job(self, response):
        first_job_on_page = response.meta["first_job_on_page"]
        jobs = response.css("li")
        num_jobs_returned = len(jobs)
        today_date = datetime.now().date()
        start_of_week = today_date - timedelta(days=today_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        for job in jobs:
            posted_on_date = datetime.strptime(
                job.xpath("//time/@datetime").extract_first(), "%Y-%m-%d"
            ).date()
            if start_of_week <= posted_on_date <= end_of_week:
                job_item = JobScraperItem()
                job_item["title"] = job.css("h3::text").get(default="not-found").strip()
                job_item["link"] = (
                    job.css(".base-card__full-link::attr(href)")
                    .get(default="not-found")
                    .strip()
                )
                job_item["posted_on"] = posted_on_date
                job_item["img"] = job.xpath("//img/@data-delayed-url").extract_first()
                job_item["company_name"] = (
                    job.css("h4 a::text").get(default="not-found").strip()
                )
                job_item["company_link"] = job.css("h4 a::attr(href)").get(
                    default="not-found"
                )
                job_item["company_location"] = (
                    job.css(".job-search-card__location::text")
                    .get(default="not-found")
                    .strip()
                )
                job_item["description"] = None
                job_item["skills"] = None
                job_item["category"] = None
                job_item["fixed"] = None
                job_item["range"] = None
                job_item["sourse"] = "L"
                yield job_item
            else:
                continue
        if num_jobs_returned >= 50:
            print("50============== done")
        elif num_jobs_returned > 0:
            first_job_on_page = int(first_job_on_page) + 25
            next_url = self.api_url + str(first_job_on_page)
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_job,
                meta={"first_job_on_page": first_job_on_page},
            )
