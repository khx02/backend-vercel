from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import TODOS_COLLECTION
from app.schemas import project
from app.schemas.project import (
    AddTodoRequest,
    AddTodoResponse,
    AddTodoStatusRequest,
    AddTodoStatusResponse,
    DeleteTodoStatusRequest,
    DeleteTodoStatusResponse,
    GetProjectResponse,
    GetTodoItemsResponse,
    Project,
    TodoStatus,
)
from app.db.project import (
    db_add_todo,
    db_add_todo_status,
    db_delete_todo_status,
    db_get_todo_items,
)
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


async def add_todo_status_service(
    project_id: str, todo_status_request: AddTodoStatusRequest, db: AsyncDatabase
) -> AddTodoStatusResponse:

    await db_add_todo_status(project_id, todo_status_request.name, db)

    return AddTodoStatusResponse()


async def delete_todo_status_service(
    project_id: str,
    delete_todo_status_request: DeleteTodoStatusRequest,
    db: AsyncDatabase,
) -> DeleteTodoStatusResponse:

    await db_delete_todo_status(project_id, delete_todo_status_request.status_id, db)

    return DeleteTodoStatusResponse()
