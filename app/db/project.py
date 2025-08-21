from typing import Any, Dict, List
from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import PROJECTS_COLLECTION, TODOS_COLLECTION
from app.schemas.project import AddTodoRequest, UpdateTodoRequest


def stringify_project_dict(project_dict: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_id": str(project_dict["_id"]),
        "name": project_dict["name"],
        "description": project_dict["description"],
        "todo_statuses": [
            {"id": str(status["id"]), "name": status["name"]}
            for status in project_dict["todo_statuses"]
        ],
        "todo_ids": [str(todo_id) for todo_id in project_dict["todo_ids"]],
    }


async def db_get_project(project_id: str, db: AsyncDatabase) -> Dict[str, Any]:

    result = await db[PROJECTS_COLLECTION].find_one({"_id": ObjectId(project_id)})
    if not result:
        raise ValueError(f"Project with ID {project_id} not found")

    return stringify_project_dict(result)


async def db_add_todo(
    project_id: str, add_todo_request: AddTodoRequest, db: AsyncDatabase
) -> None:
    todo_dict = {
        "name": add_todo_request.name,
        "description": add_todo_request.description,
        "status_id": ObjectId(add_todo_request.status_id),
        "owner_id": ObjectId(add_todo_request.owner_id),
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
                "owner_id": ObjectId(update_todo_request.owner_id),
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
    todos = [
        {**todo, "_id": str(todo["_id"]), "status_id": str(todo["status_id"])}
        for todo in todos
    ]

    return todos


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
