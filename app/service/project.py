from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.project import CreateProjectRequest


async def create_project_service(
    create_project_request: CreateProjectRequest, db: AsyncDatabase
) -> CreateProjectResponse:

    project_in_db_dict = await db_create_project()
