import datetime

from jinja2 import Environment, PackageLoader, select_autoescape
from poll.legislation import bills

env = Environment(
    loader=PackageLoader("ssg"),
    autoescape=select_autoescape()
)

template = env.get_template("template.html.jinja")
bill_objs = bills.fetch_bills_up_to_date(dt=datetime.datetime(2023, 11, 3))
output = template.render(bills=bill_objs)

with open("output/index.html", "w") as f:
    f.write(output)
