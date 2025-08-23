from unittest.mock import AsyncMock

import pytest
from bson import ObjectId

from app.db.team import (
    add_kanban_to_team,
    create_team,
    db_create_project,
    get_team_by_id,
    join_team,
    kick_team_member,
    leave_team,
    promote_team_member,
)

from app.schemas.team import CreateProjectRequest, TeamCreateReq


@pytest.mark.asyncio
async def test_create_team_success():
    team_req = TeamCreateReq(name="addi-team")
    creator_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_result = AsyncMock()
    mock_result.inserted_id = ObjectId()
    mock_collection.insert_one.return_value = mock_result

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await create_team(mock_db, team_req, creator_id)

    assert result["_id"] == str(mock_result.inserted_id)
    assert result["name"] == team_req.name
    assert result["member_ids"] == [creator_id]
    assert result["exec_member_ids"] == [creator_id]


@pytest.mark.asyncio
async def test_create_team_failure():
    team_req = TeamCreateReq(name="addi-team")
    creator_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_collection.insert_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(Exception):
        await create_team(mock_db, team_req, creator_id)


@pytest.mark.asyncio
async def test_join_team_success():
    team_id = str(ObjectId())
    user_id = str(ObjectId())
    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await join_team(mock_db, team_id, user_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)}, {"$addToSet": {"member_ids": ObjectId(user_id)}}
    )


@pytest.mark.asyncio
async def test_join_team_failure():
    team_id = str(ObjectId())
    user_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await join_team(mock_db, team_id, user_id)

    assert "Failed to add user to team" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_team_by_id_success():
    team_id = str(ObjectId())
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
    team_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_collection.find_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await get_team_by_id(mock_db, team_id)

    assert result is None


@pytest.mark.asyncio
async def test_add_kanban_to_team_success():
    team_id = str(ObjectId())
    kanban_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await add_kanban_to_team(mock_db, team_id, kanban_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)}, {"$addToSet": {"kanban_ids": ObjectId(kanban_id)}}
    )


@pytest.mark.asyncio
async def test_add_kanban_to_team_failure():
    team_id = str(ObjectId())
    kanban_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await add_kanban_to_team(mock_db, team_id, kanban_id)

    assert "Failed to add kanban to team" in str(exc_info.value)


@pytest.mark.asyncio
async def test_promote_team_member_success():
    team_id = str(ObjectId())
    member_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await promote_team_member(mock_db, team_id, member_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)},
        {"$addToSet": {"exec_member_ids": ObjectId(member_id)}},
    )


@pytest.mark.asyncio
async def test_promote_team_member_failure():
    team_id = str(ObjectId())
    member_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await promote_team_member(mock_db, team_id, member_id)

    assert "Failed to promote team member" in str(exc_info.value)


@pytest.mark.asyncio
async def test_leave_team_success():
    team_id = str(ObjectId())
    user_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await leave_team(mock_db, team_id, user_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)},
        {
            "$pull": {
                "member_ids": ObjectId(user_id),
                "exec_member_ids": ObjectId(user_id),
            }
        },
    )


@pytest.mark.asyncio
async def test_leave_team_failure():
    team_id = str(ObjectId())
    user_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await leave_team(mock_db, team_id, user_id)

    assert "Failed to remove user from team" in str(exc_info.value)


@pytest.mark.asyncio
async def test_kick_team_member_success():
    team_id = str(ObjectId())
    kick_member_id = str(ObjectId())
    caller_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await kick_team_member(mock_db, team_id, kick_member_id, caller_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(team_id)}, {"$pull": {"member_ids": ObjectId(kick_member_id)}}
    )


@pytest.mark.asyncio
async def test_kick_team_member_failure():
    team_id = str(ObjectId())
    kick_member_id = str(ObjectId())
    caller_id = str(ObjectId())

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await kick_team_member(mock_db, team_id, kick_member_id, caller_id)

    assert "Failed to remove user from team" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_project_success():
    team_id = str(ObjectId())
    create_project_request = CreateProjectRequest(
        name="Test Project",
        description="A project for testing",
    )

    mock_collection = AsyncMock()
    mock_collection.insert_one.return_value = AsyncMock(inserted_id=ObjectId())
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await db_create_project(team_id, create_project_request, mock_db)

    assert result["name"] == create_project_request.name
    assert result["description"] == create_project_request.description
    assert len(result["todo_statuses"]) == 3
    assert all(
        "id" in status and "name" in status for status in result["todo_statuses"]
    )
