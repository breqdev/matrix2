from pathlib import Path
from subprocess import Popen, run
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

import socket
import os

SOCKET_PATH = "/run/matrix/matrix.sock"


class Matter:
    def __init__(self, brightness: Brightness) -> None:
        # self.add_device(ScreenControl(brightness))  # type: ignore
        pass

    def listen(self):
        Path(SOCKET_PATH).parent.mkdir(parents=True, exist_ok=True)
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(SOCKET_PATH)
            server.listen(1)
            print(f"Listening on {SOCKET_PATH}")

            while True:
                conn, _ = server.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        print(f"Received: {data.decode()}")
                        conn.sendall(b"Hello from Python!")

    def start(self):
        Thread(target=self.listen).start()
        Popen(["/home/pi/.bun/bin/bun", "run", "start"], cwd="./matter")
