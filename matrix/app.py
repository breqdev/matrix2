from collections.abc import Callable
from dataclasses import dataclass
from itertools import cycle
from PIL.Image import Image
from gpiozero import RotaryEncoder, Button

from matrix.bluebikes import get_image_bluebikes
from matrix.mbta import get_image_mbta
from matrix.spotify import get_image_spotify
from matrix.weather import get_image_weather

MAX_BRIGHTNESS = 100


@dataclass
class Config:
    brightness: int = MAX_BRIGHTNESS


IMAGE_GENERATORS: dict[str, Callable[[], Image | None]] = {
    "mbta": get_image_mbta,
    "spotify": get_image_spotify,
    "weather": get_image_weather,
    "bluebikes": get_image_bluebikes,
}
GENERATORS = cycle(IMAGE_GENERATORS.items())


@dataclass
class App:
    config: Config
    in_menu: bool = False
    dial = RotaryEncoder(8, 7, max_steps=1024, wrap=True)
    button = Button(25)

    image: Image | None = None
