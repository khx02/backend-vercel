from unittest.mock import AsyncMock, patch

from bson import ObjectId
import pytest
from fastapi import HTTPException

from app.api.team import (
    create_team,
    join_team,
    kick_team_member,
    leave_team,
    promote_team_member,
)
from app.schemas.team import (
    CreateTeamRequest,
    CreateTeamResponse,
    JoinTeamResponse,
    KickTeamMemberRequest,
    KickTeamMemberResponse,
    LeaveTeamResponse,
    PromoteTeamMemberRequest,
    PromoteTeamMemberResponse,
    TeamModel,
)
from app.schemas.user import UserModel

MOCK_USER_ID = str(ObjectId())
MOCK_USER_EMAIL = "addi@addi.com"
MOCK_USER_PASSWORD = "addiii"
MOCK_USER_PASSWORD_HASHED = "hashed-addiii"

MOCK_USER_2_ID = str(ObjectId())

MOCK_TEAM_NAME = "Mock Team"
MOCK_TEAM_ID = str(ObjectId())


@pytest.mark.asyncio
@patch("app.api.team.create_team_service")
async def test_create_team_success(mock_create_team_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
        hashed_password=MOCK_USER_PASSWORD_HASHED,
    )
    mock_create_team_service.return_value = CreateTeamResponse(
        team=TeamModel(
            id="team-1",
            name=MOCK_TEAM_NAME,
            member_ids=[MOCK_USER_ID],
            exec_member_ids=[MOCK_USER_ID],
            project_ids=[],
        )
    )
    create_team_request = CreateTeamRequest(name=MOCK_TEAM_NAME)

    result = await create_team(create_team_request, mock_current_user, mock_db)

    assert isinstance(result, CreateTeamResponse)
    assert isinstance(result.team, TeamModel)
    assert result.team.id == "team-1"
    assert result.team.name == MOCK_TEAM_NAME
    assert result.team.member_ids == [MOCK_USER_ID]
    assert result.team.exec_member_ids == [MOCK_USER_ID]
    assert result.team.project_ids == []


@pytest.mark.asyncio
@patch("app.api.team.join_team_service")
async def test_join_team_success(mock_join_team_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
        hashed_password=MOCK_USER_PASSWORD_HASHED,
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
        hashed_password=MOCK_USER_PASSWORD_HASHED,
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
        hashed_password=MOCK_USER_PASSWORD_HASHED,
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
        hashed_password=MOCK_USER_PASSWORD_HASHED,
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
        hashed_password=MOCK_USER_PASSWORD_HASHED,
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
        hashed_password=MOCK_USER_PASSWORD_HASHED,
    )
    mock_leave_team_service.side_effect = HTTPException(
        status_code=404, detail=f"Team does not exist: team_id={MOCK_TEAM_ID}"
    )

    with pytest.raises(HTTPException) as exc_info:
        await leave_team(MOCK_TEAM_ID, mock_current_user, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Team does not exist: team_id={MOCK_TEAM_ID}"


@pytest.mark.asyncio
@patch("app.api.team.kick_team_member_service")
async def test_kick_team_member_success(mock_kick_team_member_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
        hashed_password=MOCK_USER_PASSWORD_HASHED,
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
        hashed_password=MOCK_USER_PASSWORD_HASHED,
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
