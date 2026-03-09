from os import path, remove
from pathlib import Path
from select import select
from socket import AF_UNIX, SOCK_STREAM, socket
from subprocess import Popen
from threading import Thread
from logging import getLogger

from matrix.modes.brightness import MAX_BRIGHTNESS, Brightness
from matrix.modes.mode import ModeType

log = getLogger(__name__)


SOCKET_PATH = "/run/matrix/matrix.sock"


class Matter:
    def __init__(self, brightness: Brightness) -> None:
        self.brightness = brightness
        self.socks: set[socket] = set()

    def handle_command(self, cmd: str) -> None:
        log.info("Unknown command: %s", cmd)

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
                readable, _, _ = select([server] + list(self.socks), [], [])

                if server in readable:
                    conn, _ = server.accept()
                    self.socks.add(conn)

                for s in list(self.socks):
                    if s in readable:
                        try:
                            data = s.recv(1024)
                            if data:
                                msg = data.decode()
                                log.info("Received: %s", msg)
                                self.handle_command(msg)
                            else:
                                s.close()
                                self.socks.discard(s)
                        except (BrokenPipeError, ConnectionResetError, OSError):
                            s.close()
                            self.socks.discard(s)

    def start(self):
        Thread(target=self.listen).start()
        Popen(
            ["/home/pi/.bun/bin/bun", "run", "start"],
            cwd="./matter",
        )
