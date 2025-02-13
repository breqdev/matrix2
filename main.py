import time
import datetime
import logging

from PIL import Image
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
IMAGE_TYPES = ["mbta", "spotify", "weather", "bluebikes"]

try:
    tick = 0
    while True:
        tick += 1

        image: Image.Image | None = None

        img_type_tag = "image:" + IMAGE_TYPES[tick % 4]
        t0 = time.time()
        try:
            if datetime.datetime.now().strftime("%H:%M") in ["11:11", "23:11"]:
                image = get_image_fish()
            else:
                match tick % 4:
                    case 0:
                        image = get_image_mbta()
                    case 1:
                        image = get_image_spotify()
                    case 2:
                        image = get_image_weather()
                    case 3:
                        image = get_image_bluebikes()
                # image = get_image_transit(tick % 2)
            statsd.gauge("matrix.load_seconds", time.time() - t0, tags=[img_type_tag])
        except Exception as e:
            logger.exception("Exception during rendering", exc_info=e)
            statsd.increment("matrix.exception", tags=[img_type_tag])
            image = get_image_no_connection()

        if not image:
            continue

        matrix.SetImage(image.convert("RGB"))
        time.sleep(5)

finally:
    matrix.Clear()
