from poll import bills
import pytest
from pytest_socket import socket_disabled
import datetime


def test_fetch_most_recent_session():
    assert bills.fetch_most_recent_session() >= 37


def test_fetch_most_recent_session_no_conn(socket_disabled):
    with pytest.raises(Exception):
        bills.fetch_most_recent_session()


def test_fetch_bills():
    """Check that at least one bill is retrieved with default settings"""
    for _, bill_objs in zip(range(1), bills.fetch_bills()):
        assert isinstance(bill_objs, bills.Bill)


def test_fetch_bills_no_conn(socket_disabled):
    with pytest.raises(Exception):
        for _, bill_objs in zip(range(1), bills.fetch_bills()):
            isinstance(bill_objs, bills.Bill)


def test_fetch_bills_up_to_date():
    # No datetime provided, should fail
    with pytest.raises(TypeError):
        bills.fetch_bills_up_to_date()  # type: ignore

    # Should come back with something if we give it 10 days
    # (unless parliament has been suspended for longer)
    bills.fetch_bills_up_to_date(
        datetime.datetime.now() - datetime.timedelta(days=10)
    )


def test_fetch_bills_up_to_date_no_conn(socket_disabled):
    with pytest.raises(Exception):
        bills.fetch_bills_up_to_date(
            datetime.datetime.now() - datetime.timedelta(days=10)
        )
