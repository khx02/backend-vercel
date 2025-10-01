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
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import ALGORITHM, SECRET_KEY
from app.core.security import create_token_pair, verify_password
from app.db.client import get_db
from app.schemas.token import TokenRes, UserRes
from app.schemas.user import UserModel
from app.service.user import get_hashed_password_service, get_user_service

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
        samesite="none",
        secure=True,
        max_age=60 * 15,  # 60 sec * 15
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="none",
        secure=True,
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
async def get_current_user_info(
    db: AsyncDatabase = Depends(get_db),
    cookie: Annotated[Optional[str], Cookie(alias="access_token")] = None,
    access_token: Annotated[Optional[str], Depends(oauth2_scheme)] = None,
) -> UserModel:
    try:
        cookie_user = await get_current_user_info_from_cookie(cookie, db)
        return cookie_user
    except Exception as cookie_e:
        try:
            token_user = await get_current_user_info_from_token(access_token, db)
            return token_user
        except Exception as token_e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Cookie: {cookie_e}, Token: {token_e}",
            )


# Cookie-based dependency for /me
async def get_current_user_info_from_cookie(
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

    user = await get_user_service(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


# Dev only function as tokens should never be returned to production users
async def get_current_user_info_from_token(
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
    user = await get_user_service(db, email)
    if not user:
        raise cred_exc
    return user


async def authenticate_user(db: AsyncDatabase, email: str, password: str) -> UserModel:
    user = await get_user_service(db, email)
    hashed_password = await get_hashed_password_service(email, db)
    if (
        user is None
        or hashed_password is None
        or not verify_password(password, hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
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


@router.post("/refresh-token", response_model=TokenRes)
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

    user = await get_user_service(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
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
    current_user: UserModel = Depends(get_current_user_info),
) -> UserRes:
    return UserRes(email=current_user.email)


@router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"ok": True}
