"""Custom exceptions"""


class NotFoundError(Exception):
    """Raised when a SQL query returns no results."""


class SQLExecutionError(Exception):
    """Raised when a SQL query returns no results."""


class BadClausesError(Exception):
    """Raised when a SQL query returns no results."""
