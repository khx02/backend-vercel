from pydantic import BaseModel


class Event(BaseModel):
    id: str
    name: str
    description: str


# Pass event_id through path
class GetEventRequest(BaseModel):
    pass


class GetEventResponse(BaseModel):
    event: Event
