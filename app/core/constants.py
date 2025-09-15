import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:5137/"

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 48
VERIFICATION_CODE_EXPIRE_MINUTES = 15

USERS_COLLECTION = "users"
TEAMS_COLLECTION = "teams"
KANBANS_COLLECTION = "kanbans"
PROJECTS_COLLECTION = "projects"
TODOS_COLLECTION = "todos"
EVENTS_COLLECTION = "events"
VERIFICATION_CODES_COLLECTION = "verification_codes"
RSVPS_COLLECTION = "rsvps"
