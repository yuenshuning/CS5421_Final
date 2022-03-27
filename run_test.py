import unittest
import json
import os
from typing import List
from unittest import runner
from pymongo import MongoClient

class ImportJsonToMongo:

    def __init__(self, uri, database, file):
        self.client = MongoClient(uri)
        self.database = database
        self.file = file
        self.filename = os.path.basename(self.file).split('.')[0]

    def read_json(self):
        with open(self.file, "r", encoding="utf-8") as f:
            records = json.load(f)
        dicts = list(records)
        return dicts

    def import_file(self):
        dicts = self.read_json()
        mycol = self.client.get_database(self.database).get_collection(self.filename)
        mycol.drop()
        mycol.insert_many(dicts)


class TestJson(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("starting...")
        import_json = ImportJsonToMongo(URI, DATABASE, FILE)
        import_json.import_file()
        
    @classmethod
    def tearDownClass(cls):
        print("closing...")
    
    def test_add(self):
        self.assertEqual(3, 3)
    
    def test_sub(self):
        self.assertEqual([1], [1])


if __name__ == '__main__':
    FILE = 'test/library.json'
    URI = 'mongodb://localhost:27017/'
    DATABASE = 'cs5421'

    suite = unittest.TestSuite(unittest.makeSuite(TestJson))
    unittest.TextTestRunner(verbosity=2).run(suite)