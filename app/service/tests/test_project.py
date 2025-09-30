from unittest.mock import AsyncMock, patch
import pytest
from app.schemas.project import (
    AddTodoRequest,
    AddTodoStatusRequest,
    DeleteTodoRequest,
    DeleteTodoStatusRequest,
    GetProjectResponse,
    GetTodoItemsResponse,
    ReorderTodoStatusesRequest,
    UpdateTodoRequest,
)
from app.service.project import (
    approve_todo_service,
    get_project_service,
    add_todo_service,
    get_proposed_todos_service,
    increase_budget_service,
    spend_budget_service,
    update_todo_service,
    delete_todo_service,
    get_todo_items_service,
    add_todo_status_service,
    delete_todo_status_service,
    reorder_todo_statuses_service,
)
from app.test_shared.constants import (
    MOCK_PROJECT_ID,
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
@patch("app.service.project.db_get_project")
async def test_get_project_service_success(mock_db_get_project):
    project_id = MOCK_PROJECT_ID
    mock_db = AsyncMock()
    mock_db_get_project.return_value = {
        "_id": project_id,
        "name": "Test Project",
        "description": "Desc",
        "todo_statuses": [],
        "todo_ids": [],
        "budget_available": 0,
        "budget_spent": 0,
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
@patch("app.service.project.db_get_team_by_project_id")
@patch("app.service.project.db_get_project")
async def test_add_todo_service_success(
    mock_db_get_project, mock_db_get_team_by_project_id, mock_db_add_todo
):
    mock_db = AsyncMock()
    todo_req = AddTodoRequest(
        name=MOCK_TODO_NAME,
        description=MOCK_TODO_DESCRIPTION,
        status_id=MOCK_STATUS_ID,
        assignee_id=MOCK_USER_ID,
    )
    mock_db_get_project.return_value = {"_id": MOCK_PROJECT_ID}
    mock_db_get_team_by_project_id.return_value = {"exec_member_ids": []}
    mock_db_add_todo.return_value = None

    result = await add_todo_service(MOCK_PROJECT_ID, todo_req, MOCK_USER_ID, mock_db)

    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_update_todo")
@patch("app.service.project.db_get_project")
async def test_update_todo_service_success(mock_db_get_project, mock_db_update_todo):
    mock_db = AsyncMock()
    update_req = UpdateTodoRequest(
        todo_id=MOCK_TODO_ID,
        name=MOCK_TODO_NAME,
        description=MOCK_TODO_DESCRIPTION,
        status_id=MOCK_STATUS_ID,
        assignee_id=MOCK_USER_ID,
    )
    mock_db_get_project.return_value = {
        "_id": MOCK_PROJECT_ID,
        "todo_statuses": [
            {
                "id": MOCK_STATUS_ID,
                "name": MOCK_TODO_STATUS_NAME,
            },
            {
                "id": MOCK_STATUS_2_ID,
                "name": MOCK_TODO_STATUS_2_NAME,
            },
        ],
    }
    mock_db_update_todo.return_value = None
    result = await update_todo_service(MOCK_PROJECT_ID, update_req, mock_db)

    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_delete_todo")
@patch("app.service.project.db_get_project")
async def test_delete_todo_service_success(mock_db_get_project, mock_db_delete_todo):
    mock_db = AsyncMock()
    delete_req = DeleteTodoRequest(todo_id=MOCK_TODO_ID)
    mock_db_get_project.return_value = {
        "_id": MOCK_PROJECT_ID,
        "todo_ids": [MOCK_TODO_ID],
    }
    mock_db_delete_todo.return_value = None

    result = await delete_todo_service(MOCK_PROJECT_ID, delete_req, mock_db)

    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_get_todo_items")
@patch("app.service.project.db_get_project")
async def test_get_todo_items_service_success(
    mock_db_get_project, mock_db_get_todo_items
):
    mock_db = AsyncMock()
    mock_db_get_project.return_value = {
        "_id": MOCK_PROJECT_ID,
    }
    mock_db_get_todo_items.return_value = [
        {
            "_id": MOCK_TODO_ID,
            "name": MOCK_TODO_NAME,
            "description": MOCK_TODO_DESCRIPTION,
            "status_id": MOCK_STATUS_ID,
            "assignee_id": MOCK_USER_ID,
            "approved": True,
        }
    ]

    result = await get_todo_items_service(MOCK_PROJECT_ID, mock_db)

    assert isinstance(result, GetTodoItemsResponse)
    assert len(result.todos) == 1
    assert result.todos[0].id == MOCK_TODO_ID


@pytest.mark.asyncio
@patch("app.service.project.db_add_todo_status")
@patch("app.service.project.db_get_project")
async def test_add_todo_status_service_success(
    mock_db_get_project, mock_db_add_todo_status
):
    mock_db = AsyncMock()
    status_req = AddTodoStatusRequest(
        name=MOCK_TODO_NAME, color=MOCK_TODO_STATUS_COLOUR
    )
    mock_db_get_project.return_value = {
        "_id": MOCK_PROJECT_ID,
    }
    mock_db_add_todo_status.return_value = None

    result = await add_todo_status_service(MOCK_PROJECT_ID, status_req, mock_db)

    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_delete_todo_status")
@patch("app.service.project.db_get_project")
async def test_delete_todo_status_service_success(
    mock_db_get_project, mock_db_delete_todo_status
):
    project_id = MOCK_PROJECT_ID
    mock_db = AsyncMock()
    mock_db_get_project.return_value = {
        "_id": MOCK_PROJECT_ID,
        "todo_statuses": [
            {"id": MOCK_STATUS_ID, "name": MOCK_TODO_STATUS_NAME},
            {"id": MOCK_STATUS_2_ID, "name": MOCK_TODO_STATUS_2_NAME},
        ],
    }
    delete_status_req = DeleteTodoStatusRequest(status_id=MOCK_STATUS_ID)
    mock_db_delete_todo_status.return_value = None

    result = await delete_todo_status_service(project_id, delete_status_req, mock_db)

    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_get_project")
@patch("app.service.project.db_reorder_todo_statuses")
async def test_reorder_todo_statuses_service_success(
    mock_db_reorder_todo_statuses, mock_db_get_project
):
    project_id = MOCK_PROJECT_ID
    mock_db = AsyncMock()
    reorder_req = ReorderTodoStatusesRequest(
        new_status_ids=[MOCK_STATUS_2_ID, MOCK_STATUS_ID]
    )
    mock_db_get_project.return_value = {
        "todo_statuses": [
            {"id": MOCK_STATUS_2_ID, "name": "Done"},
            {"id": MOCK_STATUS_ID, "name": "In Progress"},
        ]
    }
    mock_db_reorder_todo_statuses.return_value = None

    result = await reorder_todo_statuses_service(project_id, reorder_req, mock_db)

    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_approve_todo")
async def test_approve_todo_service_success(mock_db_approve_todo):
    mock_db = AsyncMock()
    mock_db_approve_todo.return_value = None

    result = await approve_todo_service(MOCK_PROJECT_ID, mock_db)

    assert result is None


@pytest.mark.asyncio
@patch("app.service.project.get_todo_items_service")
@patch("app.service.project.db_get_project")
async def test_get_proposed_todos_service_success(
    mock_db_get_project, mock_get_todo_items_service
):
    mock_db = AsyncMock()
    mock_db_get_project.return_value = {"_id": MOCK_PROJECT_ID}
    mock_get_todo_items_service.return_value = GetTodoItemsResponse(todos=[])
    result = await get_proposed_todos_service(MOCK_PROJECT_ID, mock_db)

    assert result is not None


@pytest.mark.asyncio
@patch("app.service.project.db_update_budget_available")
@patch("app.service.project.db_get_project")
async def test_increase_budget_service_success(
    mock_db_get_project, mock_db_update_budget_available
):
    mock_db = AsyncMock()
    mock_db_get_project.return_value = {
        "_id": MOCK_PROJECT_ID,
        "budget_available": 1000.0,
    }
    mock_db_update_budget_available.return_value = None

    result = await increase_budget_service(MOCK_PROJECT_ID, 100.0, mock_db)

    assert result is None


@pytest.mark.asyncio
@patch("app.service.project.db_update_budget_spent")
@patch("app.service.project.db_update_budget_available")
@patch("app.service.project.db_get_project")
async def test_spend_budget_service_success(
    mock_db_get_project,
    mock_db_update_budget_available,
    mock_db_update_budget_spent,
):
    mock_db = AsyncMock()
    mock_db_get_project.return_value = {
        "_id": MOCK_PROJECT_ID,
        "budget_available": 1000.0,
        "budget_spent": 200.0,
    }
    mock_db_update_budget_available.return_value = None
    mock_db_update_budget_spent.return_value = None

    result = await spend_budget_service(MOCK_PROJECT_ID, 50.0, mock_db)

    assert result is None
