from collections.abc import Callable
import time
import datetime
import logging
from itertools import cycle

from PIL.Image import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions

from dotenv import load_dotenv
from datadog import initialize, statsd

load_dotenv()
initialize(statsd_disable_buffering=False)

from matrix.bluebikes import get_image_bluebikes
from matrix.fish import get_image_fish
from matrix.mbta import get_image_mbta
from matrix.spotify import get_image_spotify
from matrix.weather import get_image_weather
from matrix.no_connection import get_image_no_connection
from matrix.transit import get_image_transit


matrix_options = RGBMatrixOptions()
matrix_options.rows = 64
matrix_options.cols = 64
matrix_options.drop_privileges = False

matrix = RGBMatrix(options=matrix_options)

logger = logging.getLogger(__name__)

IMAGE_GENERATORS: dict[str, Callable[[], Image | None]] = {
    "mbta": get_image_mbta,
    "spotify": get_image_spotify,
    "weather": get_image_weather,
    "bluebikes": get_image_bluebikes,
}


def is_eleven_eleven() -> bool:
    return datetime.datetime.now().strftime("%H:%M") in ["11:11", "23:11"]


try:
    for image_type, get_image in cycle(IMAGE_GENERATORS.items()):
        t0 = time.time()
        tags = [f"image:{image_type}"]
        try:
            image = get_image_fish() if is_eleven_eleven() else get_image()
            statsd.gauge("matrix.load_seconds", time.time() - t0, tags=tags)
        except Exception as e:
            logger.exception("Exception during rendering", exc_info=e)
            statsd.increment("matrix.exception", tags=tags)
            image = get_image_no_connection()

        if not image:
            continue

        matrix.SetImage(image.convert("RGB"))
        time.sleep(5)

finally:
    matrix.Clear()
