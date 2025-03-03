from typing import Any
import requests
import datetime
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw

from matrix.cache import DEFAULT_IMAGE_TTL, ttl_cache
from matrix.fonts import font
from matrix.timed import timed


@ttl_cache(seconds=59)
@timed("bluebikes")
def get_bluebikes_data() -> tuple[Any, Any]:
    with ThreadPoolExecutor() as tpe:
        all_stations_future = tpe.submit(
            requests.get,
            "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_information.json",
        )
        all_statuses_future = tpe.submit(
            requests.get,
            "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json",
        )

    return all_stations_future.result().json(), all_statuses_future.result().json()


@ttl_cache(seconds=DEFAULT_IMAGE_TTL)
def get_image_bluebikes() -> Image.Image:
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    STATIONS = {
        "S32022": "Cedar St",
        "S32013": "Trum Field",
        "S32040": "Lowell St",
        # "S32007": "Ball Sq",
    }

    all_stations, all_status = get_bluebikes_data()

    guids = {}
    for sta_id in STATIONS:
        sta_info = next(s for s in all_stations["data"]["stations"] if s["short_name"] == sta_id)
        guids[sta_id] = sta_info["station_id"]

    status = {}
    for sta_id in STATIONS:
        sta_status = next(s for s in all_status["data"]["stations"] if s["station_id"] == guids[sta_id])
        status[sta_id] = sta_status

    time_str = datetime.datetime.now().strftime("%H:%M")
    draw.text((1, 1), "Bikes", font=font, fill="#2CA3E1")
    draw.text((39, 1), f"{time_str:>5}", font=font, fill="#2CA3E1")

    for i, (sta_id, info) in enumerate(status.items()):
        draw.text((1, 10 + 18 * i), text=STATIONS[sta_id], font=font, fill="#999999")
        image.paste(Image.open("icons/bike.png"), (1, 18 + 18 * i))
        draw.text(
            (12, 19 + 18 * i),
            text=f"{info['num_bikes_available']:0>2}",
            font=font,
            fill="#2CA3E1",
        )
        image.paste(Image.open("icons/ebike.png"), (25, 18 + 18 * i))
        draw.text(
            (31, 19 + 18 * i),
            text=f"{info['num_ebikes_available']:0>2}",
            font=font,
            fill="#b6d3d4",
        )
        image.paste(Image.open("icons/parking.png"), (45, 18 + 18 * i))
        draw.text(
            (53, 19 + 18 * i),
            text=f"{info['num_docks_available']:0>2}",
            font=font,
            fill="#4254f5",
        )

    return image
