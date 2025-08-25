import re
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

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
    DeleteTodoRequest,
    DeleteTodoResponse,
    DeleteTodoStatusRequest,
    DeleteTodoStatusResponse,
    GetProjectResponse,
    GetTodoItemsResponse,
    ReorderTodoItemsRequest,
    ReorderTodoItemsResponse,
    ReorderTodoStatusesRequest,
    ReorderTodoStatusesResponse,
    UpdateTodoRequest,
    UpdateTodoResponse,
)
from app.service.project import (
    add_todo_service,
    add_todo_status_service,
    delete_todo_service,
    delete_todo_status_service,
    get_project_service,
    get_todo_items_service,
    reorder_todo_items_service,
    reorder_todo_statuses_service,
    update_todo_service,
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
    _: None = Depends(require_executive_project_access),
    db: AsyncDatabase = Depends(get_db),
) -> AddTodoResponse:

    return await add_todo_service(project_id, todo_request, db)


# TODO: Ensure that todo status falls within the existing status ids
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
