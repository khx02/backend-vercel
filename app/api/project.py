from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db
from app.schemas.project import (
    GetProjectRequest,
    GetProjectResponse,
    GetTodoItemsRequest,
    GetTodoItemsResponse,
)
from app.service.project import (
    get_project_service,
    get_todo_items_service,
)

router = APIRouter()


@router.get("/get-project/{project_id}")
async def get_project(
    project_id: str,
    _: GetProjectRequest,
    db: AsyncDatabase = Depends(get_db),
) -> GetProjectResponse:

    return await get_project_service(project_id, db)


@router.get("/get-todo-items/{project_id}")
async def get_todo_items(
    project_id: str, _: GetTodoItemsRequest, db: AsyncDatabase = Depends(get_db)
) -> GetTodoItemsResponse:

    return await get_todo_items_service(project_id, db)
