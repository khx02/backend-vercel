from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db
from app.schemas.project import (
    CreateProjectRequest,
    CreateProjectResponse,
)
from app.service.project import create_project_service

router = APIRouter()


@router.post("/projects")
async def create_project(
    create_project_request: CreateProjectRequest,
    db: AsyncDatabase = Depends(get_db),
) -> CreateProjectResponse:

    return await create_project_service(create_project_request, db)
