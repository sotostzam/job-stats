from scrapers import LinkedInScraper
from database import MongoDB
import json

if __name__ == "__main__":
    # Search keywords used for scraping job posts
    role = ["Data Scientist", "Machine Learning", "Data Analyst", "ML Ops"]
    location = "Greece"

    # Regex expressions to match desired job titles
    regex_matches = {
        'Data Scientist': [r'.*[Dd]ata.?[Ss]cien.*'],
        'Data Analyst':   [r'.*[Dd]ata.?[Aa]nalyst.*'],
        'ML Engineer':    [r'.*[Mm]achine.?[Ll]earning.*',
                           r'.*[Mm][Ll].?[Ee]ngineer.*',
                           r'.*[Dd]eep.?[Ll]earning.*',
                           r'.*[Aa]rtificial.?[Ii]ntelligence.*',
                           r'(?:^|(?<=[\s]))\(?[Aa][Ii]\)?(?=[\s]|$)'],
        'MLOps':          [r'.*[Mm][Ll].?[Oo]ps']
    }

    # Read the secret credentials for login
    with open("../credentials.json",'r') as secrets:
        creds = json.load(secrets)

    # Initialize the MongoDB database
    database = MongoDB()

    # List of created scrapers
    scrapers = [
        LinkedInScraper(creds['username'], creds['password'])
    ]

    # Perform scraping from all available websites
    for scraper in scrapers:
        scraped_jobs = scraper.get_jobs(role, location, regex_matches)
        if scraped_jobs:
            database.insert_documents(scraped_jobs)
