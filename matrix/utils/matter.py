from os import path, remove
from pathlib import Path
from socket import AF_UNIX, SOCK_STREAM, socket
from subprocess import Popen
from threading import Thread
from logging import getLogger

from matrix.modes.brightness import MAX_BRIGHTNESS, Brightness
from matrix.modes.mode import ModeType

log = getLogger(__name__)

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


SOCKET_PATH = "/run/matrix/matrix.sock"


class Matter:
    def __init__(self, brightness: Brightness) -> None:
        self.brightness = brightness
        self.socks: set[socket] = set()

    def handle_command(self, cmd: str) -> None:
        match cmd:
            case "on":
                self.brightness.change_mode(ModeType.MAIN)
            case "off":
                self.brightness.change_mode(ModeType.OFF)
            case _:
                try:
                    self.brightness.brightness = int(float(cmd) * MAX_BRIGHTNESS)
                except ValueError:
                    log.error("Unknown command: %s", cmd)

    def send(self, msg: str) -> None:
        broken_socks: set[socket] = set()
        for s in self.socks:
            try:
                s.sendall(msg.encode())
            except (BrokenPipeError, ConnectionResetError):
                print("Socket closed by peer.")
                s.close()
                broken_socks.add(s)
        self.socks.difference_update(broken_socks)

    def on_mode_change(self, mode: ModeType) -> None:
        if mode == ModeType.OFF:
            self.send("off")
        else:
            self.send("on")

    def listen(self):
        Path(SOCKET_PATH).parent.mkdir(parents=True, exist_ok=True)
        if path.exists(SOCKET_PATH):
            remove(SOCKET_PATH)

        with socket(AF_UNIX, SOCK_STREAM) as server:
            server.bind(SOCKET_PATH)
            server.listen(1)
            log.info("Listening on %s", SOCKET_PATH)

            while True:
                conn, _ = server.accept()
                with conn:
                    self.socks.add(conn)
                    data = conn.recv(1024)
                    if data:
                        log.info("Received: %s", data.decode())

    def start(self):
        Thread(target=self.listen).start()
        Popen(["/home/pi/.bun/bin/bun", "run", "start"], cwd="./matter")
