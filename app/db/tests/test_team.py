from unittest.mock import AsyncMock
import pytest

from bson import ObjectId
from app.schemas.team import TeamCreateReq
from app.db.team import (
    create_team,
    join_team,
    get_team_by_name,
    get_team_by_id,
    get_team_members,
    add_kanban_to_team,
    promote_team_member,
    leave_team,
    kick_team_member,
)


@pytest.mark.asyncio
async def test_create_team_success():
    team_req = TeamCreateReq(name="addi-team")
    creator_id = "addi-creator-id"

    mock_collection = AsyncMock()
    mock_result = AsyncMock()
    mock_result.inserted_id = "some-team-id"
    mock_collection.insert_one.return_value = mock_result

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await create_team(mock_db, team_req, creator_id)

    assert result["_id"] == "some-team-id"
    assert result["name"] == "addi-team"
    assert result["member_ids"] == ["addi-creator-id"]
    assert result["exec_member_ids"] == ["addi-creator-id"]


@pytest.mark.asyncio
async def test_create_team_failure():
    team_req = TeamCreateReq(name="addi-team")
    creator_id = "addi-creator-id"

    mock_collection = AsyncMock()
    mock_collection.insert_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(Exception):
        await create_team(mock_db, team_req, creator_id)


@pytest.mark.asyncio
async def test_join_team_success():
    team_id = "507f1f77bcf86cd799439011"
    user_id = "addi-user-id"

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await join_team(mock_db, team_id, user_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)}, {"$addToSet": {"member_ids": user_id}}
    )


@pytest.mark.asyncio
async def test_join_team_failure():
    team_id = "507f1f77bcf86cd799439011"
    user_id = "addi-user-id"

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await join_team(mock_db, team_id, user_id)

    assert "Failed to add user to team" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_team_by_name_success():
    team_name = "addi-team"
    team_id = ObjectId()

    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = {
        "_id": team_id,
        "name": team_name,
        "member_ids": ["addi-id"],
        "exec_member_ids": ["addi-id"],
    }

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await get_team_by_name(mock_db, team_name)

    assert isinstance(result, dict)
    assert result["_id"] == str(team_id)
    assert result["name"] == team_name
    assert result["member_ids"] == ["addi-id"]


@pytest.mark.asyncio
async def test_get_team_by_name_failure():
    team_name = "addi-team"

    mock_collection = AsyncMock()
    mock_collection.find_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await get_team_by_name(mock_db, team_name)

    assert result is None


@pytest.mark.asyncio
async def test_get_team_by_id_success():
    team_id = "507f1f77bcf86cd799439011"
    object_id = ObjectId(team_id)

    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = {
        "_id": object_id,
        "name": "addi-team",
        "member_ids": ["addi-id"],
        "exec_member_ids": ["addi-id"],
    }

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await get_team_by_id(mock_db, team_id)

    assert isinstance(result, dict)
    assert result["_id"] == team_id
    assert result["name"] == "addi-team"
    assert result["member_ids"] == ["addi-id"]


@pytest.mark.asyncio
async def test_get_team_by_id_failure():
    team_id = "507f1f77bcf86cd799439011"

    mock_collection = AsyncMock()
    mock_collection.find_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await get_team_by_id(mock_db, team_id)

    assert result is None


@pytest.mark.asyncio
async def test_get_team_members_success():
    team_id = "507f1f77bcf86cd799439011"
    object_id = ObjectId(team_id)

    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = {
        "_id": object_id,
        "name": "addi-team",
        "member_ids": ["addi-id", "member-2-id"],
        "exec_member_ids": ["addi-id"],
    }

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await get_team_members(mock_db, team_id)

    assert result == ["addi-id", "member-2-id"]


@pytest.mark.asyncio
async def test_get_team_members_failure():
    team_id = "507f1f77bcf86cd799439011"

    mock_collection = AsyncMock()
    mock_collection.find_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await get_team_members(mock_db, team_id)

    assert result is None


@pytest.mark.asyncio
async def test_add_kanban_to_team_success():
    team_id = "507f1f77bcf86cd799439011"
    kanban_id = "addi-kanban-id"

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await add_kanban_to_team(mock_db, team_id, kanban_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)}, {"$addToSet": {"kanban_ids": kanban_id}}
    )


@pytest.mark.asyncio
async def test_add_kanban_to_team_failure():
    team_id = "507f1f77bcf86cd799439011"
    kanban_id = "addi-kanban-id"

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await add_kanban_to_team(mock_db, team_id, kanban_id)

    assert "Failed to add kanban to team" in str(exc_info.value)


@pytest.mark.asyncio
async def test_promote_team_member_success():
    team_id = "507f1f77bcf86cd799439011"
    member_id = "addi-member-id"

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await promote_team_member(mock_db, team_id, member_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)}, {"$addToSet": {"exec_member_ids": member_id}}
    )


@pytest.mark.asyncio
async def test_promote_team_member_failure():
    team_id = "507f1f77bcf86cd799439011"
    member_id = "addi-member-id"

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await promote_team_member(mock_db, team_id, member_id)

    assert "Failed to promote team member" in str(exc_info.value)


@pytest.mark.asyncio
async def test_leave_team_success():
    team_id = "507f1f77bcf86cd799439011"
    user_id = "addi-user-id"

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await leave_team(mock_db, team_id, user_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)},
        {"$pull": {"member_ids": user_id, "exec_member_ids": user_id}},
    )


@pytest.mark.asyncio
async def test_leave_team_failure():
    team_id = "507f1f77bcf86cd799439011"
    user_id = "addi-user-id"

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await leave_team(mock_db, team_id, user_id)

    assert "Failed to remove user from team" in str(exc_info.value)


@pytest.mark.asyncio
async def test_kick_team_member_success():
    team_id = "507f1f77bcf86cd799439011"
    kick_member_id = "member-to-kick-id"
    caller_id = "addi-caller-id"

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await kick_team_member(mock_db, team_id, kick_member_id, caller_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)}, {"$pull": {"member_ids": kick_member_id}}
    )


@pytest.mark.asyncio
async def test_kick_team_member_failure():
    team_id = "507f1f77bcf86cd799439011"
    kick_member_id = "member-to-kick-id"
    caller_id = "addi-caller-id"

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await kick_team_member(mock_db, team_id, kick_member_id, caller_id)

    assert "Failed to remove user from team" in str(exc_info.value)
