from re import A
from unittest.mock import AsyncMock, patch

from bson import ObjectId
from fastapi import HTTPException
import pytest

from app.schemas.team import (
    CreateTeamResponse,
    JoinTeamResponse,
    KickTeamMemberResponse,
    LeaveTeamResponse,
    PromoteTeamMemberResponse,
    TeamModel,
)
from app.service.team import (
    create_team_service,
    join_team_service,
    kick_team_member_service,
    leave_team_service,
    promote_team_member_service,
)

MOCK_USER_ID = str(ObjectId())
MOCK_USER_EMAIL = "addi@addi.com"
MOCK_USER_PASSWORD = "addiii"
MOCK_USER_PASSWORD_HASHED = "hashed-addiii"

MOCK_USER_2_ID = str(ObjectId())

MOCK_TEAM_NAME = "Mock Team"
MOCK_TEAM_ID = str(ObjectId())


@pytest.mark.asyncio
@patch("app.service.team.db_create_team")
async def test_create_team_service_success(mock_db_create_team):
    mock_db = AsyncMock()
    mock_db_create_team.return_value = {
        "_id": "team-1",
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "project_ids": [],
    }

    result = await create_team_service(MOCK_USER_ID, MOCK_TEAM_NAME, mock_db)

    assert isinstance(result, CreateTeamResponse)
    assert isinstance(result.team, TeamModel)
    assert result.team.id == "team-1"
    assert result.team.name == MOCK_TEAM_NAME
    assert result.team.member_ids == [MOCK_USER_ID]
    assert result.team.exec_member_ids == [MOCK_USER_ID]
    assert result.team.project_ids == []


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
    }
    mock_db_leave_team.return_value = None

    result = await leave_team_service(MOCK_TEAM_ID, MOCK_USER_ID, mock_db)

    assert isinstance(result, LeaveTeamResponse)


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
async def test_leave_team_service_failure_last_exec(mock_db_get_team_by_id):
    mock_db = AsyncMock()
    mock_db_get_team_by_id.return_value = {
        "_id": MOCK_TEAM_ID,
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
    }

    with pytest.raises(HTTPException) as exc_info:
        await leave_team_service(MOCK_TEAM_ID, MOCK_USER_ID, mock_db)

    assert exc_info.value.status_code == 403
    assert (
        exc_info.value.detail
        == f"User is the last executive member and cannot leave the team: user_id={MOCK_USER_ID}, team_id={MOCK_TEAM_ID}"
    )


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
