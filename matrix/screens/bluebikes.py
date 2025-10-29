from typing import Any
import requests
import datetime
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw

from matrix.resources.fonts import font, smallfont
from matrix.screens.screen import REQUEST_DEFAULT_TIMEOUT, Screen


class BlueBikes(Screen[tuple[Any, Any] | None]):
    CACHE_TTL = 60

    def fetch_data(self):
        with ThreadPoolExecutor() as tpe:
            all_stations_future = tpe.submit(
                requests.get,
                "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_information.json",
                timeout=REQUEST_DEFAULT_TIMEOUT,
            )
            all_statuses_future = tpe.submit(
                requests.get,
                "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json",
                timeout=REQUEST_DEFAULT_TIMEOUT,
            )

        return all_stations_future.result().json(), all_statuses_future.result().json()

    def fallback_data(self):
        return None

    def get_image_64x64(self):
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        STATIONS = {
            "S32022": "Cedar St",
            "S32013": "Trum Field",
            "S32040": "Lowell St",
            # "S32007": "Ball Sq",
        }

        time_str = datetime.datetime.now().strftime("%H:%M")
        draw.text((1, 1), "Bikes", font=font, fill="#2CA3E1")
        draw.text((39, 1), f"{time_str:>5}", font=font, fill="#2CA3E1")

        if self.data is None:
            time_str = datetime.datetime.now().strftime("%H:%M")

            for i, sta_id in enumerate(STATIONS):
                draw.text((1, 10 + 18 * i), text=STATIONS[sta_id], font=font, fill="#999999")
                image.paste(Image.open("icons/bike.png"), (1, 18 + 18 * i))
                draw.text((12, 19 + 18 * i), text="??", font=font, fill="#2CA3E1")
                image.paste(Image.open("icons/ebike.png"), (25, 18 + 18 * i))
                draw.text((31, 19 + 18 * i), text="??", font=font, fill="#b6d3d4")
                image.paste(Image.open("icons/parking.png"), (45, 18 + 18 * i))
                draw.text((53, 19 + 18 * i), text="??", font=font, fill="#4254f5")

            return image

        all_stations, all_status = self.data

        guids = {}
        for sta_id in STATIONS:
            sta_info = next(s for s in all_stations["data"]["stations"] if s["short_name"] == sta_id)
            guids[sta_id] = sta_info["station_id"]

        status = {}
        for sta_id in STATIONS:
            sta_status = next(s for s in all_status["data"]["stations"] if s["station_id"] == guids[sta_id])
            status[sta_id] = sta_status

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

    def get_image_64x32(self):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)

        STATIONS = {}

        for i in range(len(self.config["stations"])):
            station = self.config["stations"][i]
            STATIONS[station["id"]] = station["label"]

        if self.data is None:
            for i, sta_id in enumerate(STATIONS):
                draw.text((1, 1 + 16 * i), text=STATIONS[sta_id], font=font, fill="#999999")
                image.paste(Image.open("icons/bike.png"), (1, 8 + 16 * i))
                draw.text((12, 9 + 16 * i), text="??", font=font, fill="#2CA3E1")
                image.paste(Image.open("icons/ebike.png"), (25, 8 + 16 * i))
                draw.text((31, 9 + 16 * i), text="??", font=font, fill="#b6d3d4")
                image.paste(Image.open("icons/parking.png"), (45, 8 + 16 * i))
                draw.text((53, 9 + 16 * i), text="??", font=font, fill="#4254f5")

            return image

        all_stations, all_status = self.data

        guids = {}
        for sta_id in STATIONS:
            sta_info = next(s for s in all_stations["data"]["stations"] if s["short_name"] == sta_id)
            guids[sta_id] = sta_info["station_id"]

        status = {}
        for sta_id in STATIONS:
            sta_status = next(s for s in all_status["data"]["stations"] if s["station_id"] == guids[sta_id])
            status[sta_id] = sta_status

        for i, (sta_id, info) in enumerate(status.items()):
            draw.text((1, 1 + 16 * i), text=STATIONS[sta_id], font=smallfont, fill="#999999")
            image.paste(Image.open("icons/bike.png"), (1, 8 + 16 * i))
            draw.text(
                (12, 9 + 16 * i),
                text=f"{info['num_bikes_available']:0>2}",
                font=font,
                fill="#2CA3E1",
            )
            image.paste(Image.open("icons/ebike.png"), (25, 8 + 16 * i))
            draw.text(
                (31, 9 + 16 * i),
                text=f"{info['num_ebikes_available']:0>2}",
                font=font,
                fill="#b6d3d4",
            )
            image.paste(Image.open("icons/parking.png"), (45, 8 + 16 * i))
            draw.text(
                (53, 9 + 16 * i),
                text=f"{info['num_docks_available']:0>2}",
                font=font,
                fill="#4254f5",
            )

        return image
