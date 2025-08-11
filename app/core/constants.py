import os

from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 1 # TODO: Change to 30 (minutes)
REFRESH_TOKEN_EXPIRE_HOURS = 48

USERS_COLLECTION = "users"
TEAMS_COLLECTION = "teams"
KANBANS_COLLECTION = "kanbans"
