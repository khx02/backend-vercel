from typing import List

from pydantic import BaseModel

from app.schemas.project import Project


class TeamModel(BaseModel):
    id: str
    name: str
    member_ids: List[str]
    exec_member_ids: List[str]
    kanban_ids: List[str] = []
    project_ids: List[str] = []


class TeamCreateReq(BaseModel):
    name: str


class GetTeamRequest(BaseModel):
    pass


class GetTeamResponse(BaseModel):
    team: TeamModel


class KickTeamMemberReq(BaseModel):
    member_id: str


class PromoteTeamMemberReq(BaseModel):
    member_id: str


class CreateProjectRequest(BaseModel):
    name: str
    description: str


class CreateProjectResponse(BaseModel):
    project: Project
