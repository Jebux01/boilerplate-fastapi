"""Module to connection DB and generic functions"""

from logging import Logger, getLogger
from typing import Any, Callable, Dict, List, Tuple

from fastapi import HTTPException, status
from sqlalchemy import (
    Delete,
    Insert,
    Select,
    Table,
    TextClause,
    Update,
    delete as sql_delete,
    insert as sql_insert,
    select as sql_select,
    text,
    update as sql_update,
)
from sqlalchemy import CursorResult

from app.db.config import ENGINE
from app.db.join import build
from app.db.paginator import do_response_pag
from app.db.responses import do_response
from app.exceptions import SQLExecutionError
from app.utils.db import build_alias, convert_table, get_sqlalchemy_table

logger: Logger = getLogger(__name__)


def sql_exec(fnx: Callable) -> Callable:
    """
    Decorator to execute a SQL query.

    Args:
        fnx (Callable): The function to decorate.
    """

    def wrapper(*args, **kwargs) -> dict | list | CursorResult:
        """
        Execute a SQL query.
        execute the function and this return the query object to execute
        the functions to execute have to return a sqlalchemy.sql.text.TextClause
        """
        if "table_name" in kwargs:
            kwargs["table_name"] = get_sqlalchemy_table(
                engine=ENGINE,
                **kwargs,
            )
        query = fnx(*args, **kwargs)
        return exec_query(query)

    return wrapper


def exec_query(
    query: Select | Update | Insert | Delete,
) -> dict | list | CursorResult | Any:
    """
    Execute a SQL query.

    Args:
        query (Select | Update | Insert | Delete): The query to execute.
    """
    conn = ENGINE.connect()

    try:
        return do_response(query, conn)
    except SQLExecutionError as e:
        logger.error("Error executing query: %s", e)
        raise e from e
    finally:
        conn.close()


@convert_table(ENGINE)
def select(  # pylint: disable=W0102
    table_name: Table,
    columns: list = ["*"],
    **__,
) -> Tuple[Select, Table]:
    """
    Constructs and returns a SQLAlchemy SELECT query object.

    The function returns an object of type Select from sqlalchemy and the object of type Table
    this to be able to obtain the properties of the table and use the sqlalchemy syntanx
    and not the one from sql, for example to obtain the name of the table you use table_name.name
    and to access the columns table_name.c.column_name

    Args:
        table_name (Table): SQLAlchemy Table object representing the table to select from.\
        columns (list, optional): List of columns to select. Defaults to ["*"].

    Returns:
        Tuple[sqlalchemy.sql.dml.Select, Table]: SQLAlchemy SELECT object
        and the table object.

    Example:
        result = _select(my_table)
    """
    return sql_select(text(", ".join(columns))).select_from(table_name), table_name


@convert_table(ENGINE)
def update(
    table_name: Table,
    **__,
) -> Tuple[Update, Table]:
    """
    Constructs and returns a SQLAlchemy UPDATE query object.

    The function returns an object of type Update from sqlalchemy and the object of type Table
    this to be able to obtain the properties of the table and use the sqlalchemy syntanx
    and not the one from sql, for example to obtain the name of the table you use table_name.name
    and to access the columns table_name.c.column_name

    Args:
        table_name (Table): SQLAlchemy Table object representing the table to update.

    Returns:
        sqlalchemy.sql.dml.Update: SQLAlchemy UPDATE object.

    Example:
        result = _update(my_table)
    """
    return sql_update(table=table_name), table_name


@convert_table(ENGINE)
def insert(
    table_name: Table,
    **__,
) -> Tuple[Insert, Table]:
    """
    Constructs and returns a SQLAlchemy INSERT query object.

    The function returns an object of type Insert from sqlalchemy and the object of type Table
    this to be able to obtain the properties of the table and use the sqlalchemy syntanx
    and not the one from sql, for example to obtain the name of the table you use table_name.name
    and to access the columns table_name.c.column_nam

    Args:
        table_name (Table): SQLAlchemy Table object representing the table to insert into.

    Returns:
        sqlalchemy.sql.dml.Insert: SQLAlchemy INSERT object.

    Example:
        result = _insert(my_table)
    """
    return sql_insert(table=table_name), table_name


@convert_table(ENGINE)
def delete(
    table_name: Table,
    **__,
) -> Tuple[Delete, Table]:
    """
    Constructs and returns a SQLAlchemy DELETE query object.

    The function returns an object of type Delete from sqlalchemy and the object of type Table
    this to be able to obtain the properties of the table and use the sqlalchemy syntanx
    and not the one from sql, for example to obtain the name of the table you use table_name.name
    and to access the columns table_name.c.column_nam

    Args:
        table_name (Table): SQLAlchemy Table object representing the table to delete from.

    Returns:
        sqlalchemy.sql.dml.Delete: SQLAlchemy DELETE object.

    Example:
        result = _delete(my_table)
    """
    return sql_delete(table=table_name), table_name


def join(
    table_name: str,
    columns: List[str],
    config: dict,
    schema: str = "habi_tramite",
) -> Tuple[Select, Any]:
    """
    This function receives as parameters the name of table principal that use to select_from
    the columns from which you will want to obtain,
    In the same way it receives the configuration to be able to build the joins.
    And the schema in which the tables are located if it is not the default.

    within this config parameter structure that will be a list of dictionaries,
    The dictionaries must contain the keys "table", "on_clause", "type", "schema".

    The name of the tables may have aliases and this function will construct the alias
    >>> "table t"
    >>> "table2 t2"

    The alias should also be included in the clause (if it is included in the table,
    if not directly the name)

    This function will return a tuple, since it will return the join object in the first position,
    In the second position it will return a class that will have the name or alias of
    the tables as properties, this so they can continue building the querie

    if the tables is "users u" and "departaments d", the class will be
    >>> class Tables:
    >>>     u = t
    >>>     d = t2

    >>> tables.u.c.ID == 1

    if the tables is "users" and "departaments", the class will be
    >>> class Tables:
    >>>     users = users
    >>>     departaments = departaments

    >>> tables.users.c.ID == 1

    Args:
        table_name (str): The name of the table to select from.
        columns (List[str]): List of columns to select.
        config (dict): The configuration for the join.
        schema (str, optional): The schema of the tables. Defaults to "habi_tramite".

    Returns:
        Tuple[sqlalchemy.sql.dml.Select, TablesBase]: SQLAlchemy SELECT object
        and the table object.

    Example:
    >>>    query, tables = join(
    ...        table_name="country c",
    ...        columns=[
    ...            "c.Name as CountryName",
    ...            "c.HeadOfState",
    ...            "c2.Name as NameCity",
    ...            "c2.District",
    ...        ],
    ...        config={
    ...            "tables": [
    ...                {
    ...                    "table": "city c2",
    ...                    "onclause": "c.Code = c2.CountryCode",
    ...                    "type": "right",
    ...                    "schema": "world",
    ...                },
    ...                {
    ...                    "table": "countrylanguage cl",
    ...                    "onclause": "c.Code = cl.CountryCode",
    ...                    "type": "left",
    ...                    "schema": "world",
    ...                },
    ...            ],
    ...        },
    ...    )

    >>>    query.where(tables.c.c.Code == "MEX")
    """
    table = build_alias(
        table_name=table_name,
        engine=ENGINE,
        schema=schema,
    )
    select_object = sql_select(text(", ".join(columns))).select_from(table)
    select_join, tables = build(
        select_object,
        table,
        config["tables"],
        ENGINE,
    )

    return select_join, tables


def paginator(
    query_object: Select,
    elements: int = 10,
    page: int = 1,
) -> dict:
    """
    Paginator for SQL query.

    Args:
        query_object (sqlalchemy.sql.selectable.Select): The SQL query.
        items_per_page (int): The total items per page.
        page (int): The page number.

    Returns:
        sqlalchemy.sql.selectable.Select: The SQL query.

    Examples:
        >>> paginator(
        ...     query_object=select_generic(table_name="table_name"),
        ...     items_per_page=10,
        ...     page=1
        ... )
        SELECT * FROM table_name LIMIT 10 OFFSET 0
    """

    sub = sql_select(text("count(*) AS total_items")).select_from(*query_object.froms)
    if query_object.whereclause is None:
        sub = sub.scalar_subquery().label("cnt")
    else:
        sub = sub.where(query_object.whereclause).scalar_subquery().label("cnt")

    query = query_object.add_columns(sub).limit(elements).offset(elements * (page - 1))

    result: list | dict = exec_query(query)  # type: ignore
    if not result:
        return {
            "items": [],
            "page": page,
            "elements": elements,
            "total_items": 0,
            "total_pages": 0,
        }

    return do_response_pag(result, page, elements)
