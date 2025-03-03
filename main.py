# stdlib
import logging

# 3p
from PIL.Image import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore
from gpiozero import RotaryEncoder, Button
from dotenv import load_dotenv
from datadog import initialize
from json_log_formatter import JSONFormatter

load_dotenv()
initialize(statsd_disable_buffering=False)

# project
from matrix.app import App, Config


matrix_options = RGBMatrixOptions()
matrix_options.rows = 64
matrix_options.cols = 64
matrix_options.drop_privileges = False

matrix = RGBMatrix(options=matrix_options)

dial = RotaryEncoder(8, 7, max_steps=1024, wrap=True)
button = Button(25)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(filename="/var/log/matrix2.log")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)


try:
    app = App(Config(), dial, button, logger)
    prev: Image | None = None
    for screen in app:
        if prev is not screen:
            matrix.SetImage(screen.convert("RGB"))
            prev = screen
finally:
    matrix.Clear()
