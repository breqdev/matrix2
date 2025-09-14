# stdlib
import threading
import logging
import sys

# project
from matrix.modes.screens import Screens
from matrix.screens.bluebikes import BlueBikes
from matrix.screens.mbta import MBTA
from matrix.screens.screen import Screen
from matrix.screens.spotify import Spotify
from matrix.screens.weather import Weather
from matrix.screens.forecast import Forecast
from matrix.web_ui import WebUI
from matrix.utils.no_connection import get_image_no_connection

from matrix.modes.mode import ModeType, BaseMode
from matrix.modes.main import Main
from matrix.modes.menu import Menu
from matrix.modes.off import Off
from matrix.modes.brightness import Brightness
from matrix.modes.network import Network


logger = logging.getLogger(__name__)


class App:
    def __init__(self, *, simulation: bool = False) -> None:
        if simulation:
            self.hardware = None
        else:
            from matrix.utils.hardware import Hardware

            self.hardware = Hardware()

        screens: list[Screen] = [
            MBTA(),
            Spotify(),
            Weather(),
            # Forecast(),
            BlueBikes(),
        ]
        self.modes: dict[ModeType, BaseMode] = {
            ModeType.MAIN: Main(self.change_mode, screens),
            ModeType.MENU: Menu(self.change_mode),
            ModeType.SCREENS: Screens(self.change_mode, screens),
            ModeType.OFF: Off(self.change_mode),
        }

        if self.hardware is not None:
            self.modes[ModeType.BRIGHTNESS] = Brightness(
                self.change_mode, hardware=self.hardware
            )
            self.hardware.dial.when_rotated_clockwise = self.handle_rotation_clockwise
            self.hardware.dial.when_rotated_counter_clockwise = (
                self.handle_rotation_counterclockwise
            )
            self.hardware.button.when_pressed = self.handle_press

        if sys.platform == "linux":
            self.modes[ModeType.NETWORK] = Network(self.change_mode)

        self.active_mode: ModeType = ModeType.MAIN

        self.ui = WebUI(
            port=8080 if simulation else 80,
            on_rotation_clockwise=self.handle_rotation_clockwise,
            on_rotation_counterclockwise=self.handle_rotation_counterclockwise,
            on_press=self.handle_press,
        )

        self.signal_update = threading.Event()

    def change_mode(self, mode: ModeType) -> None:
        self.active_mode = mode

    def handle_rotation_clockwise(self):
        self.modes[self.active_mode].handle_encoder_clockwise()
        self.signal_update.set()

    def handle_rotation_counterclockwise(self):
        self.modes[self.active_mode].handle_encoder_counterclockwise()
        self.signal_update.set()

    def handle_press(self):
        self.modes[self.active_mode].handle_encoder_push()
        self.signal_update.set()

    def run(self):
        try:
            prev_image = None
            while True:
                try:
                    image = self.modes[self.active_mode].get_image()
                except Exception as e:
                    logger.exception("Exception when drawing image: %s", e)
                    image = get_image_no_connection()

                if image != prev_image:  # Only send the image if it's different
                    self.ui.send_frame(image)
                    if self.hardware is not None:
                        self.hardware.matrix.SetImage(image.convert("RGB"))
                    prev_image = image
                if self.signal_update.wait(timeout=1 / 10):
                    self.signal_update.clear()
        finally:
            if self.hardware is not None:
                self.hardware.matrix.Clear()
