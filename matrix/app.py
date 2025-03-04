# stdlib
from logging import Logger
import threading

# project
from matrix.web_ui import WebUI
from matrix.utils.hardware import Hardware

from matrix.modes.mode import ModeName, BaseMode
from matrix.modes.main import Main
from matrix.modes.menu import Menu
from matrix.modes.off import Off
from matrix.modes.brightness import Brightness
from matrix.modes.network import Network


class App:
    def __init__(self, *, logger: Logger) -> None:
        self.hardware = Hardware()
        self.logger = logger

        self.modes: dict[ModeName, BaseMode] = {
            ModeName.MAIN: Main(self.change_mode),
            ModeName.MENU: Menu(self.change_mode),
            ModeName.OFF: Off(self.change_mode),
            ModeName.BRIGHTNESS: Brightness(self.change_mode, hardware=self.hardware),
            ModeName.NETWORK: Network(self.change_mode),
        }
        self.active_mode: ModeName = ModeName.MAIN

        self.ui = WebUI(
            on_rotation_clockwise=self.handle_rotation_clockwise,
            on_rotation_counterclockwise=self.handle_rotation_counterclockwise,
            on_press=self.handle_press,
        )

        self.hardware.dial.when_rotated_clockwise = self.handle_rotation_clockwise
        self.hardware.dial.when_rotated_counter_clockwise = (
            self.handle_rotation_counterclockwise
        )
        self.hardware.button.when_pressed = self.handle_press

        self.signal_update = threading.Event()

    def change_mode(self, mode: ModeName) -> None:
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
            while True:
                image = self.modes[self.active_mode].get_image()
                self.ui.send_frame(image)
                self.hardware.matrix.SetImage(image.convert("RGB"))
                if self.signal_update.wait(timeout=1):
                    self.signal_update.clear()
        finally:
            self.hardware.matrix.Clear()
