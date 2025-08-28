from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db
from app.schemas.event import GetEventResponse
from app.service.event import get_event_service

router = APIRouter()


@router.get("/get-event/{event_id}")
async def get_event(
    event_id: str, db: AsyncDatabase = Depends(get_db)
) -> GetEventResponse:
    return GetEventResponse(event=await get_event_service(event_id, db))
