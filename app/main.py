from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.kanban import router as kanban_router
from app.api.team import router as team_router
from app.api.user import router as user_router

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")
app.include_router(team_router, prefix="/teams")
app.include_router(kanban_router, prefix="/kanbans")
