from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

DATABASE_URL = os.getenv('DATABASE_URL')

uri = os.getenv('DATABASE_URL')

client = MongoClient(uri, server_api=ServerApi('1'))

db = client['Turismap']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)