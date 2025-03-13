import requests
import io

from PIL import Image, ImageDraw

from matrix.resources.fonts import font
from matrix.screens.screen import Screen


class MakeAFish(Screen[Image.Image]):
    CACHE_TTL = 5

    def fetch_data(self):
        data = requests.get("http://makea.fish/fishimg.php?s=11&t=x6362x&f=11").content
        fish = Image.open(io.BytesIO(data))
        fish.thumbnail((64, 64))
        return fish

    def get_image(self):
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, 64, 64), fill="#0000FF")

        image.paste(self.data)

        draw.text((20, 48), text="11:11", font=font, fill="#ffffff")
        draw.text((5, 56), text="make a fish", font=font, fill="#ffffff")

        return image
