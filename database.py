import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("mongodb://localhost:27017")
DB_NAME = os.getenv("mydb")

client = MongoClient('mongodb://localhost:27017')
db = client['mydb']
collection = db['pdfdata']
