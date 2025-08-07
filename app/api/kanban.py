from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db

from app.schemas.kanban import KanbanModel, KanbanCreateReq
from app.service.kanban import create_kanban_service

router = APIRouter()


@router.post("/create_kanban", response_model=KanbanModel)
async def create_kanban(
    kanban_create: KanbanCreateReq, db: AsyncDatabase = Depends(get_db)
) -> KanbanModel:
    try:
        return await create_kanban_service(db, kanban_create)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create kanban board",
        )
