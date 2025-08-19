from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status

from app.api.team import (create_team, join_team, kick_team_member, leave_team,
                          promote_team_member)
from app.schemas.team import (KickTeamMemberReq, PromoteTeamMemberReq,
                              TeamCreateReq, TeamModel)
from app.schemas.user import UserModel


@pytest.mark.asyncio
@patch("app.api.team.create_team_service")
async def test_create_team_success(mock_create_team_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    mock_team_name = "Test Team"
    team_create_req = TeamCreateReq(name=mock_team_name)

    mock_create_team_service.return_value = TeamModel(
        id="team-1",
        name=mock_team_name,
        member_ids=[user_id],
        exec_member_ids=[user_id],
        kanban_ids=[],
    )

    result = await create_team(team_create_req, mock_current_user, mock_db)

    assert result.id == "team-1"
    assert result.name == mock_team_name
    assert result.member_ids == [user_id]
    assert result.exec_member_ids == [user_id]
    assert result.kanban_ids == []


@pytest.mark.asyncio
@patch("app.api.team.create_team_service")
async def test_create_team_failure(mock_create_team_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    mock_team_name = "Test Team"
    team_create_req = TeamCreateReq(name=mock_team_name)

    mock_create_team_service.side_effect = ValueError("Invalid team data")

    with pytest.raises(HTTPException) as exc_info:
        await create_team(team_create_req, mock_current_user, mock_db)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid team data"


@pytest.mark.asyncio
@patch("app.api.team.join_team_service")
async def test_join_team_success(mock_join_team_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    team_id = "team-1"
    mock_join_team_service.return_value = None

    result = await join_team(team_id, mock_current_user, mock_db)

    assert result is None
    mock_join_team_service.assert_called_once_with(mock_db, team_id, user_id)


@pytest.mark.asyncio
@patch("app.api.team.join_team_service")
async def test_join_team_failure(mock_join_team_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    team_id = "team-1"
    mock_join_team_service.side_effect = ValueError("Team not found")

    with pytest.raises(HTTPException) as exc_info:
        await join_team(team_id, mock_current_user, mock_db)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Team not found"


@pytest.mark.asyncio
@patch("app.api.team.promote_team_member_service")
async def test_promote_team_member_success(mock_promote_team_member_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    team_id = "team-1"
    member_id = "user-2"
    promote_req = PromoteTeamMemberReq(member_id=member_id)
    mock_promote_team_member_service.return_value = None

    result = await promote_team_member(team_id, promote_req, mock_current_user, mock_db)

    assert result is None
    mock_promote_team_member_service.assert_called_once_with(
        mock_db, team_id, member_id, user_id
    )


@pytest.mark.asyncio
@patch("app.api.team.promote_team_member_service")
async def test_promote_team_member_failure(mock_promote_team_member_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    team_id = "team-1"
    member_id = "user-2"
    promote_req = PromoteTeamMemberReq(member_id=member_id)
    mock_promote_team_member_service.side_effect = ValueError("Permission denied")

    with pytest.raises(HTTPException) as exc_info:
        await promote_team_member(team_id, promote_req, mock_current_user, mock_db)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Permission denied"


@pytest.mark.asyncio
@patch("app.api.team.leave_team_service")
async def test_leave_team_success(mock_leave_team_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    team_id = "team-1"
    mock_leave_team_service.return_value = None

    result = await leave_team(team_id, mock_current_user, mock_db)

    assert result is None
    mock_leave_team_service.assert_called_once_with(mock_db, team_id, user_id)


@pytest.mark.asyncio
@patch("app.api.team.leave_team_service")
async def test_leave_team_failure(mock_leave_team_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    team_id = "team-1"
    mock_leave_team_service.side_effect = ValueError("Cannot leave team")

    with pytest.raises(HTTPException) as exc_info:
        await leave_team(team_id, mock_current_user, mock_db)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Cannot leave team"


@pytest.mark.asyncio
@patch("app.api.team.kick_team_member_service")
async def test_kick_team_member_success(mock_kick_team_member_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    team_id = "team-1"
    member_id = "user-2"
    kick_req = KickTeamMemberReq(member_id=member_id)
    mock_kick_team_member_service.return_value = None

    result = await kick_team_member(team_id, kick_req, mock_current_user, mock_db)

    assert result is None
    mock_kick_team_member_service.assert_called_once_with(
        mock_db, team_id, member_id, user_id
    )


@pytest.mark.asyncio
@patch("app.api.team.kick_team_member_service")
async def test_kick_team_member_failure(mock_kick_team_member_service):
    mock_db = AsyncMock()

    user_id = "user-1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-alex's"
    )

    team_id = "team-1"
    member_id = "user-2"
    kick_req = KickTeamMemberReq(member_id=member_id)
    mock_kick_team_member_service.side_effect = ValueError("Permission denied")

    with pytest.raises(HTTPException) as exc_info:
        await kick_team_member(team_id, kick_req, mock_current_user, mock_db)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Permission denied"
