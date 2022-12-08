from scrapers import LinkedInScraper, KarieraScraper, IndeedScraper
from database import MongoDB
import json

if __name__ == "__main__":
    # Search keywords used for scraping job posts
    role = ["Data Scientist", "Machine Learning", "Data Analyst", "ML Ops", "Data Engineer"]
    location = "Greece"

    # Read the secret credentials for login
    with open("../credentials.json",'r') as secrets:
        creds = json.load(secrets)

    # Initialize the MongoDB database
    database = MongoDB()

    # List of created scrapers
    scrapers = [
        LinkedInScraper(creds['username'], creds['password']),
        KarieraScraper(),
        IndeedScraper()
    ]

    # Perform scraping from all available websites
    for scraper in scrapers:
        scraped_jobs = scraper.get_jobs(role, location)
        if scraped_jobs:
            database.insert_documents(scraped_jobs)
