import os

import certifi
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

load_dotenv()

client = AsyncMongoClient(os.environ["MONGODB_URL"], tlsCAFile=certifi.where())


def get_db() -> AsyncDatabase:
    return client.get_database("prod")
