import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_mongo_uri() -> str:
    return os.getenv("MONGODB_URI", "mongodb://localhost:27017")


def get_database_name() -> str:
    return os.getenv("MONGODB_DB", "sentinelguard")


def init_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is not None:
        return _db
    _client = AsyncIOMotorClient(get_mongo_uri())
    _db = _client[get_database_name()]
    return _db


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        return init_db()
    return _db
