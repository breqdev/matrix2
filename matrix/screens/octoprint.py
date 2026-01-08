from urllib.parse import urljoin

import requests
from PIL import Image, ImageDraw

from matrix.resources.fonts import font, smallfont
from matrix.utils.panels import PanelSize
from matrix.screens.screen import Screen


class Octoprint(Screen[dict]):
    CACHE_TTL = 5

    def __init__(self, config: dict, size: PanelSize):
        self.api_key = config["api_key"]
        self.endpoint = config["endpoint"]
        self.printer_name = config["printer_name"]

        super().__init__(config, size)

    def _get(self, path: str):
        return requests.get(
            urljoin(self.endpoint, path),
            headers={"Authorization": f"Bearer {self.api_key}"},
        ).json()

    def fetch_data(self):
        is_connected = self._get("/api/connection")["current"]["state"] != "Offline"
        current_job = self._get("/api/job")

        # {
        # "job": {
        #     "file": {
        #     "name": "whistle_v2.gcode",
        #     "origin": "local",
        #     "size": 1468987,
        #     "date": 1378847754
        #     },
        #     "estimatedPrintTime": 8811,
        #     "filament": {
        #     "tool0": {
        #         "length": 810,
        #         "volume": 5.36
        #     }
        #     }
        # },
        # "progress": {
        #     "completion": 0.2298468264184775,
        #     "filepos": 337942,
        #     "printTime": 276,
        #     "printTimeLeft": 912
        # },
        # "state": "Printing"
        # }

        return {
            "is_connected": is_connected,
            "current_job": current_job,
        }

    def fallback_data(self):
        return {
            "is_connected": False,
            "current_job": None,
        }

    @property
    def is_active(self):
        return self.is_enabled and self.data["is_connected"]

    def get_image_64x64(self):
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text(
            (32 - (len(self.printer_name) * 5) // 2, 1),
            text=self.printer_name,
            font=font,
            fill="#77ff00",
        )

        draw.text(
            (1, 10),
            text=self.data["current_job"]["job"]["file"]["name"],
            font=smallfont,
            fill="#AAAAAA",
        )

        elapsed = self.data["current_job"]["progress"]["printTime"]
        remaining = self.data["current_job"]["progress"]["printTimeLeft"]

        draw.text(
            (1, 19),
            text=f"{elapsed // 3600:>2}:{(elapsed % 3600) // 60:02}",
            font=font,
            fill="#FFFFFF",
        )
        draw.text((26, 20), text="e", font=smallfont, fill="#AAAAAA")
        draw.text(
            (32, 19),
            text=f"{remaining // 3600:>2}:{(remaining % 3600) // 60:02}",
            font=font,
            fill="#FFFFFF",
        )
        draw.text((57, 20), text="r", font=smallfont, fill="#AAAAAA")

        draw.rectangle(
            (
                1,
                27,
                1 + int(60 * self.data["current_job"]["progress"]["completion"] / 100),
                30,
            ),
            fill="#00FFFF",
        )
        draw.rectangle((1, 27, 62, 30), outline="#AAAAAA")

        return image

    def get_image_64x32(self):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)

        draw.text(
            (32 - (len(self.printer_name) * 5) // 2, 1),
            text=self.printer_name,
            font=font,
            fill="#77ff00",
        )

        draw.text(
            (1, 10),
            text=self.data["current_job"]["job"]["file"]["name"],
            font=smallfont,
            fill="#AAAAAA",
        )

        elapsed = self.data["current_job"]["progress"]["printTime"]
        remaining = self.data["current_job"]["progress"]["printTimeLeft"]

        draw.text(
            (1, 19),
            text=f"{elapsed // 3600:>2}:{(elapsed % 3600) // 60:02}",
            font=font,
            fill="#FFFFFF",
        )
        draw.text((26, 20), text="e", font=smallfont, fill="#AAAAAA")
        draw.text(
            (32, 19),
            text=f"{remaining // 3600:>2}:{(remaining % 3600) // 60:02}",
            font=font,
            fill="#FFFFFF",
        )
        draw.text((57, 20), text="r", font=smallfont, fill="#AAAAAA")

        draw.rectangle(
            (
                1,
                27,
                1 + int(60 * self.data["current_job"]["progress"]["completion"] / 100),
                30,
            ),
            fill="#00FFFF",
        )
        draw.rectangle((1, 27, 62, 30), outline="#AAAAAA")

        return image
