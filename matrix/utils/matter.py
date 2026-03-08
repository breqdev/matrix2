from subprocess import run
from threading import Thread

from matrix.modes.brightness import MAX_BRIGHTNESS, Brightness
from matrix.modes.mode import ModeType


# class ScreenControl(DimmableLight):

#     def __init__(self, brightness: Brightness) -> None:
#         super().__init__("Matrix")
#         self.brightness_controls = brightness

#     def on(self):
#         self.brightness_controls.change_mode(ModeType.MAIN)

#     def off(self):
#         self.brightness_controls.change_mode(ModeType.OFF)

#     @property
#     def brightness(self) -> float:
#         return self.brightness_controls.brightness / MAX_BRIGHTNESS

#     @brightness.setter
#     def brightness(self, value: float):
#         self.brightness_controls.brightness = int(value * MAX_BRIGHTNESS)


class Matter:
    def __init__(self, brightness: Brightness) -> None:
        # self.add_device(ScreenControl(brightness))  # type: ignore
        pass

    def start(self):
        Thread(target=lambda: run, args=(["npm", "run", "app"],)).start()
