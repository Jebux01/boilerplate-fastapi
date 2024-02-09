"""Module with the endpoints for users section"""

from typing import Annotated, Dict

from fastapi import APIRouter, HTTPException, status
from app.db import delete, insert, select, exec_query, update
from app.schemas.users import CreateUser, UpdateUser
from app.utils.oauth import get_password_hash

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUser):
    """
    Create user

    Args:
        user (CreateUser): User data

    Returns:
        Dict: Response
    """

    query, _ = insert(table_name="users", schema="test")  # type: ignore
    query = query.values(
        password=get_password_hash(user.password),
        username=user.username,
    )

    result = exec_query(query)
    return result


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_user_by(id: int):
    """
    Create user

    Args:
        user (CreateUser): User data

    Returns:
        Dict: Response
    """

    query, table = select(
        table_name="users",  # type: ignore
        columns=[
            "username",
            "password",
        ],
        schema="test",
    )

    query = query.where(table.c.id == id)

    result = exec_query(query)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return result


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_user(id: int, user: UpdateUser):
    """
    update user

    Args:
        user (UpdateUser): User data

    Returns:
        Dict: Response
    """

    query, table = update(
        table_name="users",  # type: ignore
        schema="test",
    )

    hash_password = get_password_hash(user.password)
    user.password = hash_password
    query = query.where(table.c.id == id).values(**user.model_dump())

    result = exec_query(query)
    return result


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_user(id: int):
    """
    Create user

    Args:
        user (CreateUser): User data

    Returns:
        Dict: Response
    """

    query, table = delete(table_name="users", schema="test")  # type: ignore
    query = query.where(table.c.id == id)
    result = exec_query(query)
    return result
