import requests
import io

from PIL import Image, ImageDraw

from matrix.resources.fonts import font
from matrix.screens.screen import REQUEST_DEFAULT_TIMEOUT, Screen


class MakeAFish(Screen[Image.Image]):
    CACHE_TTL = 5

    def fetch_data(self):
        data = requests.get(
            "http://makea.fish/fishimg.php?s=11&t=x6362x&f=11",
            timeout=REQUEST_DEFAULT_TIMEOUT,
        ).content
        fish = Image.open(io.BytesIO(data))
        fish.thumbnail((64, 64))
        return fish

    def fallback_data(self):
        # transparent image
        return Image.new("RGBA", (64, 64), (0, 0, 0, 0))

    def get_image(self):
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, 64, 64), fill="#0000FF")

        image.paste(self.data)

        draw.text((20, 48), text="11:11", font=font, fill="#ffffff")
        draw.text((5, 56), text="make a fish", font=font, fill="#ffffff")

        return image
