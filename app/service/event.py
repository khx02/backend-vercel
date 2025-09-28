from datetime import datetime, timedelta, timezone
import os
from fastapi import HTTPException
from pymongo.asynchronous.database import AsyncDatabase
from typing import List
from dateutil import parser

from app.db.event import (
    db_add_rsvp_id_to_event,
    db_create_rsvp_invite,
    db_get_event_or_none,
    db_get_rsvps_by_ids,
    db_record_rsvp_response,
    db_update_event_details,
)
from app.schemas.event import RSVP, Event, RSVPStatus, UpdateEventDetailsRequest

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.constants import BASE_URL
from app.core.scheduler import scheduler
from app.core.templates import env


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
        start=event_in_db_dict["start"],
        end=event_in_db_dict["end"],
        colour=event_in_db_dict["colour"],
        location=event_in_db_dict["location"],
    )


# This should never fail outside of infrastructure / network related errors
# It will still return as normal if the email is invalid
def send_rsvp_invite_email(email: str, event: Event, rsvp_id: str) -> int:
    start_dt_local = parser.isoparse(event.start).astimezone()
    formatted_start = start_dt_local.strftime("%A, %B %d, %Y at %I:%M %p %Z")

    end_dt_local = parser.isoparse(event.end).astimezone()
    formatted_end = end_dt_local.strftime("%A, %B %d, %Y at %I:%M %p %Z")

    accept_url = f"{BASE_URL}/events/reply-rsvp/{rsvp_id}/accepted"
    decline_url = f"{BASE_URL}/events/reply-rsvp/{rsvp_id}/declined"

    template = env.get_template("rsvp_request_email.html")
    html_content = template.render(
        event_name=event.name,
        event_description=event.description,
        event_start=formatted_start,
        event_end=formatted_end,
        event_location=event.location,
        accept_url=accept_url,
        decline_url=decline_url,
    )

    message = Mail(
        from_email="admin@clubsync.club",
        to_emails=email,
        subject="You're invited to an event!",
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(os.environ["SENDGRID_KEY"])
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


async def send_rsvp_email_service(event_id: str, email: str, db: AsyncDatabase) -> str:
    event = await get_event_service(event_id, db)

    rsvp_in_db_dict = await db_create_rsvp_invite(email, db)
    rsvp_id = rsvp_in_db_dict["_id"]

    await db_add_rsvp_id_to_event(event_id, rsvp_id, db)

    send_rsvp_invite_email(email, event, rsvp_id)

    return rsvp_id


async def reply_rsvp_service(
    rsvp_id: str, rsvp_status: RSVPStatus, db: AsyncDatabase
) -> None:

    await db_record_rsvp_response(rsvp_id, rsvp_status, db)


async def get_event_rsvps_service(event_id: str, db: AsyncDatabase) -> List[RSVP]:

    event_in_db_dict = await db_get_event_or_none(event_id, db)
    if event_in_db_dict is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find an event for this id: id={event_id}",
        )

    rsvp_ids = event_in_db_dict["rsvp_ids"]
    rsvps_in_db_dict_list = await db_get_rsvps_by_ids(rsvp_ids, db)

    rsvps = [
        RSVP(
            id=rsvp_in_db_dict["_id"],
            email=rsvp_in_db_dict["email"],
            rsvp_status=RSVPStatus(rsvp_in_db_dict["status"]),
        )
        for rsvp_in_db_dict in rsvps_in_db_dict_list
    ]

    return rsvps


async def update_event_details_service(
    event_id: str,
    update_event_details_request: UpdateEventDetailsRequest,
    db: AsyncDatabase,
) -> None:
    event_in_db_dict = await db_get_event_or_none(event_id, db)
    if event_in_db_dict is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find an event for this id: id={event_id}",
        )

    new_event_details = {
        "name": update_event_details_request.name,
        "description": update_event_details_request.description,
        "public": update_event_details_request.public,
    }

    await db_update_event_details(event_id, new_event_details, db)


# Reminder email scheduling logic
async def send_reminder_email(event_id: str, when: str, db: AsyncDatabase):

    event = await get_event_service(event_id, db)
    if not event:
        return

    rsvps = await get_event_rsvps_service(event_id, db)

    start_dt_local = parser.isoparse(event.start).astimezone()
    formatted_start = start_dt_local.strftime("%A, %B %d, %Y at %I:%M %p %Z")

    template = env.get_template("event_reminder_email.html")
    html_content = template.render(
        event_name=event.name,
        when=when,
        event_location=event.location,
        event_time=formatted_start,
    )

    for rsvp in rsvps:
        if rsvp.rsvp_status != RSVPStatus.ACCEPTED:
            continue

        message = Mail(
            from_email="admin@clubsync.club",
            to_emails=rsvp.email,
            subject=f"Reminder: You have an event coming up!",
            html_content=html_content,
        )
        try:
            sg = SendGridAPIClient(os.environ["SENDGRID_KEY"])
            response = sg.send(message)
            return response.status_code
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to send email: {str(e)}"
            )


# TODO: Make the scheduling reconfigurable if event details change
def schedule_event_reminders(
    event_id: str, event_start: str, db: AsyncDatabase
) -> None:
    event_start_time = parser.isoparse(event_start)

    reminders = {
        "10 minutes": event_start_time - timedelta(minutes=10),
        "1 hour": event_start_time - timedelta(hours=1),
        "1 day": event_start_time - timedelta(days=1),
        "1 week": event_start_time - timedelta(weeks=1),
    }

    for label, run_time in reminders.items():
        if run_time > datetime.now(timezone.utc):
            scheduler.add_job(
                send_reminder_email,
                trigger="date",
                run_date=run_time,
                args=[event_id, label, db],
                id=f"{event_id}-{label}",
                replace_existing=True,
            )
