from PIL import Image
from dotenv import load_dotenv

load_dotenv()

from matrix.bluebikes import get_image_bluebikes
from matrix.fish import get_image_fish
from matrix.mbta import get_image_mbta
from matrix.spotify import get_image_spotify
from matrix.weather import get_image_weather


image = get_image_fish()
image = image.resize((256, 256), Image.NEAREST)
image.save("previews/fish.png")

image = get_image_mbta()
image = image.resize((256, 256), Image.NEAREST)
image.save("previews/mbta.png")

image = get_image_weather()
image = image.resize((256, 256), Image.NEAREST)
image.save("previews/weather.png")

image = get_image_bluebikes()
image = image.resize((256, 256), Image.NEAREST)
image.save("previews/bluebikes.png")
