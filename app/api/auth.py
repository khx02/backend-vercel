# app/api/auth.py
from typing import Annotated, Optional

import jwt
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, utils
from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import ALGORITHM, SECRET_KEY
from app.core.security import create_token_pair, verify_password
from app.db.client import get_db
from app.db.user import db_get_user_or_none_by_email
from app.schemas.token import TokenRes, UserRes
from app.schemas.user import UserModel

TOKEN_URL = "/api/auth/set-token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL, auto_error=False)
router = APIRouter()


# ---------- helpers ----------
def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    # NOTE: For local dev, secure=False is fine. In prod use secure=True and SameSite="none".
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 15,  # 60 sec * 15
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 14,  # 14 days
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        "access_token", path="/", httponly=True, samesite="lax", secure=False
    )
    response.delete_cookie(
        "refresh_token", path="/", httponly=True, samesite="lax", secure=False
    )


# ---------- shared deps ----------
# This basically runs both the token and the cookie one, prioritising the cookie one
async def get_current_user(
    db: AsyncDatabase = Depends(get_db),
    cookie: Annotated[Optional[str], Cookie(alias="access_token")] = None,
    access_token: Annotated[Optional[str], Depends(oauth2_scheme)] = None,
) -> UserModel:
    try:
        cookie_user = await get_current_user_from_cookie(cookie, db)
        return cookie_user
    except Exception as cookie_e:
        try:
            token_user = await get_current_user_from_token(access_token, db)
            return token_user
        except Exception as token_e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Cookie: {cookie_e}, Token: {token_e}",
            )


# Cookie-based dependency for /me
async def get_current_user_from_cookie(
    cookie: Annotated[Optional[str], Cookie(alias="access_token")] = None,
    db: AsyncDatabase = Depends(get_db),
) -> UserModel:
    if not cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        payload = jwt.decode(cookie, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user_dict_in_db = await db_get_user_or_none_by_email(email, db)
    if not user_dict_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return UserModel(
        id=str(user_dict_in_db["_id"]),
        email=user_dict_in_db["email"],
    )


# Dev only function as tokens should never be returned to production users
async def get_current_user_from_token(
    access_token: Optional[str],
    db: Annotated[AsyncDatabase, Depends(get_db)],
) -> UserModel:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not access_token:
        raise cred_exc
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise cred_exc
    except jwt.InvalidTokenError:
        raise cred_exc
    user_in_db_dict = await db_get_user_or_none_by_email(email, db)
    if not user_in_db_dict:
        raise cred_exc
    return UserModel(
        id=str(user_in_db_dict["_id"]),
        email=user_in_db_dict["email"],
    )


async def authenticate_user(db: AsyncDatabase, email: str, password: str) -> UserModel:
    user_in_db_dict = await db_get_user_or_none_by_email(email, db)
    if user_in_db_dict is None or not verify_password(
        password, user_in_db_dict["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserModel(
        id=str(user_in_db_dict["_id"]),
        email=user_in_db_dict["email"],
    )
    return user


# ---------- endpoints ----------
@router.post("/set-token", response_model=TokenRes)
async def login_for_token_access(
    response: Response,  # <-- add response
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncDatabase = Depends(get_db),
) -> TokenRes:
    user = await authenticate_user(db, form_data.username, form_data.password)
    token_pair = create_token_pair(data={"sub": user.email})

    # set cookies for browser session
    set_auth_cookies(response, token_pair.access_token, token_pair.refresh_token)

    # still return body (handy for non-browser clients / testing)
    return TokenRes(
        user=UserRes(email=user.email),
        access_token=token_pair.access_token,
    )


@router.post("/refresh_token", response_model=TokenRes)
async def refresh_token(
    response: Response,
    refresh_token_cookie: Optional[str] = Cookie(alias="refresh_token"),
    db: AsyncDatabase = Depends(get_db),
) -> TokenRes:

    if not refresh_token_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token"
        )

    try:
        payload = jwt.decode(refresh_token_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user_in_db_dict = await db_get_user_or_none_by_email(email, db)
    if user_in_db_dict is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    user = UserModel(
        id=str(user_in_db_dict["_id"]),
        email=user_in_db_dict["email"],
    )

    token_pair = create_token_pair(data={"sub": user.email})

    # rotate cookies
    set_auth_cookies(response, token_pair.access_token, token_pair.refresh_token)

    return TokenRes(
        user=UserRes(email=user.email),
        access_token=token_pair.access_token,
    )


@router.get("/me", response_model=UserRes)
async def read_me(
    current_user: UserModel = Depends(get_current_user),
) -> UserRes:
    return UserRes(email=current_user.email)


@router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"ok": True}
