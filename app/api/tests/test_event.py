from unittest.mock import AsyncMock, patch

from fastapi.responses import RedirectResponse
import pytest

from app.api.event import (
    get_event,
    get_event_rsvps,
    reply_rsvp,
    send_rsvp_email,
    update_event_details,
)
from app.schemas.event import (
    Event,
    GetEventRSVPsResponse,
    GetEventResponse,
    ReplyRSVPResponse,
    SendRSVPEmailRequest,
    SendRSVPEmailResponse,
    UpdateEventDetailsRequest,
    UpdateEventDetailsResponse,
)
from app.test_shared.constants import (
    MOCK_EVENT_COLOUR,
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_END,
    MOCK_EVENT_ID,
    MOCK_EVENT_LOCATION,
    MOCK_EVENT_NAME,
    MOCK_EVENT_START,
    MOCK_USER_EMAIL,
)


@pytest.mark.asyncio
@patch("app.api.event.get_event_service")
async def test_create_event_service_success(mock_get_event_service):
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

    result = await get_event(MOCK_EVENT_ID, mock_db)

    assert isinstance(result, GetEventResponse)
    assert result.event.id == MOCK_EVENT_ID
    assert result.event.name == MOCK_EVENT_NAME
    assert result.event.description == MOCK_EVENT_DESCRIPTION
    assert result.event.rsvp_ids == []


@pytest.mark.asyncio
@patch("app.api.event.send_rsvp_email_service")
async def test_send_rsvp_email_service_success(mock_send_rsvp_email_service):
    mock_db = AsyncMock()
    mock_send_rsvp_email_service.return_value = None
    mock_send_rsvp_email_request = SendRSVPEmailRequest(email=MOCK_USER_EMAIL)

    result = await send_rsvp_email(MOCK_EVENT_ID, mock_send_rsvp_email_request, mock_db)

    assert isinstance(result, SendRSVPEmailResponse)


@pytest.mark.asyncio
@patch("app.api.event.reply_rsvp_service")
async def test_reply_rsvp_service_success(mock_reply_rsvp_service):
    mock_db = AsyncMock()
    mock_reply_rsvp_service.return_value = None

    result = await reply_rsvp(mock_reply_rsvp_service, mock_db)

    assert isinstance(result, RedirectResponse)


@pytest.mark.asyncio
@patch("app.api.event.get_event_rsvps_service")
async def test_get_event_rsvps_service_success(mock_get_event_rsvps_service):
    mock_db = AsyncMock()
    mock_get_event_rsvps_service.return_value = []

    result = await get_event_rsvps(MOCK_EVENT_ID, mock_db)

    assert isinstance(result, GetEventRSVPsResponse)
    assert result.rsvps == []


@pytest.mark.asyncio
@patch("app.api.event.update_event_details_service")
async def test_update_event_details_service_success(mock_update_event_details_service):
    mock_db = AsyncMock()
    mock_update_event_details_service.return_value = None
    mock_update_event_details_request = UpdateEventDetailsRequest(
        name=MOCK_EVENT_NAME, description=MOCK_EVENT_DESCRIPTION, public=True
    )

    result = await update_event_details(
        MOCK_EVENT_ID, mock_update_event_details_request, mock_db
    )

    assert isinstance(result, UpdateEventDetailsResponse)
