from typing import Any, Dict, List
from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.common import stringify_object_ids
from app.core.constants import PROJECTS_COLLECTION, TODOS_COLLECTION
from app.schemas.project import AddTodoRequest, UpdateTodoRequest


async def db_get_project(project_id: str, db: AsyncDatabase) -> Dict[str, Any]:

    result = await db[PROJECTS_COLLECTION].find_one({"_id": ObjectId(project_id)})
    if not result:
        raise ValueError(f"Project with ID {project_id} not found")

    return stringify_object_ids(result)


async def db_add_todo(
    project_id: str, add_todo_request: AddTodoRequest, db: AsyncDatabase
) -> None:
    todo_dict = {
        "name": add_todo_request.name,
        "description": add_todo_request.description,
        "status_id": ObjectId(add_todo_request.status_id),
        "assignee_id": (
            ObjectId(add_todo_request.assignee_id)
            if add_todo_request.assignee_id
            else None
        ),
    }
    result = await db[TODOS_COLLECTION].insert_one(todo_dict)

    todo_dict["_id"] = result.inserted_id
    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$addToSet": {"todo_ids": todo_dict["_id"]}},
    )


async def db_update_todo(
    project_id: str, update_todo_request: UpdateTodoRequest, db: AsyncDatabase
) -> None:

    await db[TODOS_COLLECTION].update_one(
        {"_id": ObjectId(update_todo_request.todo_id)},
        {
            "$set": {
                "name": update_todo_request.name,
                "description": update_todo_request.description,
                "status_id": ObjectId(update_todo_request.status_id),
                "assignee_id": ObjectId(update_todo_request.assignee_id),
            }
        },
    )


async def db_delete_todo(project_id: str, todo_id: str, db: AsyncDatabase) -> None:

    await db[TODOS_COLLECTION].delete_one({"_id": ObjectId(todo_id)})
    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$pull": {"todo_ids": ObjectId(todo_id)}},
    )


async def db_get_todo_items(project_id: str, db: AsyncDatabase) -> List[Dict[str, Any]]:

    project = await db[PROJECTS_COLLECTION].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise ValueError(f"Project with ID {project_id} not found")

    todo_ids = project["todo_ids"]
    if not todo_ids:
        return []

    todos = await db[TODOS_COLLECTION].find({"_id": {"$in": todo_ids}}).to_list(None)

    # Turn all ObjectIDs into strings
    return stringify_object_ids(todos)


async def db_reorder_todo_items(
    project_id: str, new_todo_ids: List[str], db: AsyncDatabase
) -> None:

    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"todo_ids": [ObjectId(todo_id) for todo_id in new_todo_ids]}},
    )


async def db_add_todo_status(project_id: str, name: str, db: AsyncDatabase) -> None:

    todo_status_dict = {"id": ObjectId(), "name": name}

    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$addToSet": {"todo_statuses": todo_status_dict}},
    )


async def db_delete_todo_status(
    project_id: str, status_id: str, db: AsyncDatabase
) -> None:

    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$pull": {"todo_statuses": {"id": ObjectId(status_id)}}},
    )


async def db_reorder_todo_statuses(
    project_id: str, new_statuses: List[Dict[str, Any]], db: AsyncDatabase
) -> None:

    new_statuses = [
        {"id": ObjectId(status["id"]), "name": status["name"]}
        for status in new_statuses
    ]

    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"todo_statuses": new_statuses}},
    )


async def db_assign_todo(todo_id: str, assignee_id: str, db: AsyncDatabase) -> None:

    await db[TODOS_COLLECTION].update_one(
        {"_id": ObjectId(todo_id)},
        {"$set": {"assignee_id": ObjectId(assignee_id)}},
    )
