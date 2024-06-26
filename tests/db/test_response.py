from pytest import fixture
from sqlalchemy import (
    create_engine,
    Table,
    MetaData,
    Column,
    Integer,
    create_mock_engine,
    text,
)
from sqlalchemy.sql import select, insert, update, delete
from app.db.responses import do_response


@fixture
def connection():
    return create_engine("sqlite:///:memory:").connect()


@fixture
def mock_connection():
    return create_mock_engine(
        "mysql+mysqlconnector://", lambda *args, **kwargs: print(args, kwargs)
    )


@fixture
def test_table(connection):
    metadata = MetaData()
    table = Table("test_table", metadata, Column("id", Integer, primary_key=True))
    metadata.create_all(connection)
    return table


def test_insert_response(connection, test_table):
    insert_query = insert(test_table).values(id=1)
    response = do_response(insert_query, connection)
    assert response == {"id": 1}


def test_update_response(connection, test_table):
    connection.execute(test_table.insert().values(id=1))
    update_query = update(test_table).values(id=2)
    response = do_response(update_query, connection)
    assert response == {"id": 2, "affected_rows": 1}


def test_delete_response(connection, test_table):
    connection.execute(test_table.insert().values(id=1))
    delete_query = delete(test_table).where(test_table.c.id == 1)
    response = do_response(delete_query, connection)
    assert response == {"affected_rows": 1}


def test_select_one_row_response(connection, test_table):
    connection.execute(test_table.insert().values(id=1))
    select_query = select(test_table)
    response = do_response(select_query, connection)
    assert response == [{"id": 1}]


def test_select_multiple_rows_response(connection, test_table):
    connection.execute(test_table.insert().values(id=1))
    connection.execute(test_table.insert().values(id=2))
    select_query = select(test_table)
    response = do_response(select_query, connection)
    assert response == [{"id": 1}, {"id": 2}]


def test_text_clause_response(connection):
    text_query = text("SELECT 1")
    response = do_response(text_query, connection)
    assert response.fetchall() == [(1,)]


def test_mock_connection_response(mock_connection):
    update_query = update(Table("table_name", MetaData())).values(id=2)
    response = do_response(update_query, mock_connection)
    assert response == update_query


def test_mock_connection_response_for_insert(mock_connection):
    insert_query = insert(Table("test_table", MetaData())).values(id=1)
    response = do_response(insert_query, mock_connection)
    assert response == insert_query


def test_mock_connection_response_for_select(mock_connection):
    select_query = select(Table("test_table", MetaData()))
    response = do_response(select_query, mock_connection)
    assert response == select_query


def test_mock_connection_response_for_delete(mock_connection):
    delete_query = delete(Table("test_table", MetaData())).where(text("id = 1"))
    response = do_response(delete_query, mock_connection)
    assert response == delete_query
