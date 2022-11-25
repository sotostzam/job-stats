from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

class MongoDB:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client.linkedin
        self.jobs = self.db.jobs
        self.jobs.create_index([('id', 1)], unique=True)

    def insert_one(self, document):
        try:
            self.db.jobs.insert_one(document)
        except DuplicateKeyError:
            print(f'Found duplicates during insertion to db.')

    def insert_many(self, collection):
        try:
            self.db.jobs.insert_many(collection, ordered=False)
        except DuplicateKeyError as e:
            print(f'Duplicate error: {e}')
