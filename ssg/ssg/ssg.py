import datetime
import argparse
import logging

from jinja2 import Environment, PackageLoader, select_autoescape
from poll import bills, news


LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "error": logging.ERROR,
    "warn": logging.WARN,
}


def parse_args():
    parser = argparse.ArgumentParser(prog="todayintheuk static site generator")
    default_dt = datetime.datetime.now() - datetime.timedelta(days=7)
    parser.add_argument(
        "-s",
        "--bills-since",
        help=f"retrieve all bills since a historical ISO-formatted datetime, default: {default_dt.isoformat()}",
        default=default_dt.isoformat(),
    )
    parser.add_argument("-o", "--output", nargs="?", help="output to file")
    parser.add_argument(
        "--log-level",
        nargs="?",
        help="set log level",
        choices=LOG_LEVELS.keys(),
        default="info",
    )

    return parser.parse_args()


def cli():
    args = parse_args()

    # Logging
    if args.log_level:
        logging.basicConfig(
            level=LOG_LEVELS[args.log_level],
            format="%(asctime)s;%(levelname)s;%(message)s",
        )

    jinja_env = Environment(loader=PackageLoader("ssg"), autoescape=select_autoescape())
    template = jinja_env.get_template("template.html.jinja")

    # Get bills
    bill_objs = bills.fetch_bills_up_to_date(
        dt=datetime.datetime.fromisoformat(args.bills_since)
    )
    # Get news
    news_dicts = news.fetch_feeds()

    # Render template
    output_str = template.render(
        bills=bill_objs, news=news_dicts, compile_dt=datetime.datetime.now()
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_str)
    else:
        print(output_str)
