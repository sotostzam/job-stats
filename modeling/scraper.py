from scrapers import LinkedInScraper
from database import MongoDB
import json

if __name__ == "__main__":
    with open("../credentials.json",'r') as secrets:
        creds = json.load(secrets)

    role = "Data Scientist"
    location = "Athens, Attiki, Greece"

    database = MongoDB()

    scrapers = [
        LinkedInScraper(creds['username'], creds['password'])
    ]

    for scraper in scrapers:
        scraped_jobs = scraper.get_jobs(role, location)
        if scraped_jobs:
            database.insert_documents(scraped_jobs)
