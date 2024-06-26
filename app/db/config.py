"""
This module is responsible for the configuration of the database connection.
"""

from logging import Logger, getLogger
import os
from typing import MutableMapping

from sqlalchemy import (
    Engine,
    URL,
    create_engine,
    create_mock_engine,
    engine as engine_sqlalchemy,
)

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


def dump(sql):
    """
    Print SQL queries to the console.
    Only used for testing purposes.
    """
    logger.info(sql)
    return sql.compile(dialect=engine_sqlalchemy.Dialect())


def create(drivername: str) -> Engine:
    """
    Create a connection to the database using SQLAlchemy.
    And return a SQLAlchemy engine object.

    Args:
        drivername (str): Driver name.

    Returns:
        Engine: SQLAlchemy engine object.
    """
    # if using mssql
    # connection_string_mssql = f"mssql+pyodbc://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_SCHEMA}?driver=ODBC+Driver+17+for+SQL+Server"

    # check if running in CI and unit tests
    branch = os.getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
    env_name = os.getenv("CI_ENVIRONMENT_NAME")
    pytest_cov = os.getenv("COV_CORE_DATAFILE")
    cov = os.getenv("COVERAGE_RUN")
    tests = os.getenv("PYTEST_CURRENT_TEST")
    logger.info("Running in CI, using mock engine %s, %s, %s", branch, env_name, tests)
    if any([branch, env_name, pytest_cov, cov, tests]):
        return create_mock_engine("mysql+mysqlconnector://", dump)  # type: ignore

    url = build_url(drivername=drivername)
    return create_engine(url=url, pool_pre_ping=True)


class ConnectionManager:
    """
    Class to manage the connections to the database.
    """

    def __init__(self):
        """
        Initialize the ConnectionManager object.
        """
        self.engines: MutableMapping[str, Engine] = {}

    def set_connection(
        self,
        drivername: str,
        engine: Engine,
    ):
        """
        Set the connection for a given country.

        Args:
            engine (Engine): SQLAlchemy engine object for read operations.

        """
        self.engines[drivername] = engine

    def get_engine(self, drivername: str) -> Engine:
        """
        Get the engine for a given country.

        Args:
            country (str): Country code of the connection.

        Returns:
            Engine: SQLAlchemy engine object for read operations.
        """
        return self.engines[drivername]


connection_manager = ConnectionManager()

connection_manager.set_connection(
    "postgresql",
    create("postgresql"),
)
