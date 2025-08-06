from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter
from pymongo.asynchronous.database import AsyncDatabase
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone

import jwt

from app.schemas.token import TokenData, TokenRes
from app.schemas.user import UserModel, UserRes
from app.db.client import get_db
from app.service.user import get_user_service
from app.core.constants import SECRET_KEY, ALGORITHM
from app.core.security import create_token_pair, verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncDatabase, Depends(get_db)],
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(token)
    print("TRYING TO GET USER")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.InvalidTokenError:
        print("CRED EXCEPTION")
        raise credentials_exception
    user = await get_user_service(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


# OAuth2 uses username and password for authentication, for our purposes, assume the email is the username
async def authenticate_user(db: AsyncDatabase, email: str, password: str) -> UserModel:
    user = await get_user_service(db, email=email)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/token", response_model=TokenRes)
async def login_for_token_access(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncDatabase = Depends(get_db),
) -> TokenRes:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_pair = create_token_pair(data={"sub": user.email})
    return TokenRes(
        token=token_pair,
        user=UserRes(email=user.email),
        access_token=token_pair.access_token,
    )
