from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import TODOS_COLLECTION
from app.schemas import project
from app.schemas.project import (
    AddTodoRequest,
    AddTodoResponse,
    GetProjectResponse,
    GetTodoItemsResponse,
    Project,
    TodoStatus,
)
from app.db.project import db_add_todo, db_get_todo_items
from app.db.project import db_get_project

from bson import ObjectId

from app.schemas.todo import Todo


async def get_project_service(project_id: str, db: AsyncDatabase) -> GetProjectResponse:

    project_in_db_dict = await db_get_project(project_id, db)

    return GetProjectResponse(
        project=Project(
            id=project_in_db_dict["_id"],
            name=project_in_db_dict["name"],
            description=project_in_db_dict["description"],
            todo_statuses=project_in_db_dict["todo_statuses"],
            todo_ids=project_in_db_dict["todo_ids"],
        )
    )


async def add_todo_service(
    project_id: str, todo_request: AddTodoRequest, db: AsyncDatabase
) -> AddTodoResponse:

    await db_add_todo(project_id, todo_request, db)

    return AddTodoResponse()


async def get_todo_items_service(
    project_id: str, db: AsyncDatabase
) -> GetTodoItemsResponse:

    todo_items_in_db_list = await db_get_todo_items(project_id, db)

    return GetTodoItemsResponse(
        todos=[
            Todo(
                id=todo["_id"],
                name=todo["name"],
                description=todo["description"],
                status_id=todo["status_id"],
            )
            for todo in todo_items_in_db_list
        ]
    )
