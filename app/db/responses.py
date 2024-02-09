"""
Module for handling responses from the database.
"""

from multipledispatch import Dispatcher
from sqlalchemy import Connection, CursorResult
from sqlalchemy.sql import Delete, Insert, Select, Update
from sqlalchemy.sql.expression import TextClause

do_response = Dispatcher("do_response")


@do_response.register(Insert, Connection)
def _(query: Insert, conn: Connection) -> dict:
    response = conn.execute(query)
    conn.commit()
    return response.last_inserted_params()  # type: ignore


@do_response.register(Update, Connection)
def _(query: Update, conn: Connection) -> dict:
    response = conn.execute(query)
    conn.commit()
    return {"affected_rows": response.rowcount}


@do_response.register(Delete, Connection)
def _(query: Delete, conn: Connection) -> dict:
    response = conn.execute(query)
    conn.commit()
    return {"affected_rows": response.rowcount}


# pylint: disable=protected-access
@do_response.register(Select, Connection)
def _(
    query: Select,
    conn: Connection,
) -> dict | list:
    response = conn.execute(query)
    if response.rowcount == 0:
        return {}

    if response.rowcount == 1:
        return response.fetchone()._mapping  # type: ignore

    return [dict(row._mapping) for row in response.fetchall()]


@do_response.register(TextClause, Connection)
def _(query: TextClause, conn: Connection) -> CursorResult:
    return conn.execute(query)
