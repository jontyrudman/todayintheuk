import pytest
from pytest_socket import socket_disabled
from poll import news


def test_fetch_feeds():
    feeds = news.fetch_feeds()

    for k, v in feeds.items():
        assert v["data"]["entries"] is not None, f"{k} didn't load correctly!"


def test_fetch_feeds_no_conn(socket_disabled):
    feeds = news.fetch_feeds()

    for _, v in feeds.items():
        with pytest.raises(KeyError):
            v["data"]
        
        assert v["error"] == f"{v['name']} could not be retrieved."
