from unittest.mock import AsyncMock, patch
import pytest
from app.schemas.project import (
    AddTodoRequest,
    AddTodoStatusRequest,
    DeleteTodoRequest,
    DeleteTodoStatusRequest,
    GetProjectResponse,
    GetTodoItemsResponse,
    Project,
    ReorderTodoStatusesRequest,
    UpdateTodoRequest,
)
from app.schemas.todo import Todo
from app.service.project import (
    get_project_service,
    add_todo_service,
    update_todo_service,
    delete_todo_service,
    get_todo_items_service,
    add_todo_status_service,
    delete_todo_status_service,
    reorder_todo_statuses_service,
)


@pytest.mark.asyncio
@patch("app.service.project.db_get_project")
async def test_get_project_service_success(mock_db_get_project):
    project_id = "proj1"
    mock_db = AsyncMock()
    mock_db_get_project.return_value = {
        "_id": project_id,
        "name": "Test Project",
        "description": "Desc",
        "todo_statuses": [],
        "todo_ids": [],
    }
    result = await get_project_service(project_id, mock_db)
    assert isinstance(result, GetProjectResponse)
    assert result.project.id == project_id
    assert result.project.name == "Test Project"
    assert result.project.description == "Desc"
    assert result.project.todo_statuses == []
    assert result.project.todo_ids == []


@pytest.mark.asyncio
@patch("app.service.project.db_add_todo")
async def test_add_todo_service_success(mock_db_add_todo):
    project_id = "proj1"
    mock_db = AsyncMock()
    todo_req = AddTodoRequest(name="Todo", description="Desc", status_id="status1")
    mock_db_add_todo.return_value = None
    result = await add_todo_service(project_id, todo_req, mock_db)
    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_update_todo")
async def test_update_todo_service_success(mock_db_update_todo):
    project_id = "proj1"
    mock_db = AsyncMock()
    update_req = UpdateTodoRequest(
        todo_id="todo1", name="Updated", description="Desc", status_id="status1"
    )
    mock_db_update_todo.return_value = None
    result = await update_todo_service(project_id, update_req, mock_db)
    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_delete_todo")
async def test_delete_todo_service_success(mock_db_delete_todo):
    project_id = "proj1"
    mock_db = AsyncMock()
    delete_req = DeleteTodoRequest(todo_id="todo1")
    mock_db_delete_todo.return_value = None
    result = await delete_todo_service(project_id, delete_req, mock_db)
    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_get_todo_items")
async def test_get_todo_items_service_success(mock_db_get_todo_items):
    project_id = "proj1"
    mock_db = AsyncMock()
    mock_db_get_todo_items.return_value = [
        {"_id": "todo1", "name": "Todo", "description": "Desc", "status_id": "status1"}
    ]
    result = await get_todo_items_service(project_id, mock_db)
    assert isinstance(result, GetTodoItemsResponse)
    assert len(result.todos) == 1
    assert result.todos[0].id == "todo1"


@pytest.mark.asyncio
@patch("app.service.project.db_add_todo_status")
async def test_add_todo_status_service_success(mock_db_add_todo_status):
    project_id = "proj1"
    mock_db = AsyncMock()
    status_req = AddTodoStatusRequest(name="In Progress")
    mock_db_add_todo_status.return_value = None
    result = await add_todo_status_service(project_id, status_req, mock_db)
    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_delete_todo_status")
async def test_delete_todo_status_service_success(mock_db_delete_todo_status):
    project_id = "proj1"
    mock_db = AsyncMock()
    delete_status_req = DeleteTodoStatusRequest(status_id="status1")
    mock_db_delete_todo_status.return_value = None
    result = await delete_todo_status_service(project_id, delete_status_req, mock_db)
    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_get_project")
@patch("app.service.project.db_reorder_todo_statuses")
async def test_reorder_todo_statuses_service_success(
    mock_db_reorder_todo_statuses, mock_db_get_project
):
    project_id = "proj1"
    mock_db = AsyncMock()
    reorder_req = ReorderTodoStatusesRequest(new_status_ids=["status1", "status2"])
    mock_db_get_project.return_value = {
        "todo_statuses": [
            {"id": "status2", "name": "Done"},
            {"id": "status1", "name": "In Progress"},
        ]
    }
    mock_db_reorder_todo_statuses.return_value = None
    result = await reorder_todo_statuses_service(project_id, reorder_req, mock_db)
    assert result is not None
