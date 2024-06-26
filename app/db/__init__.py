"""Module to connection DB and generic functions"""

from functools import wraps
from logging import Logger, getLogger
from typing import Any, Callable, List, Tuple, TypeVar, Mapping

from sqlalchemy import (
    Delete,
    Insert,
    Select,
    Table,
    Update,
    delete as sql_delete,
    insert as sql_insert,
    select as sql_select,
    text,
    update as sql_update,
)
from sqlalchemy import CursorResult
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import Session

from app.db.config import connection_manager
from app.db.join import build
from app.db.paginator import do_response_pag
from app.db.responses import do_response
from app.exceptions import SQLExecutionError
from app.utils.db import build_alias, convert_table, get_sqlalchemy_table

logger: Logger = getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])  # pylint: disable=C0103


def sql_exec(fnx: Callable = lambda x: x) -> Callable[[F], F] | F:
    """
    Decorator to execute a SQL query with optional post-processing.

    This decorator can be used to wrap functions that return SQLAlchemy query objects.
    It allows for post-processing of the query results by specifying a post-process function.

    Args:
        fnx (Callable, optional): A post-process function to be applied to the query results.
                                  Defaults to a no-op lambda function.

    Returns:
        Callable[[F], F] | F: The decorated function, which will execute the SQL query
                              and optionally apply the post-process function.
    """

    @wraps(fnx)
    def new_fnx(*frgs, **fwargs) -> Any:
        """
        Inner function that wraps the original function and executes the SQL query.

        Args:
            *frgs: Positional arguments to be passed to the wrapped function.
            **fwargs: Keyword arguments to be passed to the wrapped function.

        Returns:
            Any: The result of the SQL query execution, potentially post-processed.
        """

        def execute(fnx_final: Callable, *args, **kwargs) -> Any:
            """
            Execute the SQL query and optionally apply post-processing.

            Args:
                fnx_final (Callable): The final function to execute.
                *args: Positional arguments to be passed to the final function.
                **kwargs: Keyword arguments to be passed to the final function.

            Returns:
                Any: The result of the SQL query execution, potentially post-processed.
            """
            if kwargs.get("table_name"):
                kwargs["table_name"] = get_sqlalchemy_table(
                    engine=connection_manager.get_engine("postgresql"),
                    **kwargs,
                )
            query = fnx_final(*args, **kwargs)
            return exec_query(query)

        if len(frgs) == 1 and len(fwargs) == 0 and callable(frgs[0]):

            def wrapper(*args, **kwargs) -> Any:
                """
                Wrapper function that calls the execute function with the given arguments.

                Args:
                    *args: Positional arguments to be passed to the execute function.
                    **kwargs: Keyword arguments to be passed to the execute function.

                Returns:
                    Any: The result of the execute function.
                """
                return fnx(execute(frgs[0], *args, **kwargs))

            return wrapper

        return execute(fnx, *frgs, **fwargs)

    return new_fnx


def exec_query(
    query: Select | Update | Insert | Delete,
    post_process: Callable = lambda x: x,
) -> dict | list | CursorResult | Any:
    """
    Execute a SQL query.

    Args:
        query (Select | Update | Insert | Delete): The query to execute.
    """
    engine = connection_manager.get_engine("postgresql")
    conn = engine.connect()
    if isinstance(conn, MockConnection):
        conn.close = lambda *_, **__: None

    try:
        return post_process(do_response(query, conn))
    except SQLExecutionError as e:
        logger.error("Error executing query: %s", e)
        raise e from e
    finally:
        conn.close()


@convert_table
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


@convert_table
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


@convert_table
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


@convert_table
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
    schema: str = "test",
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
        country (str, optional): The country to connect to. Defaults to "CO".

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
    engine = connection_manager.get_engine("postgresql")
    table = build_alias(
        table_name=table_name,
        engine=engine,
        schema=schema,
        tables=config["tables"],
    )

    select_object = sql_select(text(", ".join(columns))).select_from(table)
    select_join, tables = build(
        select_object,
        table,
        config["tables"],
        engine,
    )

    return select_join, tables


def paginator(
    query_object: Select,
    elements: int = 10,
    page: int = 1,
    country: str = "CO",
    **kwargs,
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

    sub = sql_select(text("count(*) AS total_items")).select_from(
        *query_object.get_final_froms()
    )
    if query_object.whereclause is None:
        sub = sub.scalar_subquery().label("cnt")
    else:
        sub = sub.where(query_object.whereclause).scalar_subquery().label("cnt")

    query = query_object.add_columns(sub).limit(elements).offset(elements * (page - 1))

    result: list | dict = exec_query(query, country=country, **kwargs)  # type: ignore
    if not result:
        return {
            "items": [],
            "page": page,
            "elements": elements,
            "total_items": 0,
            "total_pages": 0,
        }

    return do_response_pag(result, page, elements)


def begin_transaction(
    session_selected: Session,
    queries: List[Update | Insert],
    post_process: Callable,
) -> List:
    """
    Begin a transaction and execute a list of queries.

    Args:
        session_selected (Session): The session to use for the transaction.
        queries (List[Update | Insert]): A list of queries to execute.

    Returns:
        list: The results of the queries.
    """

    def execute_query(session: Session, query: Update | Insert) -> Mapping[str, Any]:
        result = session.execute(query)
        if isinstance(query, Insert):
            return {
                "id": result.inserted_primary_key[0],  # type: ignore
                "table": query.table.name,
                "row_affected": result.rowcount,
                "query": query,
            }

        if isinstance(query, Select):
            return {
                "row_affected": result.rowcount,
                "query": query,
                "result": result.mappings().all(),
            }

        return {
            **result.last_updated_params(),  # type: ignore
            "table": query.table.name,  # type: ignore
            "row_affected": result.rowcount,
            "query": query,
        }

    with session_selected.begin():
        results = [
            post_process(execute_query(session_selected, query)) for query in queries
        ]

    return results


def transaction(queries: List[Update | Insert], **kwargs) -> List:
    """
    Execute a list of queries in a transaction.
    A transaction is a set of queries that are executed together.
    If one of the queries fails, the entire transaction is rolled back.
    This ensures that the database remains in a consistent state.

    Args:
        queries (List[Update | Insert]): A list of queries to execute.

    Returns:
        list: The results of the queries.
    """
    session = Session(connection_manager.get_engine("postgresql"))
    post_process = kwargs.get("post_process", lambda x: x)
    return begin_transaction(session, queries, post_process)
