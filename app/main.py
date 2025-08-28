from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.team import router as team_router
from app.api.user import router as user_router
from app.api.project import router as project_router
from app.api.event import router as event_router

app = FastAPI()

# TODO: Add middleware to globally handle errors

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

api_router.include_router(user_router, prefix="/users")
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(team_router, prefix="/teams")
api_router.include_router(project_router, prefix="/projects")
api_router.include_router(event_router, prefix="/events")

app.include_router(api_router)
