from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
import pytest

from app.db.event import (
    db_create_rsvp_invite,
    db_get_event_or_none,
    db_get_events_by_ids,
    db_get_rsvps_by_ids,
    db_record_rsvp_response,
    db_update_event_details,
)
from app.schemas.event import RSVPStatus
from app.test_shared.constants import (
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_ID,
    MOCK_EVENT_NAME,
    MOCK_INSERTED_ID,
    MOCK_NEW_EVENT_DESCRIPTION,
    MOCK_NEW_EVENT_NAME,
    MOCK_RSVP_ID,
    MOCK_RSVP_STATUS,
    MOCK_USER_EMAIL,
)


@pytest.mark.asyncio
async def test_db_get_event_or_none_success():
    mock_db = AsyncMock()
    mock_events_collection = AsyncMock()
    mock_events_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_EVENT_ID),
        "name": MOCK_EVENT_NAME,
        "description": MOCK_EVENT_DESCRIPTION,
    }
    mock_db.__getitem__.return_value = mock_events_collection

    result = await db_get_event_or_none(MOCK_EVENT_ID, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_EVENT_ID
    assert result["name"] == MOCK_EVENT_NAME
    assert result["description"] == MOCK_EVENT_DESCRIPTION


@pytest.mark.asyncio
async def test_db_create_rsvp_invite_success():
    mock_db = AsyncMock()
    mock_rsvps_collection = AsyncMock()
    mock_rsvps_collection.insert_one.return_value = AsyncMock(
        inserted_id=ObjectId(MOCK_INSERTED_ID)
    )
    mock_db.__getitem__.return_value = mock_rsvps_collection

    result = await db_create_rsvp_invite(MOCK_USER_EMAIL, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_INSERTED_ID
    assert result["email"] == MOCK_USER_EMAIL
    assert result["status"] == RSVPStatus.PENDING


@pytest.mark.asyncio
async def test_db_record_rsvp_response_success():
    mock_db = AsyncMock()
    mock_rsvps_collection = AsyncMock()
    mock_db.__getitem__.return_value = mock_rsvps_collection

    result = await db_record_rsvp_response(
        MOCK_INSERTED_ID, RSVPStatus.ACCEPTED, mock_db
    )

    assert result is None


@pytest.mark.asyncio
async def test_db_get_rsvps_by_ids_success():
    mock_db = AsyncMock()
    mock_rsvps_collection = MagicMock()

    mock_db.__getitem__.return_value = mock_rsvps_collection

    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(
        return_value=[
            {
                "_id": ObjectId(MOCK_RSVP_ID),
                "rsvp_status": MOCK_RSVP_STATUS,
                "email": MOCK_USER_EMAIL,
            }
        ]
    )

    mock_rsvps_collection.find.return_value = mock_cursor

    result = await db_get_rsvps_by_ids([MOCK_RSVP_ID], mock_db)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)
    assert result[0] == {
        "_id": MOCK_RSVP_ID,
        "rsvp_status": MOCK_RSVP_STATUS,
        "email": MOCK_USER_EMAIL,
    }


@pytest.mark.asyncio
async def test_db_get_events_by_ids_success():
    mock_db = AsyncMock()
    mock_events_collection = MagicMock()

    mock_db.__getitem__.return_value = mock_events_collection

    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(
        return_value=[
            {
                "_id": ObjectId(MOCK_EVENT_ID),
                "name": MOCK_EVENT_NAME,
                "description": MOCK_EVENT_DESCRIPTION,
                "rsvp_ids": [],
            }
        ]
    )

    mock_events_collection.find.return_value = mock_cursor

    result = await db_get_events_by_ids([MOCK_EVENT_ID], mock_db)

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)
    assert result[0] == {
        "_id": MOCK_EVENT_ID,
        "name": MOCK_EVENT_NAME,
        "description": MOCK_EVENT_DESCRIPTION,
        "rsvp_ids": [],
    }


@pytest.mark.asyncio
async def test_db_update_event_details_success():
    mock_db = AsyncMock()
    mock_events_collection = AsyncMock()
    mock_events_collection.update_one.return_value = None
    mock_db.__getitem__.return_value = mock_events_collection
    mock_update_event_details_request = {
        "name": MOCK_NEW_EVENT_NAME,
        "description": MOCK_NEW_EVENT_DESCRIPTION,
        "public": True,
    }

    result = await db_update_event_details(
        MOCK_EVENT_ID,
        mock_update_event_details_request,
        mock_db,
    )

    assert result is None
