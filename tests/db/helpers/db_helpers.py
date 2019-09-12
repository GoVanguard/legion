from unittest.mock import MagicMock


def mock_execute_fetchall(return_value):
    mock_db_execute = MagicMock()
    mock_db_execute.fetchall.return_value = return_value
    return mock_db_execute


def mock_first_by_side_effect(return_value):
    mock_filter_by = MagicMock()
    mock_filter_by.first.side_effect = return_value
    return mock_filter_by


def mock_first_by_return_value(return_value):
    mock_filter_by = MagicMock()
    mock_filter_by.first.return_value = return_value
    return mock_filter_by


def mock_query_with_filter_by(return_value):
    mock_query = MagicMock()
    mock_query.filter_by.return_value = return_value
    return mock_query
