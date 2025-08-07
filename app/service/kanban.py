from app.schemas.kanban import (
    KanbanModel,
    KanbanCreateReq,
    AddKanbanItemReq,
    KanbanItem,
    RemoveKanbanItemReq,
)
from app.db.kanban import (
    create_kanban as db_create_kanban,
    add_kanban_item as db_add_kanban_item,
    remove_kanban_item as db_remove_kanban_item,
)
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


# TODO: Move ObjectID generation to DB layer
async def add_kanban_item_service(
    db: AsyncDatabase, add_kanban_item: AddKanbanItemReq
) -> KanbanItem:
    kanban_item_dict = {
        "name": add_kanban_item.name,
        "start_at": add_kanban_item.start_at,
        "end_at": add_kanban_item.end_at,
        "column": add_kanban_item.column,
        "owner": add_kanban_item.owner,
    }

    kanban_item_in_db_dict = await db_add_kanban_item(
        db, add_kanban_item.kanban_id, kanban_item_dict
    )

    return KanbanItem(
        id=kanban_item_in_db_dict["_id"],
        name=kanban_item_in_db_dict["name"],
        start_at=kanban_item_in_db_dict["start_at"],
        end_at=kanban_item_in_db_dict["end_at"],
        column=kanban_item_in_db_dict["column"],
        owner=kanban_item_in_db_dict["owner"],
    )


async def delete_kanban_item_service(
    db: AsyncDatabase,
    remove_kanban_item: RemoveKanbanItemReq,
) -> None:

    await db_remove_kanban_item(
        db, remove_kanban_item.kanban_id, remove_kanban_item.item_id
    )
