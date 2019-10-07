from unittest.mock import MagicMock


def mockExecuteFetchAll(return_value):
    mock_db_execute = MagicMock()
    mock_db_execute.fetchall.return_value = return_value
    return mock_db_execute


def mockExecuteAll(return_value):
    mock_db_execute = MagicMock()
    mock_db_execute.all.return_value = return_value
    return mock_db_execute


def mockFirstBySideEffect(return_value):
    mock_filter_by = MagicMock()
    mock_filter_by.first.side_effect = return_value
    return mock_filter_by


def mockFirstByReturnValue(return_value):
    mock_filter_by = MagicMock()
    mock_filter_by.first.return_value = return_value
    return mock_filter_by


def mockQueryWithFilterBy(return_value):
    mock_query = MagicMock()
    mock_query.filter_by.return_value = return_value
    return mock_query
