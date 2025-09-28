from typing import List

from pydantic import BaseModel

from app.schemas.project import Project
from app.schemas.event import Event


class TeamModel(BaseModel):
    id: str
    short_id: str  # 6 char lower alpha short id
    name: str
    member_ids: List[str]
    exec_member_ids: List[str]
    project_ids: List[str]
    event_ids: List[str]


class CreateTeamRequest(BaseModel):
    name: str


class CreateTeamResponse(BaseModel):
    team: TeamModel


class JoinTeamRequest(BaseModel):
    user_id: str


class JoinTeamResponse(BaseModel):
    pass


class JoinTeamByShortIdRequest(BaseModel):
    pass


class JoinTeamByShortIdResponse(BaseModel):
    pass


class GetTeamRequest(BaseModel):
    pass


class GetTeamResponse(BaseModel):
    team: TeamModel


class PromoteTeamMemberRequest(BaseModel):
    member_id: str


class PromoteTeamMemberResponse(BaseModel):
    pass


class LeaveTeamRequest(BaseModel):
    pass


class LeaveTeamResponse(BaseModel):
    pass


class DeleteTeamRequest(BaseModel):
    pass


class DeleteTeamResponse(BaseModel):
    pass


class KickTeamMemberRequest(BaseModel):
    member_id: str


class KickTeamMemberResponse(BaseModel):
    pass


class CreateProjectRequest(BaseModel):
    name: str
    description: str


class CreateProjectResponse(BaseModel):
    project: Project


class DeleteProjectRequest(BaseModel):
    project_id: str


class DeleteProjectResponse(BaseModel):
    pass


class CreateEventRequest(BaseModel):
    name: str
    description: str
    start: str
    end: str
    colour: str
    location: str


class CreateEventResponse(BaseModel):
    event: Event


class DeleteEventRequest(BaseModel):
    event_id: str


class DeleteEventResponse(BaseModel):
    pass


class GetTeamEventsRequest(BaseModel):
    pass


class GetTeamEventsResponse(BaseModel):
    events: List[Event]
