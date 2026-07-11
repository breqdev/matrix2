import io
import subprocess

from PIL import Image, ImageDraw
from cairosvg import svg2png

from matrix.resources.fonts import font
from matrix.screens.screen import Screen

class MakeAFish(Screen[tuple[Image.Image, Image.Image]]):
    CACHE_TTL = 5

    def fetch_data(self):
        svg = subprocess.run(["bun", "scripts/amy_fish.js"], capture_output=True, text=True).stdout
        data = svg2png(bytestring=svg.encode('utf-8'))
        fish = Image.open(io.BytesIO(data))

        fish_64x64 = fish.copy().resize((64, 48))

        fish_64x32 = fish.copy()
        fish_64x32.thumbnail((64, 32))
        return fish_64x64, fish_64x32

    def fallback_data(self):
        # transparent image
        blank_64x64 = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        blank_64x32 = Image.new("RGBA", (64, 32), (0, 0, 0, 0))

        return blank_64x64, blank_64x32

    def get_image_64x64(self):
        image = self.size.value.image()
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, 64, 64), fill="#0000F4")

        image.paste(self.data[0])

        draw.text((5, 48), text="11:11 make", font=font, fill="#ffffff")
        draw.text((5, 56), text="an Amy fish", font=font, fill="#ffffff")

        return image

    def get_image_64x32(self):
        image = self.size.value.image()
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, 64, 32), fill="#0000FF")

        image.paste(self.data[1])

        draw.text((39, 25), text="11:11", font=font, fill="#ffffff")

        return image
