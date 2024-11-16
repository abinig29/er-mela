import psycopg2
from itemadapter import ItemAdapter
import re
import requests


class CleanDescriptionPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        description = adapter.get("description")
        sourse = adapter.get("sourse")
        if sourse != "L":
            if description:
                match = re.search(r"(.*?)Posted On", description, re.DOTALL)
                if match:
                    description = match.group(1).strip()
                    description = re.sub(r"<.*?>", "", description)
                    description = description.replace("<br />", "\n")
                    description = description.replace("\n", " ")
                    adapter["description"] = description.strip()
        return item


class PostgresPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        bot_token = settings.get("TELEGRAM_BOT_TOKEN")
        chat_id = settings.get("TELEGRAM_CHAT_ID")
        return cls(bot_token, chat_id)

    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        user = "postgres.iptfrrlntgemcmsqvhwf"
        password = "tataTATA123123HER"
        host = "aws-0-us-west-1.pooler.supabase.com"
        dbname = "postgres"

        self.connection = psycopg2.connect(
            host=host, user=user, password=password, dbname=dbname
        )
        self.cur = self.connection.cursor()

        self.cur.execute(
            """
       CREATE TABLE IF NOT EXISTS "Job" (
        id SERIAL PRIMARY KEY,
        title TEXT,
        link VARCHAR(255),
        description TEXT,
        postedOn TIMESTAMP,
        category VARCHAR(255),
        skills TEXT[], 
        fixed VARCHAR(255),
        range VARCHAR(255),
        companyName VARCHAR(255),
        companyLink VARCHAR(255),
        companyLocation VARCHAR(255),
        source VARCHAR(255),
        img  VARCHAR(255),
        createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) 
        """
        )
        self.connection.commit()

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
        company_link = adapter.get("company_link")
        company_name = adapter.get("company_name")
        company_location = adapter.get("company_location")
        img = adapter.get("img")
        sourse = adapter.get("sourse")

        if None in (title, link, description, posted_on, category):
            spider.logger.warning("One or more required fields are None: %s", item)
        result = None
        try:
            self.cur.execute('SELECT * FROM public."Job" WHERE title = %s', (title,))
            result = self.cur.fetchone()
        except Exception as e:
            print("Error occurred:", e)
        if result:
            spider.logger.warn("Item already in database: ")

        else:
            try:
                self.cur.execute(
                    """
                    INSERT INTO "Job" (title, link, description, "postedOn", category, skills, fixed, range, "companyName", "companyLink", "companyLocation", source, img) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        title,
                        link,
                        description,
                        posted_on,
                        category,
                        skills,  
                        fixed_price,
                        price_range,
                        company_name,
                        company_link,
                        company_location,
                        sourse,
                        img,
                    ),
                )
                self.connection.commit()
            except Exception as e:
                self.connection.rollback()

            # if sourse == "U":
            #     self.send_telegram_upwork_notification(
            #         title, link, skills, posted_on, price_range, fixed_price, spider
            #     )
            # else:
            #     self.send_telegram_linkedin_notification(
            #         title,
            #         link,
            #         company_name,
            #         company_link,
            #         company_location,
            #         img,
            #         posted_on,
            #         spider,
            #     )

        return item

    def send_telegram_upwork_notification(
        self, title, link, skills, posted_on, range, fixed, spider
    ):
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
        data = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, data=data)

        if response.status_code != 200:
            spider.logger.error(
                f"Failed to send Telegram notification: {response.text}"
            )

    def send_telegram_linkedin_notification(
        self,
        title,
        link,
        company_name,
        company_link,
        company_location,
        img,
        posted_on,
        spider,
    ):
        message = f"<b>New LinkedIn Job:</b>\n"
        message += f"<b>Title:</b> {title}\n"
        message += f"<b>Link:</b> <a href='{link}'>Job Link</a>\n"
        message += f"<b>Posted on:</b> {posted_on}\n"
        if company_name:
            message += f"<b>Company Name:</b> {company_name}\n"
        if company_link:
            message += (
                f"<b>Company Link:</b> <a href='{company_link}'>Company Link</a>\n"
            )
        if company_location:
            message += f"<b>Company Location:</b> {company_location}\n"
        if img:
            message += f"<img src='{img}' width='100' height='100'>\n"

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        data = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
        if img:
            data["photo"] = img

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        response = requests.post(url, data=data)
        if response.status_code != 200:
            spider.logger.error(
                f"Failed to send Telegram notification: {response.text}"
            )

    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()
