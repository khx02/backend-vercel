import asyncio
import logging
from fastapi import APIRouter, FastAPI, Request, HTTPException, status
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


from app.api.auth import router as auth_router
from app.api.team import router as team_router
from app.api.user import router as user_router
from app.api.project import router as project_router
from app.api.event import router as event_router
from app.core.scheduler import scheduler


class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout: float = 10.0):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Request timed out"
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(lifespan=lifespan)

# Middleware for timing out requests which take too long
app.add_middleware(TimeoutMiddleware, timeout=10.0)

# Middleware for handling CORS
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for logging requests and responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    method = request.method
    path = request.url.path

    query = dict(request.query_params)

    logger.info(f"Incoming request: {method} {path} | Query: {query}")

    try:
        body = await request.json()
        logger.info(f"Body: {body}")
    except Exception:
        pass

    response = await call_next(request)

    logger.info(f"Completed {method} {path} -> {response.status_code}")

    return response


api_router = APIRouter(prefix="/api")

api_router.include_router(user_router, prefix="/users")
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(team_router, prefix="/teams")
api_router.include_router(project_router, prefix="/projects")
api_router.include_router(event_router, prefix="/events")

app.include_router(api_router)
