from sqlalchemy import Delete, Insert, Select, Update  # noqa: E402
from app.db import (  # noqa: E402
    exec_query,
    select,
    update,
    insert,
    delete,
    paginator,
    join,
)


def test_exec_query():
    # Mock de un objeto Select para la prueba
    mock_select = select(table_name="my_table")  # type: ignore
    # Prueba de exec_query con un objeto Select
    result = exec_query(mock_select[0])
    assert isinstance(result, Select)

    # Mock de un objeto Update para la prueba
    mock_update = update(table_name="my_table")  # type: ignore
    # Prueba de exec_query con un objeto Update
    result = exec_query(mock_update[0])
    assert isinstance(result, Update)

    # Mock de un objeto Insert para la prueba
    mock_insert = insert(table_name="my_table")  # type: ignore
    # Prueba de exec_query con un objeto Insert
    result = exec_query(mock_insert[0])
    assert isinstance(result, Insert)

    # Mock de un objeto Delete para la prueba
    mock_delete = delete(table_name="my_table")  # type: ignore
    # Prueba de exec_query con un objeto Delete
    result = exec_query(mock_delete[0])
    assert isinstance(result, Delete)


def test_select():
    result = select(table_name="select")  # type: ignore
    assert isinstance(result, tuple)
    assert isinstance(result[0], Select)
    assert result[1].name == "select"


def test_update():
    result = update(table_name="my_table")  # type: ignore
    assert isinstance(result, tuple)
    assert isinstance(result[0], Update)
    assert result[1].name == "my_table"


def test_insert():
    result = insert(table_name="my_table")  # type: ignore
    assert isinstance(result, tuple)
    assert isinstance(result[0], Insert)
    assert result[1].name == "my_table"


def test_delete():
    result = delete(table_name="my_table")  # type: ignore
    assert isinstance(result, tuple)
    assert isinstance(result[0], Delete)
    assert result[1].name == "my_table"


def test_paginator(mocker):
    # Mock del objeto Select para la prueba
    mocker.patch(
        "app.db.exec_query",
        return_value=[
            {"NameCity": "Ciudad de México", "District": "Distrito Federal", "cnt": 10},
            {"NameCity": "Guadalajara", "District": "Jalisco", "cnt": 10},
            {"NameCity": "Ecatepec de Morelos", "District": "México", "cnt": 10},
            {"NameCity": "Puebla", "District": "Puebla", "cnt": 10},
            {"NameCity": "Nezahualcóyotl", "District": "México", "cnt": 10},
            {"NameCity": "Juárez", "District": "Chihuahua", "cnt": 10},
            {"NameCity": "Tijuana", "District": "Baja California", "cnt": 10},
            {"NameCity": "León", "District": "Guanajuato", "cnt": 10},
            {"NameCity": "Monterrey", "District": "Nuevo León", "cnt": 10},
            {"NameCity": "Zapopan", "District": "Jalisco", "cnt": 10},
        ],
    )
    mock_select = select(table_name="my_table")  # type: ignore
    # Prueba de la función paginator
    result = paginator(mock_select[0], elements=5, page=1)
    assert isinstance(result, dict)
    assert "items" in result
    assert "page" in result
    assert "elements" in result
    assert "total_items" in result
    assert "total_pages" in result


def test_join():
    query, tables = join(
        table_name="my_table m",
        columns=["m.name"],
        config={
            "tables": [
                {
                    "table": "city c2",
                    "onclause": "m.Code = c2.CountryCode",
                    "type": "right",
                    "schema": "world",
                },
                {
                    "table": "city c3",
                    "onclause": "m.TestColumn = c3.CountryCode",
                    "type": "right",
                    "schema": "world",
                },
            ]
        },
        schema="world",
    )  # type: ignore
    assert isinstance(query, Select)
    assert isinstance(tables, object)
