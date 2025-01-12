import requests
import io

from PIL import Image, ImageDraw

from matrix.fonts import font

def get_image_fish() -> Image.Image:
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, 64, 64), fill="#0000FF")

    data = requests.get("http://makea.fish/fishimg.php?s=11&t=x6362x&f=11").content
    fish = Image.open(io.BytesIO(data))
    fish.thumbnail((64, 64))

    image.paste(fish)

    draw.text((20, 48), text="11:11", font=font, fill="#ffffff")
    draw.text((5, 56), text="make a fish", font=font, fill="#ffffff")

    return image
