"""Module that container all routers base"""
from fastapi import APIRouter, status

from app.api.api_v1.endpoints import auth, users
api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)