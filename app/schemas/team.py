from pydantic import BaseModel


class TeamModel(BaseModel):
    id: str
    name: str
    member_ids: list[str]
