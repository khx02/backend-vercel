from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db
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
    ReorderTodoStatusesRequest,
    ReorderTodoStatusesResponse,
)
from app.service.project import (
    add_todo_service,
    add_todo_status_service,
    delete_todo_service,
    delete_todo_status_service,
    get_project_service,
    get_todo_items_service,
    reorder_todo_statuses_service,
)

router = APIRouter()


@router.get("/get-project/{project_id}")
async def get_project(
    project_id: str,
    db: AsyncDatabase = Depends(get_db),
) -> GetProjectResponse:

    return await get_project_service(project_id, db)


@router.post("/add-todo/{project_id}")
async def add_todo(
    project_id: str,
    todo_request: AddTodoRequest,
    db: AsyncDatabase = Depends(get_db),
) -> AddTodoResponse:

    return await add_todo_service(project_id, todo_request, db)

@router.delete("/delete-todo/{project_id}")
async def delete_todo(
    project_id: str,
    delete_todo_request: DeleteTodoRequest,
    db: AsyncDatabase = Depends(get_db),
) -> DeleteTodoResponse:

    return await delete_todo_service(project_id, delete_todo_request, db)

@router.get("/get-todo-items/{project_id}")
async def get_todo_items(
    project_id: str, db: AsyncDatabase = Depends(get_db)
) -> GetTodoItemsResponse:

    return await get_todo_items_service(project_id, db)


@router.post("/add-todo-status/{project_id}")
async def add_todo_status(
    project_id: str,
    add_todo_status_request: AddTodoStatusRequest,
    db: AsyncDatabase = Depends(get_db),
) -> AddTodoStatusResponse:

    return await add_todo_status_service(project_id, add_todo_status_request, db)


@router.post("/delete-todo-status/{project_id}")
async def delete_todo_status(
    project_id: str,
    delete_todo_status_request: DeleteTodoStatusRequest,
    db: AsyncDatabase = Depends(get_db),
) -> DeleteTodoStatusResponse:

    return await delete_todo_status_service(project_id, delete_todo_status_request, db)


@router.post("/reorder-todo-statuses/{project_id}")
async def reorder_todo_statuses(
    project_id: str,
    reorder_todo_statuses_request: ReorderTodoStatusesRequest,
    db: AsyncDatabase = Depends(get_db),
) -> ReorderTodoStatusesResponse:

    return await reorder_todo_statuses_service(
        project_id, reorder_todo_statuses_request, db
    )
