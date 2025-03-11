# stdlib
from datetime import datetime
import time
import logging

# project
from matrix.screens.screen import Screen
from matrix.screens.bluebikes import BlueBikes
from matrix.screens.fish import MakeAFish
from matrix.screens.mbta import MBTA
from matrix.screens.spotify import Spotify
from matrix.screens.weather import Weather
from matrix.modes.mode import BaseMode, ModeType

logger = logging.getLogger(__name__)


def is_eleven_eleven() -> bool:
    now = datetime.now()
    return now.minute == 11 and now.hour in {11, 23}


class Main(BaseMode):
    screen_refresh_rate: float = 5
    screen_index: int = 0
    screens: list[Screen]

    next_refresh_time = time.time() + screen_refresh_rate

    def __init__(self, change_mode):
        super().__init__(change_mode)

        self.screens = [
            MBTA(),
            Spotify(),
            Weather(),
            BlueBikes(),
        ]

        self.fish: MakeAFish | None = None

    def handle_encoder_clockwise(self):
        self.screen_index += 1
        self.next_refresh_time = time.time() + 10

    def handle_encoder_counterclockwise(self):
        self.screen_index += len(self.screens) - 1
        self.next_refresh_time = time.time() + 10

    def handle_encoder_push(self):
        self.change_mode(ModeType.MENU)

    def get_image(self):
        if is_eleven_eleven():
            if self.fish is None:
                self.fish = MakeAFish()
            return self.fish.get_image()
        else:
            self.fish = None

        if time.time() > self.next_refresh_time:
            self.next_refresh_time = time.time() + 5
            self.screen_index += 1

        while True:
            screen = self.screens[self.screen_index % len(self.screens)]

            try:
                result = screen.get_image()
            except Exception as e:
                logger.exception("Exception drawing image for %s: %s", screen.__class__.__name__, e)
                continue

            if result is not None:
                return result

            # the previous one decided to skip, move on
            self.screen_index += 1
