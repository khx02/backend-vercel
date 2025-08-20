from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db
from app.schemas.project import (
    AddTodoRequest,
    AddTodoResponse,
    GetProjectResponse,
    GetTodoItemsResponse,
)
from app.service.project import (
    add_todo_service,
    get_project_service,
    get_todo_items_service,
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


@router.get("/get-todo-items/{project_id}")
async def get_todo_items(
    project_id: str, db: AsyncDatabase = Depends(get_db)
) -> GetTodoItemsResponse:

    return await get_todo_items_service(project_id, db)
