from fastapi import HTTPException
from pymongo.asynchronous.database import AsyncDatabase

from app.db.event import db_get_event_or_none
from app.schemas.event import Event


async def get_event_service(event_id: str, db: AsyncDatabase) -> Event:

    event_in_db_dict = await db_get_event_or_none(event_id, db)
    if event_in_db_dict is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find an event for this id: id={event_id}",
        )

    return Event(
        id=event_in_db_dict["_id"],
        name=event_in_db_dict["name"],
        description=event_in_db_dict["description"],
    )
