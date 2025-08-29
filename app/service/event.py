from email import message
import os
from fastapi import HTTPException
from httpx import get
from pymongo.asynchronous.database import AsyncDatabase

from app.db.event import (
    db_create_rsvp_invite,
    db_get_event_or_none,
    db_record_rsvp_response,
)
from app.schemas.event import Event, RSVPStatus

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.constants import BASE_URL


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
        rsvp_ids=event_in_db_dict["rsvp_ids"],
    )


# This should never fail outside of infrastructure / network related errors
# It will still return as normal if the email is invalid
def send_rsvp_invite_email(email: str, event_name: str, rsvp_id: str) -> int:
    accept_url = f"{BASE_URL}/events/reply-rsvp/{rsvp_id}/accepted"
    decline_url = f"{BASE_URL}/events/reply-rsvp/{rsvp_id}/declined"
    mail_html_content = f"""
    <p>You have been invited to the event: <b>{event_name}</b>.</p>
    <p>Please click the following link to RSVP:</p>
    <p><a href="{accept_url}">Accept</a> | <a href="{decline_url}">Decline</a></p>
    """
    message = Mail(
        from_email="admin@clubsync.club",
        to_emails=email,
        subject="You're invited to an event!",
        html_content=mail_html_content,
    )
    try:
        sg = SendGridAPIClient(os.environ["SENDGRID_KEY"])
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


async def send_rsvp_email_service(event_id: str, email: str, db: AsyncDatabase) -> None:
    event = await get_event_service(event_id, db)

    rsvp_in_db_dict = await db_create_rsvp_invite(email, db)
    rsvp_id = rsvp_in_db_dict["_id"]

    send_rsvp_invite_email(email, event.name, rsvp_id)


async def reply_rsvp_service(
    rsvp_id: str, rsvp_status: RSVPStatus, db: AsyncDatabase
) -> None:

    await db_record_rsvp_response(rsvp_id, rsvp_status, db)
