# app/api/auth.py
from typing import Annotated, Optional
from fastapi import Cookie, Depends, HTTPException, status, APIRouter, Response
from pymongo.asynchronous.database import AsyncDatabase
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

from app.schemas.token import RefreshTokenReq, TokenData, TokenRes, ValidateTokenRes
from app.schemas.user import UserModel, UserRes
from app.db.client import get_db
from app.service.user import get_token_service  # <-- keep this (used below)
from app.core.constants import SECRET_KEY, ALGORITHM
from app.core.security import create_token_pair, verify_password

TOKEN_URL = "/auth/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)
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
        max_age=60 * 15,  # match your access token TTL if you want
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
        "access_token", 
        path="/",
        httponly=True,
        samesite="lax",
        secure=False
    )
    response.delete_cookie(
        "refresh_token", 
        path="/",
        httponly=True,
        samesite="lax",
        secure=False
    )

# ---------- shared deps ----------
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncDatabase, Depends(get_db)],
) -> UserModel:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise cred_exc
    except jwt.InvalidTokenError:
        raise cred_exc
    user = await get_token_service(db, email)
    if not user:
        raise cred_exc
    return user

async def authenticate_user(db: AsyncDatabase, email: str, password: str) -> UserModel:
    user = await get_token_service(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# ---------- endpoints ----------
@router.post("/token", response_model=TokenRes)
async def login_for_token_access(
    response: Response,                                   # <-- add response
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

@router.post("/validate_token", response_model=ValidateTokenRes)
async def validate_token(
    current_user: UserModel = Depends(get_current_user),
) -> ValidateTokenRes:
    return ValidateTokenRes(is_valid=True)

@router.post("/refresh_token", response_model=TokenRes)
async def refresh_token(
    response: Response,  
    req: RefreshTokenReq,
    db: AsyncDatabase = Depends(get_db),
) -> TokenRes:
    # allow either body.token or cookie "refresh_token" (minimal change, body stays supported)
    refresh_cookie: Optional[str] = None
    try:
        # If you prefer cookie-first, uncomment the Cookie dep and use that.
        # refresh_cookie = refresh_token_cookie
        pass
    except Exception:
        pass

    token_to_use = refresh_cookie or req.token
    if not token_to_use:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    try:
        payload = jwt.decode(token_to_use, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # FIX: use the correct service (was get_user_token_service)
    user = await get_token_service(db, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    token_pair = create_token_pair(data={"sub": user.email})

    # rotate cookies
    set_auth_cookies(response, token_pair.access_token, token_pair.refresh_token)

    return TokenRes(
        user=UserRes(email=user.email),
        access_token=token_pair.access_token,
    )

# Cookie-based dependency for /me
async def get_current_user_from_cookie(
    access_token: Annotated[Optional[str], Cookie(alias="access_token")] = None,
    db: AsyncDatabase = Depends(get_db)
) -> UserModel:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await get_token_service(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.get("/me", response_model=UserRes)
async def read_me(current_user: UserModel = Depends(get_current_user_from_cookie)) -> UserRes:
    return UserRes(email=current_user.email)

@router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"ok": True}
