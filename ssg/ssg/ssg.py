import datetime
import argparse
import logging

from jinja2 import Environment, PackageLoader, select_autoescape
from poll import bills, news


def parse_args():
    parser = argparse.ArgumentParser(prog="todayin static site generator")
    default_dt = datetime.datetime.now() - datetime.timedelta(days=7)
    parser.add_argument(
        "-s",
        "--bills-since",
        help=f"retrieve all bills since a historical ISO-formatted datetime, default: {default_dt.isoformat()}",
        default=default_dt.isoformat(),
    )
    parser.add_argument("-o", "--output", nargs="?", help="output to file")
    parser.add_argument("--log", nargs="?", help="output debug log to file")

    return parser.parse_args()


def cli():
    args = parse_args()

    # Logging
    if args.log:
        logging.basicConfig(
            level=logging.INFO,
            filename=args.log,
            format="%(asctime)s;%(levelname)s;%(message)s",
            filemode="w",
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
