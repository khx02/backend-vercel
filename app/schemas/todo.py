from pydantic import BaseModel


class Todo(BaseModel):
    id: str
    name: str
    description: str
    status_id: str
    assignee_id: str | None = None
