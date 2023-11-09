from poll import bills


def test_fetch_most_recent_session():
    assert bills.fetch_most_recent_session() >= 37

def test_fetch_bills():
    ...
