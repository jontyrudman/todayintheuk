import logging

import feedparser

FEEDS = {
    "bbc": {"name": "BBC", "url": "http://feeds.bbci.co.uk/news/uk/rss.xml"},
    "guardian": {
        "name": "The Guardian",
        "url": "https://www.theguardian.com/uk-news/rss",
    },
    "gbnews": {"name": "GB News", "url": "https://www.gbnews.com/feeds/news/uk.rss"},
    "independent": {
        "name": "The Independent",
        "url": "https://www.independent.co.uk/news/uk/rss",
    },
    "dailymail": {
        "name": "Daily Mail",
        "url": "https://www.dailymail.co.uk/news/index.rss",
    },
    "mirror": {
        "name": "Mirror",
        "url": "https://www.mirror.co.uk/news/uk-news?service=rss",
    },
}


def fetch_feeds() -> dict:
    loaded_dict = {}

    for k, v in FEEDS.items():
        logging.info(f"Fetching news from {v['name']}...")
        try:
            feed = feedparser.parse(v["url"])
            loaded_dict[k] = {**v, "data": feed}
            logging.debug(f"Fetched data into dict: {loaded_dict[k]}")
        except Exception as e:
            logging.error(e)
            loaded_dict[k] = {**v, "error": f"{v['name']} could not be retrieved."}

    return loaded_dict
