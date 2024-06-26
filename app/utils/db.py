"""
Database utilities.
"""

from functools import partial
from typing import Any, Callable, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import Engine, MetaData, Table, Column
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import aliased

from app.config import settings
from app.db.config import connection_manager


def build_columns_testing(**kwargs) -> list[Column]:
    """
    Create a SQLAlchemy Table object for a given table name.

    Args:
        table_name (str): Name of the table.
        schema (str): Name of the schema.

    Returns:
        Table: SQLAlchemy Table object.
    """
    columns = {}
    if "sets" in kwargs:
        columns.update(kwargs["sets"])

    if "filters" in kwargs:
        columns.update(kwargs["filters"])

    columns_objs = [Column(key) for key in list(columns.keys())]
    return columns_objs


def create_table_with_mock_engine(table_name: str, schema: str, **kwargs) -> Table:
    """
    Create a SQLAlchemy Table object for a given table name.

    Args:
        table_name (str): Name of the table.
        schema (str): Name of the schema.

    Returns:
        Table: SQLAlchemy Table object.
    """

    return Table(
        table_name, MetaData(), schema=schema, *build_columns_testing(**kwargs)
    )


def get_sqlalchemy_table(
    table_name: Table | str,
    engine: Engine,
    schema: str = settings.DB_SCHEMA,
    **kwargs,
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

    if isinstance(engine, MockConnection):
        return create_table_with_mock_engine(table_name, schema, **kwargs)

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


def extract_columns_join(tables: List[Dict], extract_found: bool = True) -> Dict:
    """
    Extract the columns from the tables in the join based on the extract_found flag.
    """
    sets = {}
    for table in tables:
        tablename = table["table"].split(" ")[-1]
        cb, ca = map(str.strip, table["onclause"].split("="))

        if extract_found:
            column = (
                ca.split(".")[-1] if cb.startswith(tablename) else cb.split(".")[-1]
            )
        else:
            column = (
                ca.split(".")[-1] if not cb.startswith(tablename) else cb.split(".")[-1]
            )

        sets[column] = "test"

    return sets


# pylint: disable=dangerous-default-value
def build_alias(
    table_name: str,
    engine: Engine,
    schema: str,
    tables: Optional[list] = [],
    found: bool = True,
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
        if isinstance(engine, MockConnection) and tables:
            return partial_table(sets=extract_columns_join(tables, found))

        return partial_table()

    table = get_table()
    if len(split_table) > 1:
        return aliased(table, name=split_table[-1])

    return table


def convert_table(fnx: Callable) -> Callable:
    """
    Convert the table name to a Table object.
    """

    def wrapped_function(*args, **kwargs) -> Table:
        """
        Convert the table name to a Table object.
        """
        engine = connection_manager.get_engine("postgresql")
        if kwargs.get("table_name"):
            kwargs["table_name"] = get_sqlalchemy_table(
                engine=engine,
                **kwargs,
            )

        return fnx(*args, **kwargs)

    return wrapped_function
