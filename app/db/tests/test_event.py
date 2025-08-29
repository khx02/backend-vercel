"""
@pytest.mark.asyncio
async def test_db_create_team_success():
    mock_db = AsyncMock()
    mock_teams_collection = AsyncMock()
    mock_teams_collection.insert_one.return_value = AsyncMock(
        inserted_id=ObjectId(MOCK_INSERTED_ID)
    )
    mock_db.__getitem__.return_value = mock_teams_collection

    result = await db_create_team(MOCK_USER_ID, MOCK_TEAM_NAME, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_INSERTED_ID
    assert result["name"] == MOCK_TEAM_NAME
    assert result["member_ids"] == [MOCK_USER_ID]
    assert result["exec_member_ids"] == [MOCK_USER_ID]
    assert result["project_ids"] == []

"""

from unittest.mock import AsyncMock
from bson import ObjectId
import pytest

from app.db.event import (
    db_create_rsvp_invite,
    db_get_event_or_none,
    db_record_rsvp_response,
)
from app.schemas.event import RSVPStatus
from app.test_shared.constants import (
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_ID,
    MOCK_EVENT_NAME,
    MOCK_INSERTED_ID,
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
