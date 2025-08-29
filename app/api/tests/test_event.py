from unittest.mock import AsyncMock, patch

import pytest

from app.api.event import get_event, reply_rsvp, send_rsvp_email
from app.schemas.event import (
    Event,
    GetEventResponse,
    ReplyRSVPResponse,
    SendRSVPEmailRequest,
    SendRSVPEmailResponse,
)
from app.test_shared.constants import (
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_ID,
    MOCK_EVENT_NAME,
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

    assert isinstance(result, ReplyRSVPResponse)
