from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.api.auth import get_current_user_info
from app.db.client import get_db
from app.dependencies.project import (
    require_standard_project_access,
    require_executive_project_access,
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
    UpdateTodoStatusRequest,
    UpdateTodoStatusResponse,
)
from app.schemas.user import UserModel
from app.service.project import (
    add_todo_service,
    add_todo_status_service,
    approve_todo_service,
    assign_todo_service,
    delete_todo_service,
    delete_todo_status_service,
    get_project_service,
    get_proposed_todos_service,
    get_todo_items_service,
    increase_budget_service,
    reorder_todo_items_service,
    reorder_todo_statuses_service,
    spend_budget_service,
    update_todo_service,
    update_todo_status_service,
)

router = APIRouter()


@router.get("/get-project/{project_id}")
async def get_project(
    project_id: str,
    _: None = Depends(require_standard_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> GetProjectResponse:

    return await get_project_service(project_id, db)


@router.post("/add-todo/{project_id}")
async def add_todo(
    project_id: str,
    todo_request: AddTodoRequest,
    _: None = Depends(require_standard_project_access),
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> AddTodoResponse:

    return await add_todo_service(project_id, todo_request, current_user.id, db)


# TODO: Allow for assigned id to also perform update
@router.post("/update-todo/{project_id}")
async def update_todo(
    project_id: str,
    update_todo_request: UpdateTodoRequest,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> UpdateTodoResponse:

    return await update_todo_service(project_id, update_todo_request, db)


@router.delete("/delete-todo/{project_id}")
async def delete_todo(
    project_id: str,
    delete_todo_request: DeleteTodoRequest,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> DeleteTodoResponse:

    return await delete_todo_service(project_id, delete_todo_request, db)


@router.get("/get-todo-items/{project_id}")
async def get_todo_items(
    project_id: str,
    _: None = Depends(require_standard_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> GetTodoItemsResponse:

    return await get_todo_items_service(project_id, db)


@router.post("/reorder-todo-items/{project_id}")
async def reorder_todo_items(
    project_id: str,
    reorder_todo_items_request: ReorderTodoItemsRequest,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> ReorderTodoItemsResponse:

    return await reorder_todo_items_service(project_id, reorder_todo_items_request, db)


@router.post("/add-todo-status/{project_id}")
async def add_todo_status(
    project_id: str,
    add_todo_status_request: AddTodoStatusRequest,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> AddTodoStatusResponse:

    return await add_todo_status_service(project_id, add_todo_status_request, db)


@router.post("/delete-todo-status/{project_id}")
async def delete_todo_status(
    project_id: str,
    delete_todo_status_request: DeleteTodoStatusRequest,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> DeleteTodoStatusResponse:

    return await delete_todo_status_service(project_id, delete_todo_status_request, db)


@router.post("/reorder-todo-statuses/{project_id}")
async def reorder_todo_statuses(
    project_id: str,
    reorder_todo_statuses_request: ReorderTodoStatusesRequest,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> ReorderTodoStatusesResponse:

    return await reorder_todo_statuses_service(
        project_id, reorder_todo_statuses_request, db
    )


@router.post("/update-todo-status/{project_id}")
async def update_todo_status(
    project_id: str,
    update_todo_status_request: UpdateTodoStatusRequest,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> UpdateTodoStatusResponse:

    return await update_todo_status_service(project_id, update_todo_status_request, db)


@router.post("/assign-todo/{project_id}")
async def assign_todo(
    project_id: str,
    assign_todo_request: AssignTodoRequest,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> AssignTodoResponse:

    await assign_todo_service(
        project_id, assign_todo_request.todo_id, assign_todo_request.assignee_id, db
    )

    return AssignTodoResponse()


# TODO: Make sure this actually works, because project_id is not in signature
@router.post("/approve-todo/{project_id}/{todo_id}")  # project_id is used in dependency
async def approve_todo(
    todo_id: str,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> ApproveTodoResponse:

    await approve_todo_service(todo_id, db)

    return ApproveTodoResponse()


@router.get("/get-proposed-todos/{project_id}")
async def get_proposed_todos(
    project_id: str,
    _: None = Depends(require_standard_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> GetProposedTodosResponse:

    return GetProposedTodosResponse(
        proposed_todos=await get_proposed_todos_service(project_id, db)
    )


@router.post("/increase-budget/{project_id}")
async def increase_budget(
    project_id: str,
    amount: float,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> None:

    await increase_budget_service(project_id, amount, db)


@router.post("/spend-budget/{project_id}")
async def spend_budget(
    project_id: str,
    amount: float,
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> None:

    await spend_budget_service(project_id, amount, db)
