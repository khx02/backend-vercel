from pymongo.asynchronous.database import AsyncDatabase
from app.schemas.kanban import KanbanCreateReq
from typing import Dict, Any

from bson import ObjectId

from app.core.constants import KANBANS_COLLECTION


async def create_kanban(
    db: AsyncDatabase, kanban_create: KanbanCreateReq
) -> Dict[str, Any] | None:

    kanban_dict = {
        "name": kanban_create.name,
    }

    result = await db[KANBANS_COLLECTION].insert_one(kanban_dict)

    kanban_dict["_id"] = str(result.inserted_id)
    return kanban_dict


# TODO: Validate kanban item, such as checking if the column is valid
async def add_kanban_item(
    db: AsyncDatabase, kanban_id: str, kanban_item: Dict[str, Any]
) -> None:
    item_object_id = ObjectId()

    kanban_item["_id"] = item_object_id

    await db[KANBANS_COLLECTION].update_one(
        {"_id": ObjectId(kanban_id)}, {"$addToSet": {"items": kanban_item}}
    )

    kanban_item["_id"] = str(item_object_id)  # Convert back to string for return

    return kanban_item


async def remove_kanban_item(db: AsyncDatabase, kanban_id: str, item_id: str) -> None:
    await db[KANBANS_COLLECTION].update_one(
        {"_id": ObjectId(kanban_id)}, {"$pull": {"items": {"_id": ObjectId(item_id)}}}
    )
