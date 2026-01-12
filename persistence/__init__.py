import logging

logging.info("eteydeb::persistence module is loaded.")

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "teydeb"
COLLECTION_NAME = "projects"

from pymongo import MongoClient

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

db = client[DB_NAME]
project_collection = db[COLLECTION_NAME]
