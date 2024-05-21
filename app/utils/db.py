"""
Database utilities.
"""

from functools import partial
from typing import Any, Callable

from fastapi import HTTPException, status
from sqlalchemy import Engine, MetaData, Table
from sqlalchemy.orm import aliased

from app.config import settings


def get_sqlalchemy_table(
    table_name: Table | str,
    engine: Engine,
    schema: str = settings.DB_SCHEMA,
    **__,
) -> Table:
    """
    Get or create a SQLAlchemy Table object for a given table name.

    Args:
        table_name (str): Name of the table.
        engine (Engine): SQLAlchemy engine object.
        schema (str): Name of the schema.

    Returns:
        Table: SQLAlchemy Table object.
    """

    if isinstance(table_name, Table):
        return table_name

    if not bool(table_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Table name is required"
        )

    return Table(
        table_name,
        MetaData(),
        autoload_with=engine,
        schema=schema,
    )


def build_alias(
    table_name: str,
    engine: Engine,
    schema: str,
) -> Table | Any:
    """
    Build an aliased SQLAlchemy table based on the provided table name, engine, and schema.
    If the table_name contains a space an alias, the last element will be used as the alias
    example: "table_name alias_name" and return a alias object

    if the table_name not contains a space, return a sqlalchemy table object

    Args:
        table_name (str): The name of the table.
        engine (Engine): SQLAlchemy engine object.
        schema (str): The name of the schema.

    Returns:
        Table | Any: The aliased table.

    Example:
        >>> build_alias("my_table", my_engine, "my_schema")
        >>> build_alias("my_table my_alias", my_engine, "my_schema")
    """
    split_table = table_name.split(" ")

    partial_table = partial(
        get_sqlalchemy_table,
        table_name=split_table[0],
        engine=engine,
        schema=schema,
    )

    def get_table():
        return partial_table()

    table = get_table()
    if len(split_table) > 1:
        return aliased(table, name=split_table[-1])

    return table

def convert_table(engine: Engine) -> Callable:
    """
    Decorator to convert the table name to a Table object.
    """

    def wrapper(fnx: Callable) -> Callable:
        """
        Convert the table name to a Table object.
        """

        def wrapped_function(*args, **kwargs) -> Table:
            """
            Convert the table name to a Table object.
            """
            kwargs["table_name"] = get_sqlalchemy_table(
                engine=engine,
                **kwargs,
            )

            return fnx(*args, **kwargs)

        return wrapped_function

    return wrapper
