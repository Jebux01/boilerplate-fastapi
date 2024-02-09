"""
App end-points
"""

from fastapi import APIRouter, Response
from app.db import select, exec_query
from sqlalchemy import text

router = APIRouter()


@router.get("/healthcheck", tags=["Healthcheck"])
def healthcheck():
    """
    Health check end-point
    """
    return Response(content="OK")


@router.get("/healthcheck-db", tags=["Healthcheck"])
def healthcheck_db():
    """
    Health check database end-point
    """
    result = exec_query(text("SELECT NOW() AS now;"))
    return result
