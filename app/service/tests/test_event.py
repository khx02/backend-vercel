from unittest.mock import AsyncMock, patch
import pytest

from app.schemas.event import Event
from app.service.event import get_event_service
from app.test_shared.constants import (
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_ID,
    MOCK_EVENT_NAME,
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
