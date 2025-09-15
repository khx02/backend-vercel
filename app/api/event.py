from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db
from app.schemas.event import (
    GetEventRSVPsResponse,
    GetEventResponse,
    RSVPStatus,
    ReplyRSVPResponse,
    SendRSVPEmailRequest,
    SendRSVPEmailResponse,
)
from app.service.event import (
    get_event_rsvps_service,
    get_event_service,
    reply_rsvp_service,
    send_rsvp_email_service,
)

router = APIRouter()


@router.get("/get-event/{event_id}")
async def get_event(
    event_id: str, db: AsyncDatabase = Depends(get_db)
) -> GetEventResponse:
    return GetEventResponse(event=await get_event_service(event_id, db))


@router.post("/send-rsvp-email/{event_id}")
async def send_rsvp_email(
    event_id: str,
    send_rsvp_email_request: SendRSVPEmailRequest,
    db: AsyncDatabase = Depends(get_db),
) -> SendRSVPEmailResponse:

    await send_rsvp_email_service(event_id, send_rsvp_email_request.email, db)

    return SendRSVPEmailResponse()


@router.get("/reply-rsvp/{rsvp_id}/{rsvp_status}")
async def reply_rsvp(
    rsvp_id: str,
    rsvp_status: RSVPStatus,
    db: AsyncDatabase = Depends(get_db),
) -> ReplyRSVPResponse:

    await reply_rsvp_service(rsvp_id, rsvp_status, db)

    return ReplyRSVPResponse()

@router.get("/get-event-rsvps/{event_id}")
async def get_event_rsvps(event_id: str, db: AsyncDatabase = Depends(get_db)) -> GetEventRSVPsResponse:

    rsvps = await get_event_rsvps_service(event_id, db)

    return GetEventRSVPsResponse(rsvps=rsvps)