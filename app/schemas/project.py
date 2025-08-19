from pydantic import BaseModel

from typing import List


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


# Will pass project_id through path
class GetProjectRequest(BaseModel):
    pass


# Will pass project_id through path
class GetTodoItemsForProjectRequest(BaseModel):
    pass


# Will pass project_id through path
# May be able to pass the name straight into the path?
class AddTodoStatusRequest(BaseModel):
    name: str


# Will pass project_id through path
# May be able to pass status id through path as well
class DeleteTodoStatusRequest(BaseModel):
    todo_status_id: str


# Will pass project_id through path
class ReorderTodoStatusRequest(BaseModel):
    new_todo_statuses: List[str]


# Will pass project_id through path
class AddTodoRequest(BaseModel):
    name: str
    description: str
    todo_status_id: str


# Will pass project_id through path
# May be worth considering just using the path for the todo_id as well
class DeleteTodoRequest(BaseModel):
    todo_id: str
