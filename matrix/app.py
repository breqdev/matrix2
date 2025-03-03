# stdlib
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger
from time import sleep

# 3p
from PIL.Image import Image
from gpiozero import RotaryEncoder, Button

# project
from matrix.bluebikes import get_image_bluebikes
from matrix.cache import DEFAULT_IMAGE_TTL
from matrix.fish import get_image_fish
from matrix.mbta import get_image_mbta
from matrix.menu import Menu
from matrix.no_connection import get_image_no_connection
from matrix.spotify import get_image_spotify
from matrix.weather import get_image_weather

MAX_BRIGHTNESS = 100


@dataclass
class Config:
    brightness: int = MAX_BRIGHTNESS


@dataclass
class RefreshingImage:
    fetcher: Callable[[], Image | None]
    fetch_interval: int = DEFAULT_IMAGE_TTL
    image: Image | None = None

    def fetch(self):
        self.image = self.fetcher() or self.image

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
    menu: Menu = field(init=False)
    screen_refresh_rate: float = 5
    background_executor: ThreadPoolExecutor = field(init=False)
    screen_index: int = 0
    screens: list[RefreshingImage] = field(init=False)

    def __post_init__(self):
        self.menu = Menu(self.dial, self.button)
        self.background_executor = ThreadPoolExecutor()
        self.screens = [
            RefreshingImage(get_image_mbta),
            RefreshingImage(get_image_spotify),
            RefreshingImage(get_image_weather),
            RefreshingImage(get_image_bluebikes),
        ]

        for screen in self.screens:
            self.background_executor.submit(screen.refresh)

        self.background_executor.submit(self.rotate_screen)

        self.dial.when_rotated_clockwise = self.handle_rotation_clockwise
        self.dial.when_rotated_counter_clockwise = self.handle_rotation_counter_clockwise

    def get_screen(self, index: int) -> Image:
        if all(screen.image is None for screen in self.screens):
            return get_image_no_connection()
        screens = [screen.image for screen in self.screens if screen.image is not None]
        return screens[index % len(screens)]

    def handle_rotation_clockwise(self):
        if self.in_menu:
            self.menu.handle_rotation_clockwise()
        else:
            self.screen_index += 1

    def handle_rotation_counter_clockwise(self):
        if self.in_menu:
            self.menu.handle_rotation_counter_clockwise()
        else:
            self.screen_index -= 1

    def rotate_screen(self) -> Image:
        while True:
            if not self.in_menu:
                self.handle_rotation_clockwise()
            sleep(self.screen_refresh_rate)

    def wait_for_button(self, timeout: float = 0.05):
        self.button.wait_for_active(timeout=timeout)
        if self.button.is_active:
            self.button.wait_for_inactive()
            self.in_menu = True

    def __next__(self) -> Image:
        try:
            if self.in_menu:
                exit_menu = self.menu.wait_for_button()
                if exit_menu:
                    self.in_menu = False
                else:
                    return self.menu.draw()

            self.wait_for_button()
            if is_eleven_eleven():
                return get_image_fish()

            return self.get_screen(self.screen_index)
        except Exception:
            self.log.exception("Exception during rendering")
            return get_image_no_connection()

    def __iter__(self):
        return self
