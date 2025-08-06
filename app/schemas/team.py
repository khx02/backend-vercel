from pydantic import BaseModel
from typing import List


# TODO: add exec_member_ids to track executive members
class TeamModel(BaseModel):
    id: str
    name: str
    member_ids: List[str]


class TeamCreateReq(BaseModel):
    name: str


class TeamJoinReq(BaseModel):
    team_id: str
