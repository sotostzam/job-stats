from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from scrapers.common import pprint

class MongoDB:
    def __init__(self):
        self.name = self.__class__.__name__
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.scraper
        self.jobs = self.db.jobs

    def insert_documents(self, documents):
        inserted = 0
        for document in documents:
            try:
                self.db.jobs.insert_one(document)
                inserted += 1
            except DuplicateKeyError:
                pass
        pprint(msg=f'Inserted {inserted} new documents', type=1, prefix=self.name)

    def find(self, query):
        return self.jobs.find({}, query)

    def get_all_documents(self):
        return self.jobs.find({})
