from pytest import fixture
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    text,
    select as sql_select,
    create_engine,
    create_mock_engine,
)

from app.db.join import (
    build,
    build_alias,
    build_clause,
    split_clauses,
    build_clases_class,
)
from app.db import connection_manager


@fixture
def engine():
    return create_engine("sqlite:///:memory:")


@fixture
def mock_engine():
    return create_mock_engine(
        "mysql+mysqlconnector://", lambda *args, **kwargs: print(args, kwargs)
    )


@fixture
def table1():
    return Table(
        "table1",
        MetaData(),
        Column("id", Integer),
        Column("name", String),
    )


@fixture
def table2():
    return Table(
        "table2",
        MetaData(),
        Column("user_id", Integer),
        Column("city", String),
    )


@fixture
def table3():
    return Table(
        "table3",
        MetaData(),
        Column("city", String),
        Column("population", Integer),
    )


def test_build_alias():
    result = build_alias("table1 t", connection_manager.get_engine("postgresql"), "schema1")
    assert result.name == "t"


def test_build_alias_without_alias():
    result = build_alias("table1", connection_manager.get_engine("postgresql"), "schema1")
    assert str(result) == "schema1.table1"


def test_split_clauses_two():
    result = split_clauses(["table1.id", "table2.user_id"])
    assert result == (["table1", "id"], ["table2", "user_id"])


def test_build_clause(table1, table2):
    tables = {table1.name: table1, table2.name: table2}
    clause = "table1.id = table2.user_id"
    result = build_clause(clause, tables)
    expected = table1.c.id == table2.c.user_id
    assert str(result) == str(expected)


def test_build(mocker, table2):
    table = build_alias("table1", connection_manager.get_engine("postgresql"), "habi_tramite")
    table.append_column(Column("id", Integer))
    select_object = sql_select(text(", ".join(["*"]))).select_from(table)

    mocker.patch("app.db.join.build_alias", side_effect=[table2])
    tables = [
        {
            "table": "table2",
            "onclause": "table1.id = table2.user_id",
            "type": "inner",
        },
    ]

    select, tables_obj = build(
        select_object, table, tables, connection_manager.get_engine("postgresql")
    )

    assert len(select._from_obj) == 1
    assert hasattr(tables_obj, "table1")
    assert hasattr(tables_obj, "table2")


def test_build_different_types(mocker, table2):
    table = build_alias("table1", connection_manager.get_engine("postgresql"), "habi_tramite")
    table.append_column(Column("id", Integer))
    select_object = sql_select(text(", ".join(["*"]))).select_from(table)

    mocker.patch(
        "app.db.join.build_alias",
        side_effect=[table2, table2, table2, table2],
    )

    join_types = ["inner", "outer", "left", "right"]
    for join_type in join_types:
        tables = [
            {
                "table": "table2",
                "onclause": "table1.id = table2.user_id",
                "type": join_type,
            },
        ]

        select, tables_obj = build(
            select_object, table, tables, connection_manager.get_engine("postgresql")
        )
        assert len(select._from_obj) == 1
        assert hasattr(tables_obj, "table1")
        assert hasattr(tables_obj, "table2")


def test_split_clauses():
    clauses = ["table1.id", "table2.user_id", "table3.city"]
    result = split_clauses(clauses)
    assert result == (["table1", "id"], ["table2", "user_id"], ["table3", "city"])


def test_build_clases_class(table1, table2, table3):
    tables = {table1.name: table1, table2.name: table2, table3.name: table3}
    result = build_clases_class(tables)
    assert hasattr(result, "table1")
    assert hasattr(result, "table2")
    assert hasattr(result, "table3")
    assert result.table1 == table1
    assert result.table2 == table2
    assert result.table3 == table3
