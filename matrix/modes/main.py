# stdlib
from datetime import datetime
import time
import logging

# project
from matrix.screens.screen import Screen
from matrix.screens.fish import MakeAFish
from matrix.modes.mode import BaseMode, ChangeMode, ModeType

logger = logging.getLogger(__name__)


def is_eleven_eleven() -> bool:
    now = datetime.now()
    return now.minute == 11 and now.hour in {11, 23}


class Main(BaseMode):
    screen_refresh_rate: float = 5

    def __init__(self, change_mode: ChangeMode, screens: list[Screen]) -> None:
        super().__init__(change_mode)

        self.screens = screens
        self.screen_index: int = 0

        self.fish: MakeAFish | None = None
        self.next_refresh_time = time.time() + self.screen_refresh_rate

    def handle_encoder_clockwise(self):
        self.screen_index += 1
        self.next_refresh_time = time.time() + 10

    def handle_encoder_counterclockwise(self):
        self.screen_index -= 1
        self.next_refresh_time = time.time() + 10

    def handle_encoder_push(self):
        self.change_mode(ModeType.MENU)

    def get_image(self):
        if is_eleven_eleven():
            if self.fish is None:
                self.fish = MakeAFish()
            return self.fish.get_image()
        elif self.fish:
            self.fish.cancel()
            self.fish = None

        if time.time() > self.next_refresh_time:
            self.next_refresh_time = time.time() + 5
            self.screen_index += 1

        active_screens = [s for s in self.screens if s.is_active]
        while True:
            screen = active_screens[self.screen_index % len(active_screens)]

            try:
                if result := screen.get_image():
                    return result
            except Exception as e:
                logger.exception("Exception drawing image for %s: %s", screen.__class__.__name__, e)

            self.screen_index += 1
