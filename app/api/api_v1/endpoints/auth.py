"""Module with the endpoint for Auth section"""

from typing import Annotated, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.db import select, exec_query
from app.schemas.users import UserTokenData
from app.utils.oauth import (
    create_access_token,
    verify_password,
    get_current_active_user,
)

router = APIRouter()


ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


class ExceptionLogin(Exception):
    """Custom Exception"""


@router.post("/login", status_code=status.HTTP_200_OK)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login function"""
    query, table = select(
        table_name="users",  # type: ignore
        columns=[
            "username",
            "password",
        ],
        schema="test",
    )

    query = query.where(table.c.username == form_data.username)

    user_db = exec_query(query)

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_password(
        plain_password=form_data.password,
        hashed_password=user_db["password"],  # type: ignore
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    access_token: str = create_access_token(UserTokenData(**user_db).model_dump())  # type: ignore

    return {
        "status": "success",
        "access_token": access_token,
    }


@router.get("/users/me/")
async def read_users_me(
    current_user: Annotated[UserTokenData, Depends(get_current_active_user)]
):
    return current_user
