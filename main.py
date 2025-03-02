# stdlib
from collections.abc import Callable
from itertools import cycle
import time
import datetime
import logging

# 3p
from PIL.Image import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore
from gpiozero import RotaryEncoder, Button
from dotenv import load_dotenv
from datadog import initialize, statsd
from json_log_formatter import JSONFormatter

# project
from matrix.bluebikes import get_image_bluebikes
from matrix.fish import get_image_fish
from matrix.mbta import get_image_mbta
from matrix.spotify import get_image_spotify
from matrix.weather import get_image_weather
from matrix.no_connection import get_image_no_connection
from matrix.menu import draw_menu

load_dotenv()
initialize(statsd_disable_buffering=False)


matrix_options = RGBMatrixOptions()
matrix_options.rows = 64
matrix_options.cols = 64
matrix_options.drop_privileges = False

matrix = RGBMatrix(options=matrix_options)

dial = RotaryEncoder(8, 7, max_steps=1024, wrap=True)
button = Button(25)

logger = logging.getLogger(__name__)
handler = logging.FileHandler(filename="/var/log/matrix2.log")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

IMAGE_GENERATORS: dict[str, Callable[[], Image | None]] = {
    "mbta": get_image_mbta,
    "spotify": get_image_spotify,
    "weather": get_image_weather,
    "bluebikes": get_image_bluebikes,
}
GENERATORS = cycle(IMAGE_GENERATORS.items())


def is_eleven_eleven() -> bool:
    now = datetime.datetime.now()
    return now.minute == 11 and now.hour in {11, 23}


menu = False


try:
    while True:
        if menu:
            dial.value = 0
            image = draw_menu(dial)
            matrix.SetImage(image.convert("RGB"))

            button.wait_for_active(timeout=0.1)
            if button.is_active:
                button.wait_for_inactive()
                print("Moving to display page")
                menu = False
        else:
            image_type, get_image = next(GENERATORS)

            t0 = time.time()
            try:
                if is_eleven_eleven():
                    image: Image | None = get_image_fish()
                    image_type = "fish"
                else:
                    image = get_image()
                statsd.gauge(
                    "matrix.load_seconds",
                    time.time() - t0,
                    tags=[f"image:{image_type}"],
                )
            except Exception as e:
                logger.exception("Exception during rendering", exc_info=e)
                statsd.increment("matrix.exception", tags=[f"image:{image_type}"])
                image = get_image_no_connection()

            if not image:
                continue

            matrix.SetImage(image.convert("RGB"))

            # move on once we're ready for the next image,
            # or if the user tries to enter the menu
            button.wait_for_active(timeout=5.0)
            if button.is_active:
                button.wait_for_inactive()
                print("Moving to menu page")
                menu = True


finally:
    matrix.Clear()
