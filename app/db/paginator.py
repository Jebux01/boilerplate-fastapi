"""
Paginator methods.
"""
from math import ceil as up

from multipledispatch import Dispatcher
from sqlalchemy.engine import RowMapping

do_response_pag = Dispatcher("do_response_pag")


def clean(row: dict) -> dict:
    """
    Clean the row.
    """
    row = dict(row)
    del row["cnt"]
    return row


@do_response_pag.register(RowMapping, int, int)
def _(
    result: RowMapping,
    page: int,
    items_per_page: int,
) -> dict:
    """
    Return the response of the paginator.

    Args:
        result (RowMapping): The result of the query.
        page (int): The page number.
        items_per_page (int): The total items per page.

    Returns:
        dict: The response of the paginator.
    """
    total_items = result["cnt"]
    total_pages = up(total_items / items_per_page)
    items = [clean(result)]  # type: ignore
    return {
        "items": items,
        "page": page,
        "elements": items_per_page,
        "total_items": total_items,
        "total_pages": total_pages,
    }


@do_response_pag.register(list, int, int)
def _(
    result: list,
    page: int,
    items_per_page: int,
) -> dict:
    """
    Return the response of the paginator.

    Args:
        result (list): The result of the query.
        page (int): The page number.
        items_per_page (int): The total items per page.

    Returns:
        dict: The response of the paginator.
    """
    total_items = result[0]["cnt"]
    total_pages = up(total_items / items_per_page)
    items = list(map(clean, result))
    return {
        "items": items,
        "page": page,
        "elements": items_per_page,
        "total_items": total_items,
        "total_pages": total_pages,
    }
