from pydantic import BaseModel


class Todo(BaseModel):
    id: str
    name: str
    description: str
    status_id: str
    owner_id: str
