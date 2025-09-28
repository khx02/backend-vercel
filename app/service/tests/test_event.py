from unittest.mock import AsyncMock, patch
import pytest

from app.schemas.event import Event, RSVPStatus, UpdateEventDetailsRequest
from app.service.event import (
    get_event_rsvps_service,
    get_event_service,
    reply_rsvp_service,
    send_rsvp_email_service,
    update_event_details_service,
)
from app.service.team import get_team_events_service
from app.test_shared.constants import (
    MOCK_EVENT_COLOUR,
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_END,
    MOCK_EVENT_ID,
    MOCK_EVENT_LOCATION,
    MOCK_EVENT_NAME,
    MOCK_EVENT_START,
    MOCK_INSERTED_ID,
    MOCK_NEW_EVENT_DESCRIPTION,
    MOCK_NEW_EVENT_NAME,
    MOCK_RSVP_2_ID,
    MOCK_RSVP_ID,
    MOCK_USER_2_EMAIL,
    MOCK_USER_EMAIL,
)


@pytest.mark.asyncio
@patch("app.service.event.db_get_event_or_none")
async def test_get_event_service_success(mock_db_get_event_or_none):
    mock_db = AsyncMock()
    mock_db_get_event_or_none.return_value = {
        "_id": MOCK_EVENT_ID,
        "name": MOCK_EVENT_NAME,
        "description": MOCK_EVENT_DESCRIPTION,
        "rsvp_ids": [],
        "start": MOCK_EVENT_START,
        "end": MOCK_EVENT_END,
        "colour": MOCK_EVENT_COLOUR,
        "location": MOCK_EVENT_LOCATION,
    }

    result = await get_event_service(MOCK_EVENT_ID, mock_db)

    assert isinstance(result, Event)
    assert result.id == MOCK_EVENT_ID
    assert result.name == MOCK_EVENT_NAME
    assert result.description == MOCK_EVENT_DESCRIPTION
    assert result.rsvp_ids == []


@pytest.mark.asyncio
@patch("app.service.event.send_rsvp_invite_email")
@patch("app.service.event.db_add_rsvp_id_to_event")
@patch("app.service.event.db_create_rsvp_invite")
@patch("app.service.event.get_event_service")
async def test_send_rsvp_email_service_success(
    mock_get_event_service,
    mock_db_create_rsvp_invite,
    mock_db_add_rsvp_id_to_event,
    mock_send_rsvp_invite_email,
):
    mock_db = AsyncMock()
    mock_get_event_service.return_value = Event(
        id=MOCK_EVENT_ID,
        name=MOCK_EVENT_NAME,
        description=MOCK_EVENT_DESCRIPTION,
        start=MOCK_EVENT_START,
        end=MOCK_EVENT_END,
        colour=MOCK_EVENT_COLOUR,
        location=MOCK_EVENT_LOCATION,
        rsvp_ids=[],
    )

    mock_db_create_rsvp_invite.return_value = {
        "_id": MOCK_INSERTED_ID,
        "email": MOCK_USER_EMAIL,
        "status": RSVPStatus.PENDING,
    }
    mock_db_add_rsvp_id_to_event.return_value = None
    mock_send_rsvp_invite_email.return_value = None

    result = await send_rsvp_email_service(MOCK_USER_EMAIL, MOCK_EVENT_ID, mock_db)

    assert result == MOCK_INSERTED_ID


@pytest.mark.asyncio
@patch("app.service.event.db_record_rsvp_response")
async def test_reply_rsvp_service(mock_db_record_rsvp_response):
    mock_db = AsyncMock()
    mock_db_record_rsvp_response.return_value = None

    result = await reply_rsvp_service(MOCK_RSVP_ID, RSVPStatus.ACCEPTED, mock_db)

    assert result is None


@pytest.mark.asyncio
@patch("app.service.event.db_get_rsvps_by_ids")
@patch("app.service.event.db_get_event_or_none")
async def test_get_event_rsvps_service_success(
    mock_db_get_event_or_none, mock_db_get_rsvps_by_ids
):
    mock_db = AsyncMock()
    mock_db_get_event_or_none.return_value = {
        "_id": MOCK_EVENT_ID,
        "name": MOCK_EVENT_NAME,
        "description": MOCK_EVENT_DESCRIPTION,
        "rsvp_ids": [MOCK_RSVP_ID, MOCK_RSVP_2_ID],
    }
    mock_db_get_rsvps_by_ids.return_value = [
        {
            "_id": MOCK_RSVP_ID,
            "email": MOCK_USER_EMAIL,
            "status": RSVPStatus.PENDING,
        },
        {
            "_id": MOCK_RSVP_2_ID,
            "email": MOCK_USER_2_EMAIL,
            "status": RSVPStatus.PENDING,
        },
    ]

    result = await get_event_rsvps_service(MOCK_EVENT_ID, mock_db)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].id == MOCK_RSVP_ID
    assert result[0].email == MOCK_USER_EMAIL
    assert result[0].rsvp_status == RSVPStatus.PENDING
    assert result[1].id == MOCK_RSVP_2_ID
    assert result[1].email == MOCK_USER_2_EMAIL
    assert result[1].rsvp_status == RSVPStatus.PENDING


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
@patch("app.service.team.db_get_events_by_ids")
async def test_get_team_events_service_success(
    mock_db_get_events_by_ids, mock_db_get_team_by_id
):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_EVENT_ID,
        "name": MOCK_EVENT_NAME,
        "description": MOCK_EVENT_DESCRIPTION,
        "rsvp_ids": [],
        "event_ids": [MOCK_EVENT_ID],
        "member_ids": [MOCK_USER_EMAIL],
    }
    mock_db_get_events_by_ids.return_value = [
        {
            "_id": MOCK_EVENT_ID,
            "name": MOCK_EVENT_NAME,
            "description": MOCK_EVENT_DESCRIPTION,
            "rsvp_ids": [],
            "start": MOCK_EVENT_START,
            "end": MOCK_EVENT_END,
            "colour": MOCK_EVENT_COLOUR,
            "location": MOCK_EVENT_LOCATION,
        }
    ]
    result = await get_team_events_service(MOCK_EVENT_ID, MOCK_USER_EMAIL, mock_db)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].id == MOCK_EVENT_ID
    assert result[0].name == MOCK_EVENT_NAME
    assert result[0].description == MOCK_EVENT_DESCRIPTION
    assert result[0].rsvp_ids == []


@pytest.mark.asyncio
@patch("app.service.event.db_update_event_details")
@patch("app.service.event.db_get_event_or_none")
async def test_update_event_details_service(
    mock_db_get_event_or_none, mock_db_update_event_details
):
    mock_db = AsyncMock()
    mock_db_get_event_or_none.return_value = {
        "_id": MOCK_EVENT_ID,
        "name": MOCK_EVENT_NAME,
        "description": MOCK_EVENT_DESCRIPTION,
        "rsvp_ids": [],
    }
    mock_db_update_event_details.return_value = {
        "_id": MOCK_EVENT_ID,
        "name": MOCK_NEW_EVENT_NAME,
        "description": MOCK_NEW_EVENT_DESCRIPTION,
        "rsvp_ids": [],
    }
    mock_update_event_details_request = UpdateEventDetailsRequest(
        name=MOCK_NEW_EVENT_NAME, description=MOCK_NEW_EVENT_DESCRIPTION, public=True
    )

    result = await update_event_details_service(
        MOCK_EVENT_ID, mock_update_event_details_request, mock_db
    )

    assert result is None
