from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.project import (
    AddTodoRequest,
    AddTodoResponse,
    AddTodoStatusRequest,
    AddTodoStatusResponse,
    DeleteTodoRequest,
    DeleteTodoResponse,
    DeleteTodoStatusRequest,
    DeleteTodoStatusResponse,
    GetProjectResponse,
    GetTodoItemsResponse,
    Project,
    ReorderTodoItemsRequest,
    ReorderTodoItemsResponse,
    ReorderTodoStatusesRequest,
    ReorderTodoStatusesResponse,
    UpdateTodoRequest,
    UpdateTodoResponse,
)
from app.db.project import (
    db_add_todo,
    db_add_todo_status,
    db_delete_todo,
    db_delete_todo_status,
    db_get_todo_items,
    db_reorder_todo_items,
    db_reorder_todo_statuses,
    db_update_todo,
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


async def update_todo_service(
    project_id: str, update_todo_request: UpdateTodoRequest, db: AsyncDatabase
) -> UpdateTodoResponse:

    await db_update_todo(project_id, update_todo_request, db)

    return UpdateTodoResponse()


async def delete_todo_service(
    project_id: str,
    delete_todo_request: DeleteTodoRequest,
    db: AsyncDatabase,
) -> DeleteTodoResponse:

    await db_delete_todo(project_id, delete_todo_request.todo_id, db)

    return DeleteTodoResponse()


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
                owner_id=todo["owner_id"],
            )
            for todo in todo_items_in_db_list
        ]
    )


async def reorder_todo_items_service(
    project_id: str,
    reorder_todo_items_request: ReorderTodoItemsRequest,
    db: AsyncDatabase,
) -> ReorderTodoItemsResponse:

    new_todo_ids = reorder_todo_items_request.new_todo_ids

    # Get the project's current todos
    project_in_db_dict = await db_get_project(project_id, db)

    new_todos = sorted(
        project_in_db_dict["todos"],
        key=lambda todo: new_todo_ids.index(str(todo["id"])),
    )

    await db_reorder_todo_items(project_id, new_todos, db)

    return ReorderTodoItemsResponse()


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


async def reorder_todo_statuses_service(
    project_id: str,
    reorder_todo_statuses_request: ReorderTodoStatusesRequest,
    db: AsyncDatabase,
) -> ReorderTodoStatusesResponse:

    new_status_ids = reorder_todo_statuses_request.new_status_ids

    # Get the project's current statuses
    project_in_db_dict = await db_get_project(project_id, db)

    new_statuses = sorted(
        project_in_db_dict["todo_statuses"],
        key=lambda todo_status: new_status_ids.index(str(todo_status["id"])),
    )

    await db_reorder_todo_statuses(project_id, new_statuses, db)

    return ReorderTodoStatusesResponse()
