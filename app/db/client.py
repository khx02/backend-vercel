import os

import certifi
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

load_dotenv()

MONGODB_URL = os.environ["MONGODB_URL"]
DB_NAME = os.getenv("MONGODB_DB", "prod")
SERVER_SELECTION_TIMEOUT_MS = int(
    os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "50000")
)
CONNECT_TIMEOUT_MS = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "50000"))
SOCKET_TIMEOUT_MS = int(os.getenv("MONGODB_SOCKET_TIMEOUT_MS", "10000"))

client = AsyncMongoClient(
    MONGODB_URL,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
    connectTimeoutMS=CONNECT_TIMEOUT_MS,
    socketTimeoutMS=SOCKET_TIMEOUT_MS,
)


def get_db() -> AsyncDatabase:
    return client.get_database(DB_NAME)


async def ping() -> dict:
    return await client.admin.command("ping")
