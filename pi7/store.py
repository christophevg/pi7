import os

from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
  MONGO_URI = "mongodb://localhost:27017/pi7"

mongo    = MongoClient(MONGO_URI)
database = MONGO_URI.split("/")[-1]
db       = mongo[database]
