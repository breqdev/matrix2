# stdlib
import logging

# 3p
from dotenv import load_dotenv
from datadog import initialize
from json_log_formatter import JSONFormatter

load_dotenv()
initialize(statsd_disable_buffering=False)

# project
from matrix.app import App


logging.basicConfig(level=logging.INFO, handlers=[])
handler = logging.FileHandler(filename="/var/log/matrix2.log")
handler.setFormatter(JSONFormatter())
# Add our handler to the root logger
logging.getLogger("").addHandler(handler)

app = App()
app.run()
