"""
This module contains the methods for building a join clause for a SQL query.
"""

from functools import partial
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import Alias, Engine, Select, Table
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.orm import aliased

from app.exceptions import BadClausesError
from app.utils.db import extract_columns_join, get_sqlalchemy_table


type_join = {
    "inner": False,
    "outer": True,
    "left": True,
    "right": False,
}


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


def split_clauses(clauses: List[str]) -> tuple:
    """
    Split the elements of the join clause into a tuple.

    Args:
        clauses (List[str]): The list of elements in the join clause.

    Returns:
        tuple: A tuple containing the cleaned elements of the join clause.

    Example:
        >>> split_clauses(["table1.id", "table2.user_id"])
        (('table1','id'), ('table2','user_id'))
    """
    return tuple(clause.split(".") for clause in clauses)


def build_clause(
    clause: str,
    tables: Dict[str, Table | Alias],
):
    """
    Build a join clause for SQLAlchemy tables or aliases based on the provided condition.

    Args:
        clause (str): The join condition in the form "table1.column1 = table2.column2".
        tables (Dict[str, Table | Alias]): A dictionary of SQLAlchemy tables or aliases.

    Returns:
        Any: The constructed join clause.

    Raises:
        BadClausesError: If the clause is invalid.

    Example:
        >>> build_clause("table1.id = table2.user_id", {"table1": my_table, "table2": my_table2})
    """
    clause1, clause2 = split_clauses(clause.split("="))
    table = tables.get(clause1[0].strip())
    table2 = tables.get(clause2[0].strip())
    if table is None or table2 is None:
        raise BadClausesError(
            f"Invalid clause {clause}, {clause1[0]} or {clause2[0]} not found in tables"
        )

    return getattr(table.c, clause1[-1].strip()) == getattr(
        table2.c, clause2[-1].strip()
    )


def build(
    select: Select,
    table: Table,
    tables: List[Dict[str, str]],
    engine: Engine,
) -> Tuple[Select, Any]:
    """
    Builds a list of sqlalchemy Join objects and returns a select object
    With the join entered in order to continue building the query.

    Args:
        select (Select): SQLAlchemy SELECT object.
        table (Table): SQLAlchemy Table object representing the table to select from.
        tables (List[Dict[str, str]]): A list of dictionaries representing table definitions.
        engine (Engine): SQLAlchemy engine object.

    Returns:
        Tuple[List[Join], Any]: A tuple containing the list of join objects
        and the container class for tables.

    Example:
        >>> build(
        select_obj,
        my_table,
        [
            {
                "table": "pipefy_card pc",
                "onclause": "n.card_id = pc.id",
                "type": "inner",
                "schema": "habi_tramite",
            },
            {
                "table": "pipefy_phase pp2",
                "onclause": "n.phase_id = pp2.id",
                "type": "inner",
                "schema": "habi_tramite",
            },
        ],
        my_engine
        )
    """

    tables_object = {}
    tables_object[table.name] = table

    for config in tables:
        schema = config.get("schema", "habi_tramite")
        table_two = build_alias(config["table"], engine, schema, tables, False)
        tables_object[table_two.name] = table_two
        full, join_type, on_clause = (
            config.get("full", False),
            type_join.get(config["type"], False),
            config["onclause"],
        )

        clausules = build_clause(on_clause, tables_object)
        select = select.join(table_two, clausules, full=bool(full), isouter=join_type)

    return select, build_clases_class(tables_object)


def build_clases_class(tables: Dict[str, Table | Alias]) -> Any:
    """
    Build a class with the tables as properties.

    Args:
        tables (Dict[str, Table | Alias]): A dictionary of SQLAlchemy tables or aliases.

    Returns:
        Any: The constructed class.

    Example:
        >>> build_clases_class({"table1": my_table, "table2": my_table2})
    """

    class Tables:
        """
        Container class for tables.
        """

        def __init__(self, my_dict):
            for key in my_dict:
                setattr(self, key, my_dict[key])

    return Tables(tables)
