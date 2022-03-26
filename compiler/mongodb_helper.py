from http import client
import pymongo


def db_connect(url='mongodb://localhost:27017/', database='test') -> pymongo.MongoClient:
    client = pymongo.MongoClient(url)
    db = client[database]
    return db
    
