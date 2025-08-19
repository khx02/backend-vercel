from pymongo.asynchronous.database import AsyncDatabase

from app.schemas import project
from app.schemas.project import (
    CreateProjectRequest,
    CreateProjectResponse,
    GetProjectResponse,
    GetTodoItemsResponse,
    Project,
    TodoStatus,
)
from app.db.project import db_create_project, db_get_todo_items
from app.db.project import db_get_project

from bson import ObjectId

from app.schemas.todo import Todo


async def create_project_service(
    create_project_request: CreateProjectRequest, db: AsyncDatabase
) -> CreateProjectResponse:

    project_in_db_dict = await db_create_project(create_project_request, db)

    return CreateProjectResponse(
        project=Project(
            id=project_in_db_dict["_id"],
            name=project_in_db_dict["name"],
            description=project_in_db_dict["description"],
            todo_statuses=[
                TodoStatus(id=str(ObjectId()), name="To Do"),
                TodoStatus(id=str(ObjectId()), name="In Progress"),
                TodoStatus(id=str(ObjectId()), name="Done"),
            ],
            todo_ids=[],
        )
    )


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
