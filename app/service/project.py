from typing import List
from fastapi import HTTPException
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
    Todo,
    UpdateTodoStatusRequest,
    UpdateTodoStatusResponse,
)
from app.db.project import (
    db_add_todo,
    db_add_todo_status,
    db_approve_todo,
    db_assign_todo,
    db_delete_todo,
    db_delete_todo_status,
    db_get_team_by_project_id,
    db_get_todo_items,
    db_reorder_todo_items,
    db_reorder_todo_statuses,
    db_update_budget_available,
    db_update_budget_spent,
    db_update_todo,
    db_update_todo_statuses,
)
from app.db.project import db_get_project


async def get_project_service(project_id: str, db: AsyncDatabase) -> GetProjectResponse:

    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    return GetProjectResponse(
        project=Project(
            id=project_in_db_dict["_id"],
            name=project_in_db_dict["name"],
            description=project_in_db_dict["description"],
            todo_statuses=project_in_db_dict["todo_statuses"],
            todo_ids=project_in_db_dict["todo_ids"],
            budget_available=project_in_db_dict["budget_available"],
            budget_spent=project_in_db_dict["budget_spent"],
        )
    )


# TODO: Check if user is exec or standard access
# If they are exec, the todo is auto approved, otherwise, need review
async def add_todo_service(
    project_id: str, todo_request: AddTodoRequest, user_id: str, db: AsyncDatabase
) -> AddTodoResponse:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    # Assign to the first status_id in the project if status_id is not passed in
    if todo_request.status_id is None:
        # Get the project's current statuses
        if project_in_db_dict["todo_statuses"]:
            todo_request.status_id = project_in_db_dict["todo_statuses"][0]["id"]

    # Get the team of the project to check if user is exec or not
    team_in_db_dict = await db_get_team_by_project_id(project_id, db)
    if not team_in_db_dict:
        raise HTTPException(
            status_code=404,
            detail=f"Project's team does not exist: project_id={project_id}",
        )

    await db_add_todo(
        project_id, todo_request, user_id in team_in_db_dict["exec_member_ids"], db
    )

    return AddTodoResponse()


async def update_todo_service(
    project_id: str, update_todo_request: UpdateTodoRequest, db: AsyncDatabase
) -> UpdateTodoResponse:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    # Check if status_id exists in project
    status_ids = [str(status["id"]) for status in project_in_db_dict["todo_statuses"]]
    if update_todo_request.status_id not in status_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status_id: {update_todo_request.status_id}",
        )

    await db_update_todo(project_id, update_todo_request, db)

    return UpdateTodoResponse()


async def delete_todo_service(
    project_id: str,
    delete_todo_request: DeleteTodoRequest,
    db: AsyncDatabase,
) -> DeleteTodoResponse:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    # Check if todo exists
    if delete_todo_request.todo_id not in project_in_db_dict["todo_ids"]:
        raise HTTPException(
            status_code=404,
            detail=f"Todo does not exist in project: todo_id={delete_todo_request.todo_id}, project_id={project_id}",
        )

    await db_delete_todo(project_id, delete_todo_request.todo_id, db)

    return DeleteTodoResponse()


async def get_todo_items_service(
    project_id: str, db: AsyncDatabase
) -> GetTodoItemsResponse:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    todo_items_in_db_list = await db_get_todo_items(project_id, db)

    return GetTodoItemsResponse(
        todos=[
            Todo(
                id=todo["_id"],
                name=todo["name"],
                description=todo["description"],
                status_id=todo["status_id"],
                assignee_id=todo["assignee_id"],
                approved=todo["approved"],
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
    
    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )
    
    await db_add_todo_status(project_id, todo_status_request.name, todo_status_request.color, db)

    return AddTodoStatusResponse()


async def delete_todo_status_service(
    project_id: str,
    delete_todo_status_request: DeleteTodoStatusRequest,
    db: AsyncDatabase,
) -> DeleteTodoStatusResponse:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    # Prevent deleting the last todo status in a project
    if len(project_in_db_dict["todo_statuses"]) == 1:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete the last todo status in the project: project_id={project_id}",
        )

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
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    existing_status_ids = [
        str(status["id"]) for status in project_in_db_dict["todo_statuses"]
    ]
    if sorted(new_status_ids) != sorted(existing_status_ids):
        raise HTTPException(
            status_code=400,
            detail=f"new_status_ids must contain all existing status ids exactly once: existing_status_ids={existing_status_ids}, new_status_ids={new_status_ids}",
        )

    new_statuses = sorted(
        project_in_db_dict["todo_statuses"],
        key=lambda todo_status: new_status_ids.index(str(todo_status["id"])),
    )

    await db_reorder_todo_statuses(project_id, new_statuses, db)

    return ReorderTodoStatusesResponse()


async def update_todo_status_service(
    project_id: str, update_todo_status_request: UpdateTodoStatusRequest, 
    db: AsyncDatabase
) -> UpdateTodoStatusResponse:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    # Check if status_id exists in project
    status_ids = [str(status["id"]) for status in project_in_db_dict["todo_statuses"]]
    if update_todo_status_request.status_id not in status_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status_id: {update_todo_status_request.status_id}",
        )

    # Call DB layer to update the todo status
    await db_update_todo_statuses(
        project_id,
        update_todo_status_request.status_id,
        update_todo_status_request.name,
        update_todo_status_request.color,
        db,
    )

    return UpdateTodoStatusResponse()


async def assign_todo_service(
    project_id: str,
    todo_id: str,
    assignee_id: str,
    db: AsyncDatabase,
) -> None:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    # Check if todo exists
    if todo_id not in project_in_db_dict["todo_ids"]:
        raise HTTPException(
            status_code=404,
            detail=f"Todo does not exist in project: todo_id={todo_id}, project_id={project_id}",
        )

    # Check if assignee exists in project team
    team_in_db_dict = await db_get_team_by_project_id(project_id, db)
    if not team_in_db_dict:
        raise HTTPException(
            status_code=404,
            detail=f"Project's team does not exist: project_id={project_id}",
        )

    if assignee_id not in team_in_db_dict["member_ids"]:
        raise HTTPException(
            status_code=404,
            detail=f"Assignee does not exist in project team: assignee_id={assignee_id}, project_id={project_id}",
        )

    await db_assign_todo(todo_id, assignee_id, db)


async def approve_todo_service(todo_id: str, db: AsyncDatabase) -> None:

    await db_approve_todo(todo_id, db)


async def get_proposed_todos_service(project_id: str, db: AsyncDatabase) -> List[Todo]:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    proposed_todos = [
        todo
        for todo in (await get_todo_items_service(project_id, db)).todos
        if todo.approved is False
    ]

    return proposed_todos


async def increase_budget_service(
    project_id: str, amount: float, db: AsyncDatabase
) -> None:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Amount must be positive: amount={amount}",
        )

    new_budget = project_in_db_dict["budget_available"] + amount

    await db_update_budget_available(project_id, new_budget, db)


async def spend_budget_service(
    project_id: str, amount: float, db: AsyncDatabase
) -> None:

    # Check if project exists
    project_in_db_dict = await db_get_project(project_id, db)
    if not project_in_db_dict:
        raise HTTPException(
            status_code=404, detail=f"Project does not exist: project_id={project_id}"
        )

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Amount must be positive: amount={amount}",
        )

    if amount > project_in_db_dict["budget_available"]:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient budget available: budget_available={project_in_db_dict['budget_available']}, amount={amount}",
        )

    new_budget_available = project_in_db_dict["budget_available"] - amount
    new_budget_spent = project_in_db_dict["budget_spent"] + amount

    await db_update_budget_available(project_id, new_budget_available, db)
    await db_update_budget_spent(project_id, new_budget_spent, db)
