from unittest.mock import AsyncMock, patch

import pytest

from app.api.event import get_event
from app.schemas.event import Event, GetEventResponse
from app.test_shared.constants import (
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_ID,
    MOCK_EVENT_NAME,
)


@pytest.mark.asyncio
@patch("app.api.event.get_event_service")
async def test_create_event_service_success(mock_get_event_service):
    mock_db = AsyncMock()
    mock_get_event_service.return_value = Event(
        id=MOCK_EVENT_ID, name=MOCK_EVENT_NAME, description=MOCK_EVENT_DESCRIPTION
    )

    result = await get_event(MOCK_EVENT_ID, mock_db)

    assert isinstance(result, GetEventResponse)
    assert result.event.id == MOCK_EVENT_ID
    assert result.event.name == MOCK_EVENT_NAME
    assert result.event.description == MOCK_EVENT_DESCRIPTION
