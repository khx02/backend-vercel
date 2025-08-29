from unittest.mock import AsyncMock, patch
import pytest

from app.schemas.event import Event, RSVPStatus
from app.service.event import (
    get_event_service,
    reply_rsvp_service,
    send_rsvp_email_service,
)
from app.test_shared.constants import (
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_ID,
    MOCK_EVENT_NAME,
    MOCK_INSERTED_ID,
    MOCK_RSVP_ID,
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
    }

    result = await get_event_service(MOCK_EVENT_ID, mock_db)

    assert isinstance(result, Event)
    assert result.id == MOCK_EVENT_ID
    assert result.name == MOCK_EVENT_NAME
    assert result.description == MOCK_EVENT_DESCRIPTION
    assert result.rsvp_ids == []


@pytest.mark.asyncio
@patch("app.service.event.send_rsvp_invite_email")
@patch("app.service.event.db_create_rsvp_invite")
@patch("app.service.event.get_event_service")
async def test_send_rsvp_email_service_success(
    mock_get_event_service, mock_db_create_rsvp_invite, mock_send_rsvp_invite_email
):
    mock_db = AsyncMock()
    mock_get_event_service.return_value = Event(
        id=MOCK_EVENT_ID,
        name=MOCK_EVENT_NAME,
        description=MOCK_EVENT_DESCRIPTION,
        rsvp_ids=[],
    )
    mock_db_create_rsvp_invite.return_value = {
        "_id": MOCK_INSERTED_ID,
        "email": MOCK_USER_EMAIL,
        "status": RSVPStatus.PENDING,
    }
    mock_send_rsvp_invite_email.return_value = None

    result = await send_rsvp_email_service(MOCK_USER_EMAIL, MOCK_EVENT_ID, mock_db)

    assert result is None


@pytest.mark.asyncio
@patch("app.service.event.db_record_rsvp_response")
async def test_reply_rsvp_service(mock_db_record_rsvp_response):
    mock_db = AsyncMock()
    mock_db_record_rsvp_response.return_value = None

    result = await reply_rsvp_service(MOCK_RSVP_ID, RSVPStatus.ACCEPTED, mock_db)

    assert result is None
