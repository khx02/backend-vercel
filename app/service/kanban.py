from app.schemas.kanban import KanbanModel, KanbanCreateReq, AddKanbanItemReq
from app.db.kanban import create_kanban as db_create_kanban, add_kanban_item as db_add_kanban_item
from app.db.team import add_kanban_to_team as db_add_kanban_to_team
from pymongo.asynchronous.database import AsyncDatabase


async def create_kanban_service(
    db: AsyncDatabase, kanban_create: KanbanCreateReq
) -> KanbanModel:

    kanban_in_db_dict = await db_create_kanban(db, kanban_create)

    # Attach the kanban ID to the team which created it
    await db_add_kanban_to_team(db, kanban_create.team_id, kanban_in_db_dict["_id"])

    return KanbanModel(
        id=kanban_in_db_dict["_id"],
        name=kanban_in_db_dict["name"],
    )


async def add_kanban_item_service(
    db: AsyncDatabase, add_kanban_item: AddKanbanItemReq
) -> None:

    kanban_item_dict = add_kanban_item.kanban_item.model_dump()

    await db_add_kanban_item(db, add_kanban_item.kanban_id, kanban_item_dict)
