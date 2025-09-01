from unittest.mock import AsyncMock, MagicMock
import pytest
from bson import ObjectId

from app.db.project import (
    db_get_project,
    db_add_todo,
    db_update_todo,
    db_delete_todo,
    db_get_todo_items,
    db_add_todo_status,
    db_delete_todo_status,
    db_reorder_todo_statuses,
)
from app.schemas.project import AddTodoRequest, UpdateTodoRequest


@pytest.mark.asyncio
async def test_db_get_project_success():
    project_id = "507f1f77bcf86cd799439011"
    object_id = ObjectId(project_id)
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = {
        "_id": object_id,
        "name": "Test Project",
        "description": "Desc",
        "todo_statuses": [
            {"id": ObjectId(), "name": "To Do"},
            {"id": ObjectId(), "name": "Done"},
        ],
        "todo_ids": [],
    }
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await db_get_project(project_id, mock_db)

    assert result["_id"] == project_id
    assert result["name"] == "Test Project"
    assert isinstance(result["todo_statuses"], list)


@pytest.mark.asyncio
async def test_db_add_todo_success():
    project_id = "507f1f77bcf86cd799439011"
    todo_req = AddTodoRequest(
        name="Todo",
        description="Desc",
        status_id="507f1f77bcf86cd799439012",
        owner_id="507f1f77bcf86cd799439013",
    )
    mock_todos_collection = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_result = AsyncMock()
    mock_result.inserted_id = ObjectId()
    mock_todos_collection.insert_one.return_value = mock_result
    mock_projects_collection.update_one.return_value = None
    mock_db = AsyncMock()

    def getitem(name):
        if name == "todos":
            return mock_todos_collection
        return mock_projects_collection

    mock_db.__getitem__.side_effect = getitem

    await db_add_todo(project_id, todo_req, mock_db)
    mock_todos_collection.insert_one.assert_called_once()
    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_update_todo_success():
    project_id = "507f1f77bcf86cd799439011"
    update_req = UpdateTodoRequest(
        todo_id="507f1f77bcf86cd799439014",
        name="Updated",
        description="Desc",
        status_id="507f1f77bcf86cd799439012",
        owner_id="507f1f77bcf86cd799439013",
    )
    mock_todos_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_todos_collection

    await db_update_todo(project_id, update_req, mock_db)

    mock_todos_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_delete_todo_success():
    project_id = "507f1f77bcf86cd799439011"
    todo_id = "507f1f77bcf86cd799439014"
    mock_todos_collection = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_todos_collection.delete_one.return_value = None
    mock_projects_collection.update_one.return_value = None
    mock_db = AsyncMock()

    def getitem(name):
        if name == "todos":
            return mock_todos_collection
        return mock_projects_collection

    mock_db.__getitem__.side_effect = getitem

    await db_delete_todo(project_id, todo_id, mock_db)

    mock_todos_collection.delete_one.assert_called_once()
    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_get_todo_items_success():
    project_id = "507f1f77bcf86cd799439011"
    object_id = ObjectId(project_id)
    todo_id = "507f1f77bcf86cd799439014"
    mock_projects_collection = AsyncMock()
    mock_projects_collection.find_one.return_value = {
        "_id": object_id,
        "todo_ids": [ObjectId(todo_id)],
    }
    mock_todos_collection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(
        return_value=[
            {
                "_id": ObjectId(todo_id),
                "name": "Todo",
                "description": "Desc",
                "status_id": ObjectId("507f1f77bcf86cd799439012"),
                "owner_id": ObjectId("507f1f77bcf86cd799439013"),
            }
        ]
    )
    mock_todos_collection.find.return_value = mock_cursor
    mock_db = AsyncMock()

    def getitem(name):
        if name == "projects":
            return mock_projects_collection
        return mock_todos_collection

    mock_db.__getitem__.side_effect = getitem
    result = await db_get_todo_items(project_id, mock_db)
    assert isinstance(result, list)
    assert result[0]["_id"] == todo_id


@pytest.mark.asyncio
async def test_db_add_todo_status_success():
    project_id = "507f1f77bcf86cd799439011"
    name = "In Progress"
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_projects_collection

    await db_add_todo_status(project_id, name, mock_db)

    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_delete_todo_status_success():
    project_id = "507f1f77bcf86cd799439011"
    status_id = "507f1f77bcf86cd799439015"
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_projects_collection

    await db_delete_todo_status(project_id, status_id, mock_db)

    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_reorder_todo_statuses_success():
    project_id = "507f1f77bcf86cd799439011"
    new_statuses = [
        {"id": "507f1f77bcf86cd799439015", "name": "To Do"},
        {"id": "507f1f77bcf86cd799439016", "name": "Done"},
    ]
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_projects_collection

    await db_reorder_todo_statuses(project_id, new_statuses, mock_db)

    mock_projects_collection.update_one.assert_called_once()
