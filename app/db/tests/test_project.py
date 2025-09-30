from unittest.mock import AsyncMock, MagicMock
import pytest
from bson import ObjectId

from app.core.constants import PROJECTS_COLLECTION, TODOS_COLLECTION
from app.db.project import (
    db_approve_todo,
    db_assign_todo,
    db_get_project,
    db_add_todo,
    db_update_budget_available,
    db_update_budget_spent,
    db_update_todo,
    db_delete_todo,
    db_get_todo_items,
    db_add_todo_status,
    db_delete_todo_status,
    db_reorder_todo_statuses,
)
from app.schemas.project import AddTodoRequest, UpdateTodoRequest
from app.test_shared.constants import (
    MOCK_PROJECT_DESCRIPTION,
    MOCK_PROJECT_ID,
    MOCK_PROJECT_NAME,
    MOCK_STATUS_2_ID,
    MOCK_STATUS_ID,
    MOCK_TODO_DESCRIPTION,
    MOCK_TODO_ID,
    MOCK_TODO_NAME,
    MOCK_TODO_STATUS_2_NAME,
    MOCK_TODO_STATUS_COLOUR,
    MOCK_TODO_STATUS_NAME,
    MOCK_USER_ID,
)


@pytest.mark.asyncio
async def test_db_get_project_success():
    mock_projects_collection = AsyncMock()
    mock_projects_collection.find_one.return_value = {
        "_id": MOCK_PROJECT_ID,
        "name": MOCK_PROJECT_NAME,
        "description": MOCK_PROJECT_DESCRIPTION,
        "todo_statuses": [
            {"id": ObjectId(MOCK_STATUS_ID), "name": MOCK_TODO_STATUS_NAME},
            {"id": ObjectId(MOCK_STATUS_2_ID), "name": MOCK_TODO_STATUS_2_NAME},
        ],
        "todo_ids": [],
    }
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_projects_collection

    result = await db_get_project(MOCK_PROJECT_ID, mock_db)

    assert result["_id"] == MOCK_PROJECT_ID
    assert result["name"] == MOCK_PROJECT_NAME
    assert isinstance(result["todo_statuses"], list)


@pytest.mark.asyncio
async def test_db_add_todo_success():
    todo_req = AddTodoRequest(
        name=MOCK_TODO_NAME,
        description=MOCK_TODO_DESCRIPTION,
        status_id=MOCK_STATUS_ID,
        assignee_id=MOCK_USER_ID,
    )
    mock_todos_collection = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_result = AsyncMock()
    mock_result.inserted_id = ObjectId()
    mock_todos_collection.insert_one.return_value = mock_result
    mock_projects_collection.update_one.return_value = None
    mock_db = AsyncMock()

    def getitem(name):
        if name == TODOS_COLLECTION:
            return mock_todos_collection
        return mock_projects_collection

    mock_db.__getitem__.side_effect = getitem

    await db_add_todo(MOCK_PROJECT_ID, todo_req, False, mock_db)
    mock_todos_collection.insert_one.assert_called_once()
    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_update_todo_success():
    update_req = UpdateTodoRequest(
        todo_id=MOCK_TODO_ID,
        name=MOCK_TODO_NAME,
        description=MOCK_TODO_DESCRIPTION,
        status_id=MOCK_STATUS_ID,
        assignee_id=MOCK_USER_ID,
    )
    mock_todos_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_todos_collection

    await db_update_todo(MOCK_PROJECT_ID, update_req, mock_db)

    mock_todos_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_delete_todo_success():
    todo_id = MOCK_TODO_ID
    mock_todos_collection = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_todos_collection.delete_one.return_value = None
    mock_projects_collection.update_one.return_value = None
    mock_db = AsyncMock()

    def getitem(name):
        if name == TODOS_COLLECTION:
            return mock_todos_collection
        return mock_projects_collection

    mock_db.__getitem__.side_effect = getitem

    await db_delete_todo(MOCK_PROJECT_ID, todo_id, mock_db)

    mock_todos_collection.delete_one.assert_called_once()
    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_get_todo_items_success():
    mock_projects_collection = AsyncMock()
    mock_projects_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_PROJECT_ID),
        "todo_ids": [ObjectId(MOCK_TODO_ID)],
    }
    mock_todos_collection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(
        return_value=[
            {
                "_id": ObjectId(MOCK_TODO_ID),
                "name": MOCK_TODO_NAME,
                "description": MOCK_TODO_DESCRIPTION,
                "status_id": ObjectId(MOCK_STATUS_ID),
                "assignee_id": ObjectId(MOCK_USER_ID),
            }
        ]
    )
    mock_todos_collection.find.return_value = mock_cursor
    mock_db = AsyncMock()

    def getitem(name):
        if name == PROJECTS_COLLECTION:
            return mock_projects_collection
        return mock_todos_collection

    mock_db.__getitem__.side_effect = getitem
    result = await db_get_todo_items(MOCK_PROJECT_ID, mock_db)
    assert isinstance(result, list)
    assert result[0]["_id"] == MOCK_TODO_ID


@pytest.mark.asyncio
async def test_db_add_todo_status_success():
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_projects_collection

    await db_add_todo_status(
        MOCK_PROJECT_ID, MOCK_TODO_STATUS_NAME, MOCK_TODO_STATUS_COLOUR, mock_db
    )

    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_delete_todo_status_success():
    mock_db = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_todos_collection = AsyncMock()
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(
        return_value=[
            {
                "_id": ObjectId(MOCK_TODO_ID),
                "name": MOCK_TODO_NAME,
                "description": MOCK_TODO_DESCRIPTION,
                "status_id": ObjectId(MOCK_STATUS_ID),
                "assignee_id": ObjectId(MOCK_USER_ID),
            }
        ]
    )
    mock_todos_collection.find = MagicMock(return_value=mock_cursor)
    mock_todos_collection.delete_one.return_value = None
    mock_db.__getitem__.side_effect = lambda name: (
        mock_projects_collection
        if name == PROJECTS_COLLECTION
        else mock_todos_collection
    )

    result = await db_delete_todo_status(MOCK_PROJECT_ID, MOCK_STATUS_ID, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_reorder_todo_statuses_success():
    new_statuses = [
        {"id": MOCK_STATUS_ID, "name": MOCK_TODO_STATUS_NAME},
        {"id": MOCK_STATUS_2_ID, "name": MOCK_TODO_STATUS_2_NAME},
    ]
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_projects_collection

    await db_reorder_todo_statuses(MOCK_PROJECT_ID, new_statuses, mock_db)

    mock_projects_collection.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_db_assign_todo_success():
    todo_id = MOCK_TODO_ID
    assignee_id = MOCK_USER_ID
    mock_todos_collection = AsyncMock()
    mock_todos_collection.update_one.return_value = None
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_todos_collection

    result = await db_assign_todo(todo_id, assignee_id, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_approve_todo_success():
    mock_db = AsyncMock()
    mock_todos_collection = AsyncMock()
    mock_todos_collection.update_one.return_value = None
    mock_db.__getitem__.return_value = mock_todos_collection

    result = await db_approve_todo(MOCK_TODO_ID, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_update_budget_available_success():
    mock_db = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db.__getitem__.return_value = mock_projects_collection

    result = await db_update_budget_available(MOCK_PROJECT_ID, 100.0, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_update_budget_spent_success():
    mock_db = AsyncMock()
    mock_projects_collection = AsyncMock()
    mock_projects_collection.update_one.return_value = None
    mock_db.__getitem__.return_value = mock_projects_collection

    result = await db_update_budget_spent(MOCK_PROJECT_ID, 50.0, mock_db)

    assert result is None
