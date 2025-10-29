# stdlib
import logging
import sys
import threading

# project
from matrix.modes.brightness import Brightness
from matrix.modes.main import Main
from matrix.modes.menu import Menu
from matrix.modes.mode import BaseMode, ModeType
from matrix.modes.network import Network
from matrix.modes.off import Off
from matrix.modes.screens import Screens
from matrix.screens.bluebikes import BlueBikes
from matrix.screens.mbta import MBTA
from matrix.screens.screen import Screen
from matrix.screens.spotify import Spotify
from matrix.screens.weather import Weather
from matrix.utils.config import parse_config
from matrix.utils.no_connection import get_image_no_connection
from matrix.utils.panels import PanelSize
from matrix.web_ui import WebUI

logger = logging.getLogger(__name__)


class App:
    def __init__(self) -> None:
        self.config = parse_config()

        match self.config["panel"]["size"]:
            case "64x64":
                self.panel = PanelSize.PANEL_64x64
            case "64x32":
                self.panel = PanelSize.PANEL_64x32
            case unknown:
                raise ValueError(f"Unexpected panel size: {unknown}")

        if self.config["panel"]["simulation"]:
            self.hardware = None
        else:
            from matrix.utils.hardware import Hardware

            self.hardware = Hardware(self.panel, self.config["panel"]["brightness"])

        screens: list[Screen] = [
            MBTA(self.config["screens"]["mbta"], self.panel),
            Spotify(self.config["screens"]["spotify"], self.panel),
            Weather(self.config["screens"]["weather"], self.panel),
            # Forecast(self.config["screens"]["forecast"], self.panel),
            BlueBikes(self.config["screens"]["bluebikes"], self.panel),
        ]
        self.modes: dict[ModeType, BaseMode] = {
            ModeType.MAIN: Main(self.change_mode, self.panel, screens),
            ModeType.MENU: Menu(self.change_mode, self.panel),
            ModeType.SCREENS: Screens(self.change_mode, self.panel, screens),
            ModeType.OFF: Off(self.change_mode, self.panel),
        }

        if self.hardware is not None:
            self.modes[ModeType.BRIGHTNESS] = Brightness(self.change_mode, self.panel, hardware=self.hardware)
            self.hardware.dial.when_rotated_clockwise = self.handle_rotation_clockwise
            self.hardware.dial.when_rotated_counter_clockwise = self.handle_rotation_counterclockwise
            self.hardware.button.when_pressed = self.handle_press

        if sys.platform == "linux":
            self.modes[ModeType.NETWORK] = Network(self.change_mode, self.panel)

        self.active_mode: ModeType = ModeType.MAIN

        self.ui = WebUI(
            port=8080 if self.config["panel"]["simulation"] else 80,
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
                    mode = self.modes[self.active_mode]
                    image = mode.get_image()
                except Exception as e:
                    logger.exception("Exception when drawing image: %s", e)
                    image = get_image_no_connection(self.panel)

                if image != prev_image:  # Only send the image if it's different
                    self.ui.send_frame(image)
                    if self.hardware is not None:
                        self.hardware.matrix.SetImage(image.convert("RGB"))
                    prev_image = image
                if self.signal_update.wait(timeout=1 / 30):
                    self.signal_update.clear()
        finally:
            if self.hardware is not None:
                self.hardware.matrix.Clear()
