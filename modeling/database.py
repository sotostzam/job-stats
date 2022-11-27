from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

class MongoDB:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.linkedin
        self.jobs = self.db.jobs
        self.jobs.create_index([('id', 1)], unique=True)

    def insert_document(self, document):
        try:
            self.db.jobs.insert_one(document)
        except DuplicateKeyError:
            print(f'Found duplicates during insertion to db.')

    def find(self, query):
        return self.jobs.find(query)

    def get_all_documents(self):
        return self.jobs.find({})
