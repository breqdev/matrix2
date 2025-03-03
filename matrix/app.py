# stdlib
from logging import Logger
import threading

# project
from matrix.web_ui import run_web_ui
from matrix.utils.hardware import Hardware

from matrix.modes.mode import ModeName, BaseMode
from matrix.modes.main import Main
from matrix.modes.menu import Menu
from matrix.modes.off import Off
from matrix.modes.brightness import Brightness
from matrix.modes.network import Network


class App:
    hardware: Hardware
    logger: Logger
    modes: dict[ModeName, BaseMode]
    active_mode: ModeName

    def __init__(self, *, logger: Logger) -> None:
        self.hardware = Hardware()
        self.logger = logger

        self.modes = {
            ModeName.MAIN: Main(self.change_mode),
            ModeName.MENU: Menu(self.change_mode),
            ModeName.OFF: Off(self.change_mode),
            ModeName.BRIGHTNESS: Brightness(self.change_mode),
            ModeName.NETWORK: Network(self.change_mode),
        }
        self.active_mode = ModeName.MAIN

        self.ui_thread = threading.Thread(target=run_web_ui)
        self.ui_thread.start()

        self.hardware.dial.when_rotated_clockwise = self.handle_rotation_clockwise
        self.hardware.dial.when_rotated_counter_clockwise = (
            self.handle_rotation_counter_clockwise
        )
        self.hardware.button.when_pressed = self.handle_press

        self.signal_update = threading.Event()

    def change_mode(self, mode: ModeName) -> None:
        self.active_mode = mode

    def handle_rotation_clockwise(self):
        self.modes[self.active_mode].handle_encoder_clockwise()
        self.signal_update.set()

    def handle_rotation_counter_clockwise(self):
        self.modes[self.active_mode].handle_encoder_counterclockwise()
        self.signal_update.set()

    def handle_press(self):
        self.modes[self.active_mode].handle_encoder_push()
        self.signal_update.set()

    def run(self):
        try:
            while True:
                image = self.modes[self.active_mode].get_image()
                self.hardware.matrix.SetImage(image.convert("RGB"))
                if self.signal_update.wait(timeout=1):
                    self.signal_update.clear()
        finally:
            self.hardware.matrix.Clear()
