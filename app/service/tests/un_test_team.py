from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.team import TeamModel
from app.service.team import (
    create_team_service,
    join_team_service,
    kick_team_member_service,
    leave_team_service,
    promote_team_member_service,
)


@pytest.mark.asyncio
@patch("app.service.team.db_create_team")
async def test_create_team_service_success(mock_db_create_team):
    team_id = "1"
    team_name = "addi's team"
    creator_id = "alex's_id"
    team_create_req = TeamCreateReq(name=team_name)

    mock_db = AsyncMock()

    mock_db_create_team.return_value = {
        "_id": team_id,
        "name": team_name,
        "member_ids": [creator_id],
        "exec_member_ids": [creator_id],
        "project_ids": [],
    }

    result = await create_team_service(mock_db, team_create_req, creator_id)

    assert result.id == team_id
    assert result.name == team_name
    assert result.member_ids == [creator_id]
    assert result.exec_member_ids == [creator_id]
    assert result.project_ids == []


@pytest.mark.asyncio
@patch("app.service.team.db_join_team")
@patch("app.service.team.db_get_team_by_id")
async def test_join_team_service_success(mock_db_get_team_by_id, mock_db_join_team):
    team_id = "1"
    user_id = "addi@addi.com"

    mock_db = AsyncMock()

    mock_db_get_team_by_id.return_value = {
        "_id": team_id,
        "name": "alex's team",
        "member_ids": ["alex's_id"],
        "exec_member_ids": ["alex's_id"],
    }
    mock_db_join_team.return_value = None

    await join_team_service(mock_db, team_id, user_id)

    mock_db_join_team.assert_called_once_with(mock_db, team_id, user_id)


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
async def test_join_team_service_failure_team_not_exist(mock_db_get_team_by_id):
    team_id = "1"
    user_id = "addi@addi.com"

    mock_db = AsyncMock()

    mock_db_get_team_by_id.return_value = None

    with pytest.raises(ValueError) as exc_info:
        await join_team_service(mock_db, team_id, user_id)

    assert str(exc_info.value) == f"Team with ID '{team_id}' does not exist"


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
async def test_join_team_service_failure_user_already_in_team(mock_db_get_team_by_id):
    team_id = "1"
    user_id = "addi@addi.com"

    mock_db = AsyncMock()

    mock_db_get_team_by_id.return_value = {
        "_id": team_id,
        "name": "alex's team",
        "member_ids": [user_id, "alex's_id"],
        "exec_member_ids": ["alex's_id"],
    }

    with pytest.raises(ValueError) as exc_info:
        await join_team_service(mock_db, team_id, user_id)

    assert (
        str(exc_info.value)
        == f"User with ID '{user_id}' is already in team '{team_id}'"
    )


@pytest.mark.asyncio
@patch("app.service.team.db_promote_team_member")
@patch("app.service.team.db_get_team_by_id")
async def test_promote_team_member_service_success(
    mock_db_get_team_by_id, mock_db_promote_team_member
):
    team_id = "1"
    promote_member_id = "addi@addi.com"
    caller_id = "alex's_id"

    mock_db = AsyncMock()

    mock_db_get_team_by_id.return_value = {
        "_id": team_id,
        "name": "alex's team",
        "member_ids": [caller_id, promote_member_id],
        "exec_member_ids": [caller_id],
    }
    mock_db_promote_team_member.return_value = None

    await promote_team_member_service(mock_db, team_id, promote_member_id, caller_id)

    mock_db_promote_team_member.assert_called_once_with(
        mock_db, team_id, promote_member_id
    )


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
async def test_promote_team_member_service_failure_no_permission(
    mock_db_get_team_by_id,
):
    team_id = "1"
    promote_member_id = "addi@addi.com"
    caller_id = "alex's_id"

    mock_db = AsyncMock()

    mock_db_get_team_by_id.return_value = {
        "_id": team_id,
        "name": "alex's team",
        "member_ids": [caller_id, promote_member_id],
        "exec_member_ids": ["other_exec"],
    }

    with pytest.raises(ValueError) as exc_info:
        await promote_team_member_service(
            mock_db, team_id, promote_member_id, caller_id
        )

    assert (
        str(exc_info.value)
        == f"User with ID '{caller_id}' does not have permission to promote members in team '{team_id}'"
    )


@pytest.mark.asyncio
@patch("app.service.team.db_leave_team")
@patch("app.service.team.db_get_team_by_id")
async def test_leave_team_service_success(mock_db_get_team_by_id, mock_db_leave_team):
    team_id = "1"
    user_id = "addi@addi.com"

    mock_db = AsyncMock()

    mock_db_get_team_by_id.return_value = {
        "_id": team_id,
        "name": "alex's team",
        "member_ids": ["alex's_id", user_id],
        "exec_member_ids": ["alex's_id"],
    }
    mock_db_leave_team.return_value = None

    await leave_team_service(mock_db, team_id, user_id)

    mock_db_leave_team.assert_called_once_with(mock_db, team_id, user_id)


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
async def test_leave_team_service_failure_last_exec(mock_db_get_team_by_id):
    team_id = "1"
    user_id = "alex's_id"

    mock_db = AsyncMock()

    mock_db_get_team_by_id.return_value = {
        "_id": team_id,
        "name": "alex's team",
        "member_ids": [user_id],
        "exec_member_ids": [user_id],
    }

    with pytest.raises(ValueError) as exc_info:
        await leave_team_service(mock_db, team_id, user_id)

    assert (
        str(exc_info.value)
        == f"User with ID '{user_id}' is the last executive member and cannot leave the team '{team_id}'"
    )


@pytest.mark.asyncio
@patch("app.service.team.db_kick_team_member")
@patch("app.service.team.db_get_team_by_id")
async def test_kick_team_member_service_success(
    mock_db_get_team_by_id, mock_db_kick_team_member
):
    team_id = "1"
    kick_member_id = "addi@addi.com"
    caller_id = "alex's_id"

    mock_db = AsyncMock()

    mock_db_get_team_by_id.return_value = {
        "_id": team_id,
        "name": "alex's team",
        "member_ids": [caller_id, kick_member_id],
        "exec_member_ids": [caller_id],
    }
    mock_db_kick_team_member.return_value = None

    await kick_team_member_service(mock_db, team_id, kick_member_id, caller_id)

    mock_db_kick_team_member.assert_called_once_with(
        mock_db, team_id, kick_member_id, caller_id
    )


@pytest.mark.asyncio
@patch("app.service.team.db_get_team_by_id")
async def test_kick_team_member_service_failure_kick_exec(mock_db_get_team_by_id):
    team_id = "1"
    kick_member_id = "addi@addi.com"
    caller_id = "alex's_id"

    mock_db = AsyncMock()

    mock_db_get_team_by_id.return_value = {
        "_id": team_id,
        "name": "alex's team",
        "member_ids": [caller_id, kick_member_id],
        "exec_member_ids": [caller_id, kick_member_id],
    }

    with pytest.raises(ValueError) as exc_info:
        await kick_team_member_service(mock_db, team_id, kick_member_id, caller_id)

    assert (
        str(exc_info.value)
        == f"Member with ID '{kick_member_id}' is an executive and cannot be kicked"
    )
