from typing import Any, Dict
from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.common import stringify_object_ids
from app.core.constants import EVENTS_COLLECTION, RSVPS_COLLECTION
from app.schemas.event import RSVPStatus


async def db_get_event_or_none(
    event_id: str, db: AsyncDatabase
) -> Dict[str, Any] | None:
    result = await db[EVENTS_COLLECTION].find_one({"_id": ObjectId(event_id)})
    return stringify_object_ids(result)


async def db_create_rsvp_invite(email: str, db: AsyncDatabase) -> Dict[str, Any]:
    rsvp_dict = {"email": email, "status": RSVPStatus.PENDING}

    result = await db[RSVPS_COLLECTION].insert_one(rsvp_dict)

    rsvp_dict["_id"] = result.inserted_id
    return stringify_object_ids(rsvp_dict)


async def db_record_rsvp_response(
    rsvp_id: str, rsvp_status: RSVPStatus, db: AsyncDatabase
) -> None:
    await db[RSVPS_COLLECTION].update_one(
        {"_id": ObjectId(rsvp_id)},
        {"$set": {"status": rsvp_status}},
    )
