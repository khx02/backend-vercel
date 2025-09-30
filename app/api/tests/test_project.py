from unittest.mock import AsyncMock, patch
import pytest

from app.api.project import (
    approve_todo,
    get_project,
    add_todo,
    get_proposed_todos,
    increase_budget,
    spend_budget,
    update_todo,
    delete_todo,
    get_todo_items,
    reorder_todo_items,
    add_todo_status,
    delete_todo_status,
    reorder_todo_statuses,
    assign_todo,
)
from app.schemas.project import (
    AddTodoRequest,
    AddTodoResponse,
    AddTodoStatusRequest,
    AddTodoStatusResponse,
    ApproveTodoResponse,
    AssignTodoRequest,
    AssignTodoResponse,
    DeleteTodoRequest,
    DeleteTodoResponse,
    DeleteTodoStatusRequest,
    DeleteTodoStatusResponse,
    GetProjectResponse,
    GetProposedTodosResponse,
    GetTodoItemsResponse,
    ReorderTodoItemsRequest,
    ReorderTodoItemsResponse,
    ReorderTodoStatusesRequest,
    ReorderTodoStatusesResponse,
    UpdateTodoRequest,
    UpdateTodoResponse,
    Project,
)
from app.test_shared.constants import (
    MOCK_PROJECT_ID,
    MOCK_PROJECT_NAME,
    MOCK_PROJECT_DESCRIPTION,
    MOCK_TODO_ID,
    MOCK_TODO_STATUS_COLOUR,
    MOCK_TODO_STATUS_NAME,
    MOCK_USER_ID,
    MOCK_USER_2_ID,
)


@pytest.mark.asyncio
@patch("app.api.project.get_project_service")
async def test_get_project_success(mock_get_project_service):
    mock_db = AsyncMock()
    mock_get_project_service.return_value = GetProjectResponse(
        project=Project(
            id=MOCK_PROJECT_ID,
            name=MOCK_PROJECT_NAME,
            description=MOCK_PROJECT_DESCRIPTION,
            todo_statuses=[],
            todo_ids=[],
            budget_available=0,
            budget_spent=0,
        )
    )

    result = await get_project(MOCK_PROJECT_ID, db=mock_db)

    assert isinstance(result, GetProjectResponse)
    assert result.project.id == MOCK_PROJECT_ID
    assert result.project.name == MOCK_PROJECT_NAME
    assert result.project.description == MOCK_PROJECT_DESCRIPTION
    assert result.project.todo_statuses == []
    assert result.project.todo_ids == []


@pytest.mark.asyncio
@patch("app.api.project.add_todo_service")
async def test_add_todo_success(mock_add_todo_service):
    mock_db = AsyncMock()
    mock_user = AsyncMock()
    mock_add_todo_service.return_value = AddTodoResponse()
    todo_request = AddTodoRequest(
        name="Todo",
        description="Desc",
        status_id=MOCK_USER_ID,
        assignee_id=MOCK_USER_2_ID,
    )

    result = await add_todo(
        MOCK_PROJECT_ID, todo_request, current_user=mock_user, db=mock_db
    )

    assert isinstance(result, AddTodoResponse)


@pytest.mark.asyncio
@patch("app.api.project.update_todo_service")
async def test_update_todo_success(mock_update_todo_service):
    mock_db = AsyncMock()
    mock_update_todo_service.return_value = UpdateTodoResponse()
    update_todo_request = UpdateTodoRequest(
        todo_id=MOCK_TODO_ID,
        name="Updated",
        description="Desc",
        status_id=MOCK_USER_ID,
        assignee_id=MOCK_USER_2_ID,
    )

    result = await update_todo(MOCK_PROJECT_ID, update_todo_request, db=mock_db)

    assert isinstance(result, UpdateTodoResponse)


@pytest.mark.asyncio
@patch("app.api.project.delete_todo_service")
async def test_delete_todo_success(mock_delete_todo_service):
    mock_db = AsyncMock()
    mock_delete_todo_service.return_value = DeleteTodoResponse()
    delete_todo_request = DeleteTodoRequest(todo_id=MOCK_TODO_ID)

    result = await delete_todo(MOCK_PROJECT_ID, delete_todo_request, db=mock_db)

    assert isinstance(result, DeleteTodoResponse)


@pytest.mark.asyncio
@patch("app.api.project.get_todo_items_service")
async def test_get_todo_items_success(mock_get_todo_items_service):
    mock_db = AsyncMock()
    mock_get_todo_items_service.return_value = GetTodoItemsResponse(todos=[])

    result = await get_todo_items(MOCK_PROJECT_ID, db=mock_db)

    assert isinstance(result, GetTodoItemsResponse)
    assert result.todos == []


@pytest.mark.asyncio
@patch("app.api.project.reorder_todo_items_service")
async def test_reorder_todo_items_success(mock_reorder_todo_items_service):
    mock_db = AsyncMock()
    mock_reorder_todo_items_service.return_value = ReorderTodoItemsResponse()
    reorder_todo_items_request = ReorderTodoItemsRequest(new_todo_ids=[MOCK_TODO_ID])

    result = await reorder_todo_items(
        MOCK_PROJECT_ID, reorder_todo_items_request, db=mock_db
    )

    assert isinstance(result, ReorderTodoItemsResponse)


@pytest.mark.asyncio
@patch("app.api.project.add_todo_status_service")
async def test_add_todo_status_success(mock_add_todo_status_service):
    mock_db = AsyncMock()
    mock_add_todo_status_service.return_value = AddTodoStatusResponse()
    add_todo_status_request = AddTodoStatusRequest(
        name=MOCK_TODO_STATUS_NAME, color=MOCK_TODO_STATUS_COLOUR
    )

    result = await add_todo_status(MOCK_PROJECT_ID, add_todo_status_request, db=mock_db)

    assert isinstance(result, AddTodoStatusResponse)


@pytest.mark.asyncio
@patch("app.api.project.delete_todo_status_service")
async def test_delete_todo_status_success(mock_delete_todo_status_service):
    mock_db = AsyncMock()
    mock_delete_todo_status_service.return_value = DeleteTodoStatusResponse()
    delete_todo_status_request = DeleteTodoStatusRequest(status_id=MOCK_TODO_ID)

    result = await delete_todo_status(
        MOCK_PROJECT_ID, delete_todo_status_request, db=mock_db
    )

    assert isinstance(result, DeleteTodoStatusResponse)


@pytest.mark.asyncio
@patch("app.api.project.reorder_todo_statuses_service")
async def test_reorder_todo_statuses_success(
    mock_reorder_todo_statuses_service,
):
    mock_db = AsyncMock()
    mock_reorder_todo_statuses_service.return_value = ReorderTodoStatusesResponse()
    reorder_todo_statuses_request = ReorderTodoStatusesRequest(
        new_status_ids=[MOCK_TODO_ID]
    )

    result = await reorder_todo_statuses(
        MOCK_PROJECT_ID, reorder_todo_statuses_request, db=mock_db
    )

    assert isinstance(result, ReorderTodoStatusesResponse)


@pytest.mark.asyncio
@patch("app.api.project.assign_todo_service")
async def test_assign_todo_success(mock_assign_todo_service):
    mock_db = AsyncMock()
    mock_assign_todo_service.return_value = None
    assign_todo_request = AssignTodoRequest(
        todo_id=MOCK_TODO_ID, assignee_id=MOCK_USER_ID
    )

    result = await assign_todo(MOCK_PROJECT_ID, assign_todo_request, db=mock_db)

    assert isinstance(result, AssignTodoResponse)


@pytest.mark.asyncio
@patch("app.api.project.approve_todo_service")
async def test_approve_todo_success(mock_approve_todo_service):
    mock_db = AsyncMock()
    mock_approve_todo_service.return_value = None

    result = await approve_todo(MOCK_TODO_ID, db=mock_db)

    assert isinstance(result, ApproveTodoResponse)


@pytest.mark.asyncio
@patch("app.api.project.get_proposed_todos_service")
async def test_get_proposed_todos_success(mock_get_proposed_todos_service):
    mock_db = AsyncMock()
    mock_get_proposed_todos_service.return_value = []

    result = await get_proposed_todos(MOCK_PROJECT_ID, db=mock_db)

    assert isinstance(result, GetProposedTodosResponse)


@pytest.mark.asyncio
@patch("app.api.project.increase_budget_service")
async def test_increase_budget_success(mock_increase_budget_service):
    mock_db = AsyncMock()
    mock_increase_budget_service.return_value = None

    result = await increase_budget(MOCK_PROJECT_ID, 100.0, db=mock_db)

    assert result is None


@pytest.mark.asyncio
@patch("app.api.project.spend_budget_service")
async def test_spend_budget_success(mock_spend_budget_service):
    mock_db = AsyncMock()
    mock_spend_budget_service.return_value = None

    result = await spend_budget(MOCK_PROJECT_ID, 50.0, db=mock_db)

    assert result is None
