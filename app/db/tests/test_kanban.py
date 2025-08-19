from unittest.mock import AsyncMock
import pytest

from bson import ObjectId
from app.schemas.kanban import KanbanCreateReq
from app.db.kanban import (
    create_kanban,
    add_kanban_item,
    remove_kanban_item,
)


@pytest.mark.asyncio
async def test_create_kanban_success():
    kanban_req = KanbanCreateReq(name="addi-kanban", team_id="addi-team-id")

    mock_collection = AsyncMock()
    mock_result = AsyncMock()
    mock_result.inserted_id = "some-kanban-id"
    mock_collection.insert_one.return_value = mock_result

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await create_kanban(mock_db, kanban_req)

    assert isinstance(result, dict)
    assert result["_id"] == "some-kanban-id"
    assert result["name"] == "addi-kanban"


@pytest.mark.asyncio
async def test_create_kanban_failure():
    kanban_req = KanbanCreateReq(name="addi-kanban", team_id="addi-team-id")

    mock_collection = AsyncMock()
    mock_collection.insert_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(Exception):
        await create_kanban(mock_db, kanban_req)


@pytest.mark.asyncio
async def test_add_kanban_item_success():
    kanban_id = "507f1f77bcf86cd799439011"
    kanban_item = {
        "name": "addi-task",
        "start_at": 1234567890.0,
        "end_at": 1234567891.0,
        "column": 1,
        "owner": "addi@addi.com",
    }

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await add_kanban_item(mock_db, kanban_id, kanban_item)

    mock_collection.update_one.assert_called_once()
    assert isinstance(result, dict)
    assert "_id" in result
    assert result["name"] == "addi-task"
    assert result["owner"] == "addi@addi.com"


@pytest.mark.asyncio
async def test_add_kanban_item_failure():
    kanban_id = "507f1f77bcf86cd799439011"
    kanban_item = {
        "name": "addi-task",
        "start_at": 1234567890.0,
        "end_at": 1234567891.0,
        "column": 1,
        "owner": "addi@addi.com",
    }

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(Exception):
        await add_kanban_item(mock_db, kanban_id, kanban_item)


@pytest.mark.asyncio
async def test_remove_kanban_item_success():
    kanban_id = "507f1f77bcf86cd799439011"
    item_id = "507f1f77bcf86cd799439012"

    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    await remove_kanban_item(mock_db, kanban_id, item_id)

    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(kanban_id)}, {"$pull": {"items": {"_id": ObjectId(item_id)}}}
    )


@pytest.mark.asyncio
async def test_remove_kanban_item_failure():
    kanban_id = "507f1f77bcf86cd799439011"
    item_id = "507f1f77bcf86cd799439012"

    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(Exception):
        await remove_kanban_item(mock_db, kanban_id, item_id)
