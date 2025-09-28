from unittest.mock import AsyncMock, patch

from bson import ObjectId
from fastapi import HTTPException
import pytest

from app.schemas.event import Event
from app.schemas.team import (
    CreateEventRequest,
    CreateTeamResponse,
    JoinTeamResponse,
    KickTeamMemberResponse,
    LeaveTeamResponse,
    PromoteTeamMemberResponse,
    TeamModel,
)
from app.service.team import (
    create_event_for_team_service,
    create_team_service,
    delete_event_service,
    delete_project_service,
    delete_team_service,
    join_team_service,
    kick_team_member_service,
    leave_team_service,
    promote_team_member_service,
)

from app.test_shared.constants import (
    MOCK_EVENT_COLOUR,
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_END,
    MOCK_EVENT_ID,
    MOCK_EVENT_LOCATION,
    MOCK_EVENT_NAME,
    MOCK_EVENT_START,
    MOCK_PROJECT_DESCRIPTION,
    MOCK_PROJECT_ID,
    MOCK_PROJECT_NAME,
    MOCK_TEAM_SHORT_ID,
    MOCK_USER_ID,
    MOCK_USER_2_ID,
    MOCK_TEAM_NAME,
    MOCK_TEAM_ID,
)


@pytest.mark.asyncio
@patch("app.service.team.db_create_team")
@patch("app.service.team.db_get_team_by_short_id")
async def test_create_team_service_success(
    mock_db_get_team_by_short_id, mock_db_create_team
):
    mock_db = AsyncMock()
    mock_db_get_team_by_short_id.return_value = None
    mock_db_create_team.return_value = {
        "_id": MOCK_TEAM_ID,
        "short_id": MOCK_TEAM_SHORT_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "project_ids": [],
        "event_ids": [],
    }

    result = await create_team_service(MOCK_USER_ID, MOCK_TEAM_NAME, mock_db)

    assert isinstance(result, CreateTeamResponse)
    assert isinstance(result.team, TeamModel)
    assert result.team.id == MOCK_TEAM_ID
    assert result.team.short_id == MOCK_TEAM_SHORT_ID
    assert result.team.name == MOCK_TEAM_NAME
    assert result.team.member_ids == [MOCK_USER_ID]
    assert result.team.exec_member_ids == [MOCK_USER_ID]
    assert result.team.project_ids == []
    assert result.team.event_ids == []


@pytest.mark.asyncio
@patch("app.service.team.db_join_team")
@patch("app.service.team.db_get_team_by_id")
async def test_join_team_service_success(mock_db_get_team_by_id, mock_db_join_team):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "event_ids": [],
    }
    mock_db_join_team.return_value = None

    result = await join_team_service(MOCK_TEAM_ID, MOCK_USER_2_ID, mock_db)

    assert isinstance(result, JoinTeamResponse)


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
async def test_join_team_service_failure_team_not_exist(mock_db_get_team_by_id):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await join_team_service(MOCK_TEAM_ID, MOCK_USER_2_ID, mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == f"Team does not exist: team_id={MOCK_TEAM_ID}"


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
async def test_join_team_service_failure_user_already_in_team(mock_db_get_team_by_id):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "event_ids": [],
    }

    with pytest.raises(HTTPException) as exc_info:
        await join_team_service(MOCK_TEAM_ID, MOCK_USER_2_ID, mock_db)

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == f"User is already in the team: user_id={MOCK_USER_2_ID}, team_id={MOCK_TEAM_ID}"
    )


@pytest.mark.asyncio
@patch("app.service.team.db_promote_team_member")
@patch("app.service.team.db_get_team_by_id")
async def test_promote_team_member_service_success(
    mock_db_get_team_by_id, mock_db_promote_team_member
):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "event_ids": [],
    }
    mock_db_promote_team_member.return_value = None

    result = await promote_team_member_service(
        MOCK_TEAM_ID, MOCK_USER_2_ID, MOCK_USER_ID, mock_db
    )

    assert isinstance(result, PromoteTeamMemberResponse)


@pytest.mark.asyncio
@patch("app.service.team.db_promote_team_member")
@patch("app.service.team.db_get_team_by_id")
async def test_promote_team_member_service_failure_no_permission(
    mock_db_get_team_by_id, mock_db_promote_team_member
):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "event_ids": [],
    }
    mock_db_promote_team_member.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await promote_team_member_service(
            MOCK_TEAM_ID, MOCK_USER_2_ID, MOCK_USER_2_ID, mock_db
        )

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == f"User does not have permission to promote members in team: user_id={MOCK_USER_2_ID}, team_id={MOCK_TEAM_ID}"
    )


@pytest.mark.asyncio
@patch("app.service.team.db_leave_team")
@patch("app.service.team.db_get_team_by_id")
async def test_leave_team_service_success(mock_db_get_team_by_id, mock_db_leave_team):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "event_ids": [],
    }
    mock_db_leave_team.return_value = None

    result = await leave_team_service(MOCK_TEAM_ID, MOCK_USER_2_ID, mock_db)

    assert isinstance(result, LeaveTeamResponse)


@pytest.mark.asyncio
@patch("app.service.team.db_delete_team")
@patch("app.service.team.db_get_team_by_id")
async def test_leave_team_service_last_executive(
    mock_db_get_team_by_id, mock_db_delete_team
):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "event_ids": [],
    }
    mock_db_delete_team.return_value = None

    result = await leave_team_service(MOCK_TEAM_ID, MOCK_USER_ID, mock_db)

    assert isinstance(result, LeaveTeamResponse)


@pytest.mark.asyncio
@patch("app.service.team.db_delete_team")
@patch("app.service.team.db_get_team_by_id")
async def test_db_delete_team_success(mock_db_get_team_by_id, mock_db_delete_team):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "event_ids": [],
    }
    mock_db_delete_team.return_value = None

    result = await delete_team_service(MOCK_TEAM_ID, MOCK_USER_ID, mock_db)

    assert result is None


@pytest.mark.asyncio
@patch("app.service.team.db_kick_team_member")
@patch("app.service.team.db_get_team_by_id")
async def test_kick_team_member_service_success(
    mock_db_get_team_by_id, mock_db_kick_team_member
):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "event_ids": [],
    }
    mock_db_kick_team_member.return_value = None

    result = await kick_team_member_service(
        MOCK_TEAM_ID, MOCK_USER_2_ID, MOCK_USER_ID, mock_db
    )

    assert isinstance(result, KickTeamMemberResponse)


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
async def test_kick_team_member_service_failure_kick_exec(mock_db_get_team_by_id):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "event_ids": [],
    }

    with pytest.raises(HTTPException) as exc_info:
        await kick_team_member_service(
            MOCK_TEAM_ID, MOCK_USER_2_ID, MOCK_USER_ID, mock_db
        )

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == f"Member is an executive and cannot be kicked: member_id={MOCK_USER_2_ID}, team_id={MOCK_TEAM_ID}"
    )


@pytest.mark.asyncio
@patch("app.service.team.db_delete_project")
@patch("app.service.team.db_get_project_by_id")
@patch("app.service.team.db_get_team_by_id")
async def test_delete_project_service_success(
    mock_db_get_team_by_id, mock_db_get_project_by_id, mock_db_delete_project
):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "project_ids": [MOCK_PROJECT_ID],
        "event_ids": [],
    }
    mock_db_get_project_by_id.return_value = {
        "_id": MOCK_PROJECT_ID,
        "name": MOCK_PROJECT_NAME,
        "description": MOCK_PROJECT_DESCRIPTION,
        "todo_statuses": [
            {"id": ObjectId(), "name": "To Do"},
            {"id": ObjectId(), "name": "In Progress"},
            {"id": ObjectId(), "name": "Done"},
        ],
        "todo_ids": [],
    }
    mock_db_delete_project.return_value = None

    result = await delete_project_service(
        MOCK_TEAM_ID, MOCK_PROJECT_ID, MOCK_USER_ID, mock_db
    )

    assert result is None


@pytest.mark.asyncio
@patch("app.service.team.db_create_event_for_team")
async def test_create_event_for_team_service_success(mock_db_create_event_for_team):
    mock_db = AsyncMock()
    mock_db_create_event_for_team.return_value = {
        "_id": MOCK_EVENT_ID,
        "name": MOCK_EVENT_NAME,
        "description": MOCK_EVENT_DESCRIPTION,
        "rsvp_ids": [],
        "start": MOCK_EVENT_START,
        "end": MOCK_EVENT_END,
        "colour": MOCK_EVENT_COLOUR,
        "location": MOCK_EVENT_LOCATION,
    }
    mock_create_event_request = CreateEventRequest(
        name=MOCK_EVENT_NAME,
        description=MOCK_EVENT_DESCRIPTION,
        start=MOCK_EVENT_START,
        end=MOCK_EVENT_END,
        colour=MOCK_EVENT_COLOUR,
        location=MOCK_EVENT_LOCATION,
    )

    result = await create_event_for_team_service(
        MOCK_TEAM_ID, mock_create_event_request, mock_db
    )

    assert isinstance(result, Event)
    assert result.id == MOCK_EVENT_ID
    assert result.name == MOCK_EVENT_NAME
    assert result.description == MOCK_EVENT_DESCRIPTION
    assert result.rsvp_ids == []


@pytest.mark.asyncio
@patch("app.service.team.db_delete_event")
@patch("app.service.team.db_get_event_by_id")
@patch("app.service.team.db_get_team_by_id")
async def test_delete_event_service_success(
    mock_db_get_team_by_id, mock_db_get_event_by_id, mock_db_delete_event
):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "event_ids": [MOCK_EVENT_ID],
    }
    mock_db_get_event_by_id.return_value = {
        "_id": MOCK_EVENT_ID,
        "name": MOCK_EVENT_NAME,
        "description": MOCK_EVENT_DESCRIPTION,
        "rsvp_ids": [],
    }
    mock_db_delete_event.return_value = None

    result = await delete_event_service(
        MOCK_TEAM_ID, MOCK_EVENT_ID, MOCK_USER_ID, mock_db
    )

    assert result is None
