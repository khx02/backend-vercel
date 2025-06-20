from fastapi.security import OAuth2PasswordBearer
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
import certifi

from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncMongoClient(os.environ["MONGODB_URL"], tlsCAFile=certifi.where())


def get_db() -> AsyncDatabase:
    return client.get_database("prod")
