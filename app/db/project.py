from typing import Any, Dict, List
from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.project import CreateProjectRequest

from app.core.constants import PROJECTS_COLLECTION, TODOS_COLLECTION


async def db_create_project(
    create_project_request: CreateProjectRequest, db: AsyncDatabase
) -> Dict[str, Any]:

    project_dict = {
        "name": create_project_request.name,
        "description": create_project_request.description,
    }

    result = await db[PROJECTS_COLLECTION].insert_one(project_dict)

    project_dict["_id"] = str(result.inserted_id)
    return project_dict


async def db_get_project(project_id: str, db: AsyncDatabase) -> Dict[str, Any]:

    result = await db[PROJECTS_COLLECTION].find_one({"_id": ObjectId(project_id)})
    if not result:
        raise ValueError(f"Project with ID {project_id} not found")

    result["_id"] = str(result["_id"])

    return result


async def db_get_todo_items(project_id: str, db: AsyncDatabase) -> List[Dict[str, Any]]:

    project = await db[PROJECTS_COLLECTION].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise ValueError(f"Project with ID {project_id} not found")

    todo_ids = project["todo_ids"]
    if not todo_ids:
        return []

    todos = (
        await db[TODOS_COLLECTION]
        .find({"_id": {"$in": [ObjectId(todo_id) for todo_id in todo_ids]}})
        .to_list(None)
    )

    return todos
