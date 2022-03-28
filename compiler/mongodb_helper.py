import pymongo


def db_connect(url='mongodb://localhost:27017/', database='cs5421') -> pymongo.MongoClient:
    client = pymongo.MongoClient(url)
    db = client[database]
    return db
    
