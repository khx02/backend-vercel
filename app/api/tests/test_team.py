from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.team import (
    create_event,
    create_team,
    delete_event,
    delete_project,
    delete_team,
    get_team_events,
    join_team,
    kick_team_member,
    leave_team,
    promote_team_member,
)
from app.schemas.event import Event
from app.schemas.team import (
    CreateEventRequest,
    CreateEventResponse,
    CreateTeamRequest,
    CreateTeamResponse,
    DeleteEventRequest,
    DeleteEventResponse,
    DeleteProjectRequest,
    DeleteProjectResponse,
    DeleteTeamResponse,
    GetTeamEventsResponse,
    JoinTeamResponse,
    KickTeamMemberRequest,
    KickTeamMemberResponse,
    LeaveTeamResponse,
    PromoteTeamMemberRequest,
    PromoteTeamMemberResponse,
    TeamModel,
)
from app.schemas.user import UserModel

from app.service.team import delete_team_service
from app.test_shared.constants import (
    MOCK_EVENT_COLOUR,
    MOCK_EVENT_DESCRIPTION,
    MOCK_EVENT_END,
    MOCK_EVENT_ID,
    MOCK_EVENT_LOCATION,
    MOCK_EVENT_NAME,
    MOCK_EVENT_START,
    MOCK_PROJECT_ID,
    MOCK_TEAM_SHORT_ID,
    MOCK_USER_ID,
    MOCK_USER_EMAIL,
    MOCK_USER_2_ID,
    MOCK_TEAM_NAME,
    MOCK_TEAM_ID,
)


@pytest.mark.asyncio
@patch("app.api.team.create_team_service")
async def test_create_team_success(mock_create_team_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_create_team_service.return_value = CreateTeamResponse(
        team=TeamModel(
            id=MOCK_TEAM_ID,
            short_id=MOCK_TEAM_SHORT_ID,
            name=MOCK_TEAM_NAME,
            member_ids=[MOCK_USER_ID],
            exec_member_ids=[MOCK_USER_ID],
            project_ids=[],
            event_ids=[],
        )
    )
    create_team_request = CreateTeamRequest(name=MOCK_TEAM_NAME)

    result = await create_team(create_team_request, mock_current_user, mock_db)

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
@patch("app.api.team.join_team_service")
async def test_join_team_success(mock_join_team_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_join_team_service.return_value = JoinTeamResponse()

    result = await join_team(MOCK_TEAM_ID, mock_current_user, mock_db)

    assert isinstance(result, JoinTeamResponse)


@pytest.mark.asyncio
@patch("app.api.team.join_team_service")
async def test_join_team_failure(mock_join_team_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_join_team_service.side_effect = HTTPException(
        status_code=404,
        detail=f"Team does not exist: team_id={MOCK_TEAM_ID}",
    )

    with pytest.raises(HTTPException) as exc_info:
        await join_team(MOCK_TEAM_ID, mock_current_user, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Team does not exist: team_id={MOCK_TEAM_ID}"


@pytest.mark.asyncio
@patch("app.api.team.promote_team_member_service")
async def test_promote_team_member_success(mock_promote_team_member_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_promote_team_member_service.return_value = PromoteTeamMemberResponse()
    promote_team_member_request = PromoteTeamMemberRequest(member_id=MOCK_USER_2_ID)

    result = await promote_team_member(
        MOCK_TEAM_ID, promote_team_member_request, mock_current_user, mock_db
    )

    assert isinstance(result, PromoteTeamMemberResponse)


@pytest.mark.asyncio
@patch("app.api.team.promote_team_member_service")
async def test_promote_team_member_failure(mock_promote_team_member_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_promote_team_member_service.side_effect = HTTPException(
        status_code=404,
        detail=f"Team does not exist: team_id={MOCK_TEAM_ID}",
    )
    promote_team_member_request = PromoteTeamMemberRequest(member_id=MOCK_USER_2_ID)

    with pytest.raises(HTTPException) as exc_info:
        await promote_team_member(
            MOCK_TEAM_ID, promote_team_member_request, mock_current_user, mock_db
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Team does not exist: team_id={MOCK_TEAM_ID}"


@pytest.mark.asyncio
@patch("app.api.team.leave_team_service")
async def test_leave_team_success(mock_leave_team_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_leave_team_service.return_value = LeaveTeamResponse()

    result = await leave_team(MOCK_TEAM_ID, mock_current_user, mock_db)

    assert isinstance(result, LeaveTeamResponse)


@pytest.mark.asyncio
@patch("app.api.team.leave_team_service")
async def test_leave_team_failure(mock_leave_team_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_leave_team_service.side_effect = HTTPException(
        status_code=404, detail=f"Team does not exist: team_id={MOCK_TEAM_ID}"
    )

    with pytest.raises(HTTPException) as exc_info:
        await leave_team(MOCK_TEAM_ID, mock_current_user, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Team does not exist: team_id={MOCK_TEAM_ID}"


@pytest.mark.asyncio
@patch("app.api.team.delete_team_service")
async def test_delete_team_success(mock_delete_team_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_delete_team_service.return_value = DeleteTeamResponse()

    result = await delete_team(MOCK_TEAM_ID, mock_current_user, mock_db)

    assert isinstance(result, DeleteTeamResponse)


@pytest.mark.asyncio
@patch("app.api.team.kick_team_member_service")
async def test_kick_team_member_success(mock_kick_team_member_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    kick_team_member_request = KickTeamMemberRequest(member_id=MOCK_USER_2_ID)
    mock_kick_team_member_service.return_value = KickTeamMemberResponse()

    result = await kick_team_member(
        MOCK_TEAM_ID, kick_team_member_request, mock_current_user, mock_db
    )

    assert isinstance(result, KickTeamMemberResponse)


@pytest.mark.asyncio
@patch("app.api.team.kick_team_member_service")
async def test_kick_team_member_failure(mock_kick_team_member_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    kick_team_member_request = KickTeamMemberRequest(member_id=MOCK_USER_2_ID)
    mock_kick_team_member_service.side_effect = HTTPException(
        status_code=404, detail=f"Team does not exist: team_id={MOCK_TEAM_ID}"
    )

    with pytest.raises(HTTPException) as exc_info:
        await kick_team_member(
            MOCK_TEAM_ID, kick_team_member_request, mock_current_user, mock_db
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Team does not exist: team_id={MOCK_TEAM_ID}"


@pytest.mark.asyncio
@patch("app.api.team.delete_project_service")
async def test_delete_project_success(mock_delete_project_service):
    mock_db = AsyncMock()
    mock_delete_project_service.return_value = None
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_delete_project_request = DeleteProjectRequest(project_id=MOCK_PROJECT_ID)

    result = await delete_project(
        MOCK_TEAM_ID, mock_delete_project_request, mock_current_user, mock_db
    )

    assert isinstance(result, DeleteProjectResponse)


@pytest.mark.asyncio
@patch("app.api.team.create_event_for_team_service")
async def test_create_event_success(mock_create_event_for_team_service):
    mock_db = AsyncMock()
    mock_create_event_for_team_service.return_value = Event(
        id=MOCK_EVENT_ID,
        name=MOCK_EVENT_NAME,
        description=MOCK_EVENT_DESCRIPTION,
        start=MOCK_EVENT_START,
        end=MOCK_EVENT_END,
        colour=MOCK_EVENT_COLOUR,
        location=MOCK_EVENT_LOCATION,
        rsvp_ids=[],
    )

    mock_create_event_request = CreateEventRequest(
        name=MOCK_EVENT_NAME,
        description=MOCK_EVENT_DESCRIPTION,
        start=MOCK_EVENT_START,
        end=MOCK_EVENT_END,
        colour=MOCK_EVENT_COLOUR,
        location=MOCK_EVENT_LOCATION,
    )

    result = await create_event(MOCK_TEAM_ID, mock_create_event_request, mock_db)

    assert isinstance(result, CreateEventResponse)
    assert result.event.id == MOCK_EVENT_ID
    assert result.event.name == MOCK_EVENT_NAME
    assert result.event.description == MOCK_EVENT_DESCRIPTION
    assert result.event.rsvp_ids == []


@pytest.mark.asyncio
@patch("app.api.team.delete_event_service")
async def test_delete_event_success(mock_delete_event_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_delete_event_service.return_value = None
    mock_delete_event_request = DeleteEventRequest(event_id=MOCK_EVENT_ID)

    result = await delete_event(
        MOCK_TEAM_ID, mock_delete_event_request, mock_current_user, mock_db
    )

    assert isinstance(result, DeleteEventResponse)


@pytest.mark.asyncio
@patch("app.api.team.get_team_events_service")
async def test_get_team_events_success(mock_get_team_events_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_get_team_events_service.return_value = [
        Event(
            id=MOCK_EVENT_ID,
            name=MOCK_EVENT_NAME,
            description=MOCK_EVENT_DESCRIPTION,
            start=MOCK_EVENT_START,
            end=MOCK_EVENT_END,
            colour=MOCK_EVENT_COLOUR,
            location=MOCK_EVENT_LOCATION,
            rsvp_ids=[],
        )
    ]

    result = await get_team_events(MOCK_TEAM_ID, mock_current_user, mock_db)

    assert isinstance(result, GetTeamEventsResponse)
    assert len(result.events) == 1
    assert result.events[0].id == MOCK_EVENT_ID
    assert result.events[0].name == MOCK_EVENT_NAME
    assert result.events[0].description == MOCK_EVENT_DESCRIPTION
    assert result.events[0].rsvp_ids == []
