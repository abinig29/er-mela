
from itemadapter import ItemAdapter
import sqlite3
import re
import requests
class CleanDescriptionPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        description =adapter.get('description')
        sourse=adapter.get('sourse')
        if sourse !='L':
         if description:
             match = re.search(r'(.*?)Posted On', description, re.DOTALL)
             if match:
                 description=match.group(1).strip()
                 description = re.sub(r'<.*?>', '', description)
                 description = description.replace('<br />', '\n')
                 description = description.replace('\n', ' ')
                 adapter['description'] =  description.strip()
        return item

class SqlitePipeline:
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        bot_token = settings.get('TELEGRAM_BOT_TOKEN')
        chat_id = settings.get('TELEGRAM_CHAT_ID')
        return cls(bot_token, chat_id)
    def __init__(self,bot_token,chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.con = sqlite3.connect('jobs.db')
        self.cur = self.con.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT,
            description TEXT,
            postedOn TEXT,
            category TEXT,
            skills TEXT,
            fixed TEXT,
            range TEXT,
            job_listed TEXT,
            company_name TEXT,
            company_link TEXT,
            company_location TEXT,
            sourse TEXT,
            img TEXT
            
        )
        """)

    
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        title = adapter.get("title")
        link = adapter.get("link")
        description = adapter.get("description")
        posted_on = adapter.get("posted_on")
        category = adapter.get("category")
        skills = adapter.get("skills")
        price_range = adapter.get("range")
        fixed_price = adapter.get("fixed")
        company_name=adapter.get("company_name")
        company_link=adapter.get("company_link")
        company_location=adapter.get("company_location")
        img=adapter.get("img")
        
        sourse=adapter.get("sourse")

        if None in (title, link, description, posted_on, category):
         spider.logger.warning("One or more required fields are None: %s", item)
        self.cur.execute("select * from jobs where title = ?", (adapter.get("title"),))
        result = self.cur.fetchone()
        if result:
            spider.logger.warn("Item already in database: ")
     
        else:
            self.cur.execute("""
                INSERT INTO jobs (title, link, description, postedOn, category,skills,fixed,range,company_name,company_link,company_location,sourse,img) VALUES (?, ?, ?, ?, ?,?,?,?,?,?,?,?,?)
            """,
            (
                title,
                link,
                description,
                str(posted_on),
                str(category),
                str(skills), 
                fixed_price,
                price_range,
                company_name,
                company_link,
                company_location,
                sourse,
                img
                 
            ))
            self.con.commit()
            if sourse=='U':
             self.send_telegram_upwork_notification(title,link,skills,posted_on,price_range,fixed_price,spider)
            else:
             self.send_telegram_linkedin_notification( title, link,company_name,company_link,company_location,img,posted_on,spider)
                
        return item
    def send_telegram_upwork_notification(self, title, link,skills,posted_on,range,fixed,spider):
        message = f"<b>New Upwork Job:</b>\n"
        message += f"<b>Title:</b> {title}\n"
        message += f"<b>Link:</b> <a href='{link}'>Job Link</a>\nSkills:\t"
        for skill in skills:
         message += f'#{skill.replace(" ", "_")}\t\t\t'
        message += f"\nPosted on: {posted_on[0]}"
        if range:
         message += f"\nHourly Range: {range}"
        if fixed:
         message += f"\nFixed Price: {fixed}"
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"  
            
        }
        response = requests.post(url, data=data)
        
        if response.status_code != 200:
            spider.logger.error(f"Failed to send Telegram notification: {response.text}")
    def send_telegram_linkedin_notification(self, title, link,company_name,company_link,company_location,img,posted_on,spider):
        message = f"<b>New LinkedIn Job:</b>\n"
        message += f"<b>Title:</b> {title}\n"
        message += f"<b>Link:</b> <a href='{link}'>Job Link</a>\n"
        message += f"<b>Posted on:</b> {posted_on}\n"
        if company_name:
            message += f"<b>Company Name:</b> {company_name}\n"
        if company_link:
            message += f"<b>Company Link:</b> <a href='{company_link}'>Company Link</a>\n"
        if company_location:
            message += f"<b>Company Location:</b> {company_location}\n"
        if img:
         message += f"<img src='{img}' width='100' height='100'>\n"

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"  
        }
        if img:
         data["photo"] = img
         
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
       
        response = requests.post(url, data=data)
        if response.status_code != 200:
            spider.logger.error(f"Failed to send Telegram notification: {response.text}")
            
            
    def close_spider(self, spider):
        self.con.close()