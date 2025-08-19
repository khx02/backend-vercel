from pydantic import BaseModel

from typing import List

from app.schemas.todo import Todo


class TodoStatus(BaseModel):
    id: str
    name: str


# TODO: Handle todo statuses
class Project(BaseModel):
    id: str
    name: str
    description: str
    todo_statuses: List[TodoStatus]
    todo_ids: List[str]


class CreateProjectRequest(BaseModel):
    name: str
    description: str


class CreateProjectResponse(BaseModel):
    project: Project


# Will pass project_id through path
class GetProjectRequest(BaseModel):
    pass


class GetProjectResponse(BaseModel):
    project: Project


# Will pass project_id through path
class GetTodoItemsRequest(BaseModel):
    pass


class GetTodoItemsResponse(BaseModel):
    todos: List[Todo]


# Will pass project_id through path
# May be able to pass the name straight into the path?
class AddTodoStatusRequest(BaseModel):
    name: str


class AddTodoStatusResponse(BaseModel):
    pass


# Will pass project_id through path
# May be able to pass status id through path as well
class DeleteTodoStatusRequest(BaseModel):
    todo_status_id: str


class DeleteTodoStatusResponse(BaseModel):
    pass


# Will pass project_id through path
class ReorderTodoStatusRequest(BaseModel):
    new_todo_statuses: List[str]


class ReorderTodoStatusResponse(BaseModel):
    pass


# Will pass project_id through path
class AddTodoRequest(BaseModel):
    name: str
    description: str
    todo_status_id: str


class AddTodoResponse(BaseModel):
    pass


# Will pass project_id through path
# May be worth considering just using the path for the todo_id as well
class DeleteTodoRequest(BaseModel):
    todo_id: str


class DeleteTodoResponse(BaseModel):
    pass
