from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db
from app.schemas.kanban import (AddKanbanItemReq, KanbanCreateReq, KanbanItem,
                                KanbanModel, RemoveKanbanItemReq)
from app.service.kanban import (add_kanban_item_service, create_kanban_service,
                                delete_kanban_item_service)

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


@router.post("/add_kanban_item/{kanban_id}", response_model=KanbanItem)
async def add_kanban_item(
    kanban_id: str,
    add_kanban_item: AddKanbanItemReq,
    db: AsyncDatabase = Depends(get_db),
) -> KanbanItem:
    try:
        return await add_kanban_item_service(db, kanban_id, add_kanban_item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to kanban board",
        )


@router.delete("/remove_kanban_item/{kanban_id}")
async def remove_kanban_item(
    kanban_id: str,
    remove_kanban_item: RemoveKanbanItemReq,
    db: AsyncDatabase = Depends(get_db),
) -> None:
    try:
        await delete_kanban_item_service(db, kanban_id, remove_kanban_item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from kanban board",
        )
