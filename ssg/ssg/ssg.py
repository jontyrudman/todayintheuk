import datetime
import argparse

from jinja2 import Environment, PackageLoader, select_autoescape
from poll import bills, news


def parse_args():
    parser = argparse.ArgumentParser(prog="todayin static site generator")
    default_dt = datetime.datetime.now() - datetime.timedelta(hours=24)
    parser.add_argument(
        "-s",
        "--bills-since",
        help=f"retrieve all bills since a historical ISO-formatted datetime, default: {default_dt.isoformat()}",
        default=default_dt.isoformat()
    )
    parser.add_argument("-o", "--output", nargs='?', help="output to file")

    return parser.parse_args()


def cli():
    args = parse_args()

    jinja_env = Environment(loader=PackageLoader("ssg"), autoescape=select_autoescape())
    template = jinja_env.get_template("template.html.jinja")

    # Get bills
    bill_objs = bills.fetch_bills_up_to_date(dt=datetime.datetime.fromisoformat(args.bills_since))
    # Get news
    news_dicts = news.fetch_feeds()

    # Render template
    output_str = template.render(bills=bill_objs, news=news_dicts)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_str)
    else:
        print(output_str)
