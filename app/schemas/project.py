from pydantic import BaseModel

from typing import List


class TodoStatus(BaseModel):
    id: str
    name: str
    color: str


class Todo(BaseModel):
    id: str
    name: str
    description: str
    status_id: str
    assignee_id: str | None = None
    approved: bool = False


class Project(BaseModel):
    id: str
    name: str
    description: str
    todo_statuses: List[TodoStatus]
    todo_ids: List[str]
    budget_available: float = 0
    budget_spent: float = 0


# Will pass project_id through path
class GetProjectRequest(BaseModel):
    pass


class GetProjectResponse(BaseModel):
    project: Project


# Will pass project_id through path
class AddTodoRequest(BaseModel):
    name: str
    description: str
    status_id: str | None = None
    assignee_id: str | None = None


class AddTodoResponse(BaseModel):
    pass


# Will pass project_id through path
class UpdateTodoRequest(BaseModel):
    todo_id: str
    name: str
    description: str
    status_id: str
    assignee_id: str


class UpdateTodoResponse(BaseModel):
    pass


# Will pass project_id through path
# May be worth considering just using the path for the todo_id as well
class DeleteTodoRequest(BaseModel):
    todo_id: str


class DeleteTodoResponse(BaseModel):
    pass


# Will pass project_id through path
class GetTodoItemsRequest(BaseModel):
    pass


class GetTodoItemsResponse(BaseModel):
    todos: List[Todo]


class ReorderTodoItemsRequest(BaseModel):
    new_todo_ids: List[str]


class ReorderTodoItemsResponse(BaseModel):
    pass


# Will pass project_id through path
# Will add the todo status as the last status
class AddTodoStatusRequest(BaseModel):
    name: str
    color: str

class AddTodoStatusResponse(BaseModel):
    pass


# Will pass project_id through path
# May be able to pass status id through path as well
class DeleteTodoStatusRequest(BaseModel):
    status_id: str


class DeleteTodoStatusResponse(BaseModel):
    pass


# Will pass project_id through path
class ReorderTodoStatusesRequest(BaseModel):
    new_status_ids: List[str]


class ReorderTodoStatusesResponse(BaseModel):
    pass


class UpdateTodoStatusRequest(BaseModel):
    status_id: str
    name: str
    color: str


class UpdateTodoStatusResponse(BaseModel):
    pass


class AssignTodoRequest(BaseModel):
    todo_id: str
    assignee_id: str


class AssignTodoResponse(BaseModel):
    pass


class ApproveTodoRequest(BaseModel):
    pass


class ApproveTodoResponse(BaseModel):
    pass


class GetProposedTodosRequest(BaseModel):
    pass


class GetProposedTodosResponse(BaseModel):
    proposed_todos: List[Todo]


class IncreaseBudgetRequest(BaseModel):
    amount: float


class IncreaseBudgetResponse(BaseModel):
    pass


class SpendBudgetRequest(BaseModel):
    amount: float


class SpendBudgetResponse(BaseModel):
    pass
