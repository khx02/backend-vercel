from typing import Any, Dict
from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.common import stringify_object_ids
from app.core.constants import EVENTS_COLLECTION


async def db_get_event_or_none(
    event_id: str, db: AsyncDatabase
) -> Dict[str, Any] | None:
    result = await db[EVENTS_COLLECTION].find_one({"_id": ObjectId(event_id)})
    return stringify_object_ids(result)
