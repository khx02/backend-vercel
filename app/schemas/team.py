from pydantic import BaseModel
from typing import List


class TeamModel(BaseModel):
    id: str
    name: str
    member_ids: List[str]
    exec_member_ids: List[str]
    kanban_ids: List[str] = []


class TeamCreateReq(BaseModel):
    name: str
