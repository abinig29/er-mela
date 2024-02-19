from datetime import datetime
import re
import scrapy
from upworkScraper.items import UpworkscraperItem


class JobspiderSpider(scrapy.Spider):
    name = "jobspider"
    allowed_domains = ["www.upwork.com"]
    start_urls = ["https://www.upwork.com/ab/feed/jobs/rss?paging=0%3B10&q=%28Python+OR+Vue.js+OR+React+OR+Native+OR+Django+OR+Next.js+OR+Svelte+OR+React%29&sort=recency&api_params=1&securityToken=c5466a33f0980fa4088031b92938f873985c27e062ab271ef6916b1274ed84bbee5ae845326f092c57e4681c4d36c0fa6ca4ad890f0f4c13795908ce2b03ad48&userUid=1385588801216208896&orgUid=1385588801220403200"]

    def parse(self, response):
        today = datetime.now().strftime("%B %d, %Y")
        for item in response.xpath('//item'):
            title = item.xpath('title/text()').get()
            link = item.xpath('link/text()').get()
            description = item.xpath('description/text()').get()
            posted_on_str =self.extract_posted_on(description)
            posted_on_date = datetime.strptime(posted_on_str, "%B %d, %Y %H:%M")
            posted_date_to_comaper= posted_on_date.strftime("%B %d, %Y")
            if posted_date_to_comaper == today:
                job_item=UpworkscraperItem()
                job_item["title"]=title.strip() if title else None
                job_item["link"]=link.strip() if link else None
                job_item["description"]=description.strip() if description else None
                job_item["skills"]  = self.extract_skills(description)    
                job_item["posted_on"] = posted_date_to_comaper,
                job_item["category"]  = self.extract_category(description)
                job_item["fixed"]  = self.extract_budget(description)
                job_item["range"]  = self.extract_hourly_range(description)
                yield job_item
    def extract_hourly_range(self, description):
        if description:
            match = re.search(r'Hourly Range</b>:\s*(.*?)\n*<br />', description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def extract_budget(self, description):
        if description:
            match = re.search(r'Budget</b>:\s*(.*?)\s*<br />', description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    def extract_posted_on(self, description):
        if description:
            match = re.search(r'Posted On</b>: (.*?) UTC', description)
            if match:
                return match.group(1)
        return None
    def extract_skills(self,description):
        if description:
            skills_match = re.findall(r'Skills</b>:\s*([\w\s,.]+)', description)
            skills = [skill.strip() for skill in skills_match[0].split(',')]
            return skills
        return None 
    def extract_category(self, description):
        if description:
            matches = re.findall(r'Category</b>: (.*?)<br />', description)
            if matches:
                return [match.strip() for match in matches]
        return None
    def extract_country(self, description):
        if description:
            match = re.search(r'Country</b>: (.*?)<br />', description)
            if match:
                return match.group(1).strip()
        return None