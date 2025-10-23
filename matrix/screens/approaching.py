import datetime

from PIL import Image, ImageDraw

from matrix.resources.fonts import font
from matrix.screens.screen import Screen


class Approaching(Screen[None]):
    def fetch_data(self) -> None:
        return None

    def fallback_data(self):
        return None

    def get_image_64x64(self):
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        time_str = datetime.datetime.now().strftime("%H:%M")
        draw.text((39, 1), f"{time_str:>5}", font=font, fill="#FFAA00")

        for i, (label, wait) in list(
            enumerate(
                [
                    ("dial a fish", datetime.timedelta(minutes=5)),
                    ("make a fish", datetime.timedelta(minutes=5)),
                    # "make a wiish", datetime.timedelta(minutes=5),
                    ("ssh a fish", datetime.timedelta(minutes=5)),
                    ("spin a fish", datetime.timedelta(minutes=5)),
                    # "X11:11 a fish", datetime.timedelta(minutes=5),
                    ("bake a dish", datetime.timedelta(minutes=5)),
                    ("make a seq.", datetime.timedelta(minutes=5)),
                ]
            )
        ):
            time_str = str(int(wait / datetime.timedelta(minutes=1)))
            draw.text((1, 12 + 9 * i), f"{label:<8}", font=font, fill="#FFAA00")
            draw.text((47, 12 + 9 * i), f"{time_str:>2}", font=font, fill="#FFAA00")
            draw.text((59, 12 + 9 * i), "m", font=font, fill="#FFAA00")

        return image

    def get_image_64x32(self):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)

        time_str = datetime.datetime.now().strftime("%H:%M")
        draw.text((39, 1), f"{time_str:>5}", font=font, fill="#FFAA00")

        for i, (label, wait) in list(
            enumerate(
                [
                    ("make a fish", datetime.timedelta(minutes=5)),
                    ("bake a dish", datetime.timedelta(minutes=5)),
                    ("make a seq.", datetime.timedelta(minutes=5)),
                ]
            )
        ):
            time_str = str(int(wait / datetime.timedelta(minutes=1)))
            draw.text((1, 12 + 9 * i), f"{label:<8}", font=font, fill="#FFAA00")
            draw.text((47, 12 + 9 * i), f"{time_str:>2}", font=font, fill="#FFAA00")
            draw.text((59, 12 + 9 * i), "m", font=font, fill="#FFAA00")

        return image
