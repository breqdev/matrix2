# stdlib
import logging
import sys
import threading
from typing import Any

# project
from matrix.modes.brightness import Brightness
from matrix.modes.main import Main
from matrix.modes.menu import Menu
from matrix.modes.mode import BaseMode, ModeType
from matrix.modes.network import Network
from matrix.modes.off import Off
from matrix.modes.screens import Screens
from matrix.screens.bluebikes import BlueBikes
from matrix.screens.forecast import Forecast
from matrix.screens.mbta import MBTA
from matrix.screens.screen import Screen
from matrix.screens.spotify import Spotify
from matrix.screens.weather import Weather
from matrix.utils.config_singleton import get_config
from matrix.utils.matter import Matter
from matrix.utils.no_connection import get_image_no_connection
from matrix.web_ui import WebUI

logger = logging.getLogger(__name__)


class App:
    def __init__(self) -> None:
        self.config = get_config()

        self.panel = self.config.panel_size

        self.matter = None
        if self.config.is_simulated:
            self.hardware = None
        else:
            from matrix.utils.hardware import Hardware

            self.hardware = Hardware(self.panel, self.config.panel_brightness)

        screens: list[Screen[Any]] = [
            MBTA(self.config.screens.get("mbta", {}), self.panel),
            Spotify(self.config.screens.get("spotify", {}), self.panel),
            Weather(self.config.screens.get("weather", {}), self.panel),
            Forecast(self.config.screens.get("forecast", {}), self.panel),
            BlueBikes(self.config.screens.get("bluebikes", {}), self.panel),
            # Octoprint(self.config.screens.get("octoprint", {}), self.panel),
        ]
        self.modes: dict[ModeType, BaseMode] = {
            ModeType.MAIN: Main(self.change_mode, self.panel, screens, self.config),
            ModeType.MENU: Menu(self.change_mode, self.panel),
            ModeType.SCREENS: Screens(self.change_mode, self.panel, screens),
            ModeType.OFF: Off(self.change_mode, self.panel),
        }

        if self.hardware is not None:
            brightness = Brightness(self.change_mode, self.panel, hardware=self.hardware)
            self.modes[ModeType.BRIGHTNESS] = brightness
            if not self.config.is_simulated and self.config.screens.get("matter"):
                self.matter = Matter(brightness)
                self.matter.start()
            self.hardware.dial.when_rotated_clockwise = self.handle_rotation_clockwise
            self.hardware.dial.when_rotated_counter_clockwise = self.handle_rotation_counterclockwise
            self.hardware.button.when_pressed = self.handle_press

        if sys.platform == "linux":
            self.modes[ModeType.NETWORK] = Network(self.change_mode, self.panel)

        self.active_mode: ModeType = ModeType.MAIN

        self.ui = WebUI(
            port=8080 if self.config.is_simulated else 80,
            on_rotation_clockwise=self.handle_rotation_clockwise,
            on_rotation_counterclockwise=self.handle_rotation_counterclockwise,
            on_press=self.handle_press,
        )

        self.signal_update = threading.Event()

    def change_mode(self, mode: ModeType) -> None:
        self.active_mode = mode
        if self.matter and mode in (ModeType.OFF, ModeType.MAIN):
            self.matter.on_mode_change(mode)

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
                    mode = self.modes[self.active_mode]
                    image = mode.get_image()
                except Exception as e:
                    logger.exception("Exception when drawing image: %s", e)
                    image = get_image_no_connection(self.panel)

                if image != prev_image and image is not None:  # Only send the image if it's different
                    self.ui.send_frame(image)
                    if self.hardware is not None:
                        self.hardware.matrix.SetImage(image.convert("RGB"))
                    prev_image = image
                if self.signal_update.wait(timeout=1 / 30):
                    self.signal_update.clear()
        finally:
            if self.hardware is not None:
                self.hardware.matrix.Clear()
