from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger
from time import sleep
from PIL.Image import Image
from gpiozero import RotaryEncoder, Button

from matrix.bluebikes import BLUEBIKES_REFRESH_INTERVAL, get_image_bluebikes
from matrix.fish import get_image_fish
from matrix.mbta import MBTA_REFRESH_INTERVAL, get_image_mbta
from matrix.no_connection import get_image_no_connection
from matrix.spotify import SPOTIFY_REFRESH_INTERVAL, get_image_spotify
from matrix.weather import WEATHER_REFRESH_INTERVAL, get_image_weather

MAX_BRIGHTNESS = 100


@dataclass
class Config:
    brightness: int = MAX_BRIGHTNESS


@dataclass
class RefreshingImage:
    fetcher: Callable[[], Image | None]
    fetch_interval: int
    image: Image = field(init=False)

    def fetch(self):
        self.image = self.fetcher() or get_image_no_connection()

    def __post_init__(self):
        self.fetch()

    def refresh(self):
        while True:
            self.fetch()
            sleep(self.fetch_interval)


def is_eleven_eleven() -> bool:
    now = datetime.now()
    return now.minute == 11 and now.hour in {11, 23}


@dataclass
class App:
    config: Config
    dial: RotaryEncoder
    button: Button
    log: Logger
    in_menu: bool = False

    screen_refresh_rate: int = 5

    background_executor: ThreadPoolExecutor = field(init=False)
    screen_index: int = 0
    screens: list[RefreshingImage] = field(init=False)

    def __post_init__(self):
        self.background_executor = ThreadPoolExecutor()
        self.screens = [
            RefreshingImage(get_image_mbta, MBTA_REFRESH_INTERVAL),
            RefreshingImage(get_image_spotify, SPOTIFY_REFRESH_INTERVAL),
            RefreshingImage(get_image_weather, WEATHER_REFRESH_INTERVAL),
            RefreshingImage(get_image_bluebikes, BLUEBIKES_REFRESH_INTERVAL),
        ]

        for screen in self.screens:
            self.background_executor.submit(screen.refresh)

        self.background_executor.submit(self.rotate_screen)

    def rotate_screen(self) -> Image:
        while True:
            self.screen_index = (self.screen_index + 1) % len(self.screens)
            sleep(self.screen_refresh_rate)

    def handle_menu(self) -> Image: ...

    def wait_for_button(self, timeout: float = 0.05):
        self.button.wait_for_active(timeout=timeout)
        if self.button.is_active:
            self.button.wait_for_inactive()
            self.in_menu = not self.in_menu

    def __next__(self) -> Image:
        try:
            self.wait_for_button()
            if self.in_menu:
                return self.handle_menu()

            if is_eleven_eleven():
                return get_image_fish()

            return self.screens[self.screen_index].image
        except Exception as e:
            self.log.exception("Exception during rendering", exc_info=e)
            return get_image_no_connection()

    def __iter__(self):
        return self
