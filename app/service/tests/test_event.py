from unittest.mock import AsyncMock, patch
import pytest

from app.schemas.event import Event, RSVPStatus
from app.service.event import (
    get_event_rsvps_service,
    get_event_service,
    reply_rsvp_service,
    send_rsvp_email_service,
)
from app.test_shared.constants import (
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_ID,
    MOCK_EVENT_NAME,
    MOCK_INSERTED_ID,
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


"""
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
"""


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
    print(result)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].id == MOCK_RSVP_ID
    assert result[0].email == MOCK_USER_EMAIL
    assert result[0].rsvp_status == RSVPStatus.PENDING
    assert result[1].id == MOCK_RSVP_2_ID
    assert result[1].email == MOCK_USER_2_EMAIL
    assert result[1].rsvp_status == RSVPStatus.PENDING
