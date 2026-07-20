import io
import subprocess
from typing import assert_never

from cairosvg import svg2png
from PIL import Image, ImageDraw

from matrix.resources.fonts import font
from matrix.screens.screen import Screen
from matrix.utils.bun import find_bun
from matrix.utils.config import get_config


class MakeAFish(Screen[tuple[Image.Image, Image.Image]]):
    CACHE_TTL = 5

    def fetch_data(self):
        provider = get_config().screens.fish.provider
        match provider:
            case "amy":
                svg = subprocess.run(
                    [find_bun(), "scripts/amy_fish.js"],
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout
                data = svg2png(bytestring=svg.encode("utf-8"))

                if not data:
                    raise ValueError("No data returned from fish SVG conversion")

                fish_64x48 = Image.open(io.BytesIO(data))
                fish_64x32 = fish_64x48.resize((64, 32))

                return fish_64x48, fish_64x32
            case "makeafish":
                data = self.fetch_url(
                    "http://makea.fish/fishimg.php?s=11&t=x6362x&f=11",
                ).content
                fish = Image.open(io.BytesIO(data))

                fish_64x64 = fish.copy()
                fish_64x64.thumbnail((64, 64))

                fish_64x32 = fish.copy()
                fish_64x32.thumbnail((64, 32))
                return fish_64x64, fish_64x32
            case _:
                assert_never(provider)

    def fallback_data(self):
        # transparent image
        blank_64x64 = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        blank_64x32 = Image.new("RGBA", (64, 32), (0, 0, 0, 0))

        return blank_64x64, blank_64x32

    def get_image_64x64(self):
        image = self.size.empty_image()
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, 64, 64), fill="#0000F4")

        image.paste(self.data[0])

        match get_config().screens.fish.provider:
            case "amy":
                draw.text((5, 48), text="11:11 make", font=font, fill="#ffffff")
                draw.text((5, 56), text="an Amy fish", font=font, fill="#ffffff")
            case "makeafish":
                draw.text((20, 48), text="11:11", font=font, fill="#ffffff")
                draw.text((5, 56), text="make a fish", font=font, fill="#ffffff")

        return image

    def get_image_64x32(self):
        image = self.size.empty_image()
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, 64, 32), fill="#0000FF")

        image.paste(self.data[1])

        draw.text((39, 25), text="11:11", font=font, fill="#ffffff")

        return image
