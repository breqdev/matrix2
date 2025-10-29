# stdlib
import argparse
import logging

# 3p
import datadog
from dotenv import load_dotenv
from json_log_formatter import VerboseJSONFormatter

load_dotenv()

# project
from matrix.app import App  # noqa: E402

parser = argparse.ArgumentParser(
    prog="matrix",
    description="LED matrix display driver",
)

parser.add_argument("--simulate", action="store_true")
parser.add_argument("--logfile", default="/var/log/matrix.log")

args = parser.parse_args()

logging.basicConfig(level=logging.INFO)

if not args.simulate:
    datadog.initialize(statsd_disable_buffering=False)

    handler = logging.FileHandler(filename=args.logfile)
    handler.setFormatter(VerboseJSONFormatter())
    # Add our handler to the root logger
    logging.root.addHandler(handler)

app = App()
app.run()
