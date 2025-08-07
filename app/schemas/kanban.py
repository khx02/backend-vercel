from pydantic import BaseModel
from typing import List


class KanbanItem(BaseModel):
    id: str
    name: str
    start_at: float
    end_at: float
    column: int
    owner: str


class KanbanModel(BaseModel):
    id: str
    name: str
    kanban_elements: List[KanbanItem] = []


class KanbanCreateReq(BaseModel):
    name: str
    team_id: str


class AddKanbanItemReq(BaseModel):
    kanban_item: KanbanItem
    kanban_id: str
