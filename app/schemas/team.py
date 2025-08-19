from typing import List

from pydantic import BaseModel


class TeamModel(BaseModel):
    id: str
    name: str
    member_ids: List[str]
    exec_member_ids: List[str]
    kanban_ids: List[str] = []


class TeamCreateReq(BaseModel):
    name: str


class KickTeamMemberReq(BaseModel):
    member_id: str


class PromoteTeamMemberReq(BaseModel):
    member_id: str
