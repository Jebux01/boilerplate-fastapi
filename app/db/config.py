"""
This module is responsible for the configuration of the database connection.
"""

from logging import Logger, getLogger
from sqlalchemy import URL, create_engine, Engine

from app.config import settings

logger: Logger = getLogger(__name__)


def build_url(drivername: str = "mssql+pyodbc") -> URL:
    """
    Build the URL for the connection
    
    Args:
        drivername (str, optional): Driver name. Defaults to "mssql+pyodbc".

    Returns:
        URL: URL for the connection
    """
    return URL.create(
        drivername=drivername,
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        database=settings.DB_SCHEMA,
    )


def engine() -> Engine:
    """Decorator for insert the engine"""
    # connection_string_mssql = f"mssql+pyodbc://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_SCHEMA}?driver=ODBC+Driver+17+for+SQL+Server"
    return create_engine(build_url(drivername="postgresql"))


ENGINE = engine()
