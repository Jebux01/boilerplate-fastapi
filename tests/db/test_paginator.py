from pytest import fixture

from app.db.paginator import clean, do_response_pag


@fixture
def sample_list():
    return [{"cnt": 10, "other_column": "value"}, {"cnt": 15, "other_column": "value2"}]


def test_do_response_pag_list(sample_list):
    result = sample_list
    page = 2
    items_per_page = 5
    response = do_response_pag(result, page, items_per_page)

    assert "items" in response
    assert "page" in response
    assert "elements" in response
    assert "total_items" in response
    assert "total_pages" in response

    expected_items = [clean(row) for row in result]
    assert response["items"] == expected_items
    assert response["page"] == page
    assert response["elements"] == items_per_page
    assert response["total_items"] == result[0]["cnt"]
    assert response["total_pages"] == 2


def test_clean():
    row = {"cnt": 10, "other_column": "value"}
    cleaned_row = clean(row)

    assert "cnt" not in cleaned_row
    assert "other_column" in cleaned_row
    assert cleaned_row == {"other_column": "value"}
