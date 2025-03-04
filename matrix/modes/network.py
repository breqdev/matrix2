from collections.abc import Callable
from typing import NamedTuple
from PIL import Image, ImageDraw
from matrix.modes.mode import BaseMode, ModeType
from matrix.resources.fonts import font
import subprocess


class Network(BaseMode):
    def __init__(self, change_mode: Callable[[ModeType], None]) -> None:
        super().__init__(change_mode)
        self.network_info = get_network_info()

    def handle_encoder_push(self):
        self.change_mode(ModeType.MAIN)

    def get_image(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((2, 1), text="Network Info", font=font, fill="#ffffff")
        draw.line((0, 8, 64, 8), fill="#888888")

        draw.text((1, 12), text="SSID", font=font, fill="#888888")
        draw.text((1, 20), text=self.network_info.ssid, font=font, fill="#ffffff")

        draw.text((1, 30), text="IP Address", font=font, fill="#888888")
        draw.text((1, 38), text=self.network_info.ip_addr, font=font, fill="#ffffff")

        # draw.text((1, 48), text="IP Address", font=font, fill="#888888")
        # draw.text((1, 56), text=self.network_info.ip_addr, font=font, fill="#ffffff")

        return image


class NetworkInfo(NamedTuple):
    ssid: str
    ip_addr: str


def get_ip_addr() -> str:
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))
    addr = s.getsockname()[0]
    s.close()
    return addr


def get_ssid() -> str:
    result = subprocess.run(["iw", "dev", "wlan0", "link"], capture_output=True)
    lines = result.stdout.decode().splitlines()
    for line in lines:
        if line.strip().startswith("SSID: "):
            return line.strip().removeprefix("SSID: ")
    raise ValueError("command failed")


def get_network_info() -> NetworkInfo:
    return NetworkInfo(
        ssid=get_ssid(),
        ip_addr=get_ip_addr(),
    )
