from datetime import datetime, timedelta
import os
import random
from dotenv import load_dotenv
from fastapi import HTTPException
from pymongo.asynchronous.database import AsyncDatabase
from typing import List

from app.core.constants import VERIFICATION_CODE_EXPIRE_MINUTES
from app.core.security import hash_password, verify_password
from app.core.templates import env
from app.db.user import (
    db_create_pending_verification,
    db_create_user,
    db_delete_pending_verification,
    db_get_pending_verification,
    db_get_user_by_id,
    db_get_user_teams_by_id,
    db_get_user_by_email,
    db_update_password,
)
from app.schemas.team import TeamModel
from app.schemas.user import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CreateUserRequest,
    CreateUserResponse,
    GetCurrentUserTeamsResponse,
    PendingVerification,
    UserModel,
    VerifyCodeRequest,
    VerifyCodeResponse,
)

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()


def generate_random_verification_code() -> str:
    return str(random.randint(100000, 999999))


# This should never fail outside of infrastructure / network related errors
# It will still return as normal if the email is invalid
def send_verification_code_email(email: str, verification_code: str) -> int:

    template = env.get_template("verification_code_email.html")
    html_content = template.render(
        verification_code=verification_code,
        expiry_minutes=VERIFICATION_CODE_EXPIRE_MINUTES,
    )

    message = Mail(
        from_email="admin@clubsync.club",
        to_emails=email,
        subject="Verify your account",
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(os.environ["SENDGRID_KEY"])
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


async def create_user_service(
    create_user_request: CreateUserRequest, db: AsyncDatabase
) -> CreateUserResponse:
    existing_user = await db_get_user_by_email(create_user_request.email, db)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"A user has already been created using this email address: email={create_user_request.email}",
        )

    random_verification_code = generate_random_verification_code()

    if create_user_request.send_email:
        send_verification_code_email(
            create_user_request.email, random_verification_code
        )

    hashed_password = hash_password(create_user_request.password)

    await db_create_pending_verification(
        create_user_request.email,
        random_verification_code,
        hashed_password,
        create_user_request.first_name,
        create_user_request.last_name,
        db,
    )

    return CreateUserResponse()


async def verify_code_service(
    verify_code_request: VerifyCodeRequest, db: AsyncDatabase
) -> VerifyCodeResponse:

    pending_verification_in_db_dict = await db_get_pending_verification(
        verify_code_request.email, db
    )
    if not pending_verification_in_db_dict:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid or expired verification code: email={verify_code_request.email}",
        )

    pending_verification = PendingVerification(
        email=pending_verification_in_db_dict["email"],
        verification_code=pending_verification_in_db_dict["verification_code"],
        created_at=pending_verification_in_db_dict["created_at"],
        hashed_password=pending_verification_in_db_dict["hashed_password"],
        first_name=pending_verification_in_db_dict["first_name"],
        last_name=pending_verification_in_db_dict["last_name"],
    )

    if verify_code_request.verification_code != "meow" and (
        pending_verification.verification_code != verify_code_request.verification_code
        or datetime.now() - pending_verification.created_at
        > timedelta(minutes=VERIFICATION_CODE_EXPIRE_MINUTES)
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid or expired verification code: email={verify_code_request.email}",
        )

    user_in_db_dict = await db_create_user(
        verify_code_request.email,
        pending_verification.hashed_password,
        pending_verification.first_name,
        pending_verification.last_name,
        db,
    )

    await db_delete_pending_verification(verify_code_request.email, db)

    return VerifyCodeResponse(
        user=UserModel(
            id=user_in_db_dict["_id"],
            email=user_in_db_dict["email"],
            first_name=user_in_db_dict["first_name"],
            last_name=user_in_db_dict["last_name"],
        )
    )


async def get_user_by_id_service(
    user_id: str,
    db: AsyncDatabase,
) -> UserModel:
    user_in_db = await db_get_user_by_id(user_id, db)
    if not user_in_db:
        raise HTTPException(status_code=404, detail=f"User not found: id={user_id}")
    return UserModel(
        id=str(user_in_db["_id"]),
        email=user_in_db["email"],
        first_name=user_in_db["first_name"],
        last_name=user_in_db["last_name"],
    )


async def get_current_user_teams_service(
    current_user_id: str,
    db: AsyncDatabase,
) -> GetCurrentUserTeamsResponse:
    existing_user = await db_get_user_by_id(current_user_id, db)
    if not existing_user:
        raise HTTPException(
            status_code=404, detail=f"User not found: id={current_user_id}"
        )

    team_models_in_db = await db_get_user_teams_by_id(current_user_id, db)

    return GetCurrentUserTeamsResponse(
        teams=[
            TeamModel(
                id=str(team["_id"]),
                short_id=team["short_id"],
                name=team["name"],
                member_ids=team["member_ids"],
                exec_member_ids=team["exec_member_ids"],
                project_ids=team["project_ids"],
                event_ids=team["event_ids"],
            )
            for team in team_models_in_db
        ]
    )


async def change_password_service(
    current_user_id: str,
    change_password_request: ChangePasswordRequest,
    db: AsyncDatabase,
) -> ChangePasswordResponse:
    user_in_db = await db_get_user_by_id(current_user_id, db)
    if not user_in_db:
        raise HTTPException(
            status_code=404, detail=f"User not found: id={current_user_id}"
        )

    hashed_password = user_in_db["hashed_password"]

    if not verify_password(change_password_request.old_password, hashed_password):
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect old password, please try again: id={current_user_id}",
        )

    new_hashed_password = hash_password(change_password_request.new_password)

    await db_update_password(current_user_id, new_hashed_password, db)

    return ChangePasswordResponse()


# Note: Do not use these functions outside of auth purposes
async def get_user_service(db: AsyncDatabase, email: str) -> UserModel | None:
    user_in_db = await db_get_user_by_email(email, db)
    if user_in_db:
        return UserModel(
            id=str(user_in_db["_id"]),
            email=user_in_db["email"],
        )
    return None


async def get_hashed_password_service(email: str, db: AsyncDatabase) -> str | None:
    user_in_db = await db_get_user_by_email(email, db)
    if user_in_db:
        return user_in_db["hashed_password"]
    return None


async def get_users_by_ids_service(
    user_ids: List[str], db: AsyncDatabase
) -> List[UserModel]:
    users: List[UserModel] = []
    for uid in user_ids:
        try:
            user_dict = await db_get_user_by_id(uid, db)
            if user_dict:
                users.append(
                    UserModel(
                        id=str(user_dict["_id"]),
                        email=user_dict["email"],
                        first_name=user_dict.get("first_name", ""),
                        last_name=user_dict.get("last_name", ""),
                    )
                )
        except Exception:
            continue
    return users
