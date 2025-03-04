from collections.abc import Callable
from typing import NamedTuple
from PIL import Image, ImageDraw
from matrix.modes.mode import BaseMode, ModeType
from matrix.resources.fonts import font
import subprocess
import qrcode


class Network(BaseMode):
    def __init__(self, change_mode: Callable[[ModeType], None]) -> None:
        super().__init__(change_mode)
        self.network_info = get_network_info()

        self.show_qr_code = False

    def handle_encoder_push(self):
        self.change_mode(ModeType.MAIN)

    def handle_encoder_clockwise(self):
        self.show_qr_code = not self.show_qr_code

    def handle_encoder_counterclockwise(self):
        self.show_qr_code = not self.show_qr_code

    def get_image(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        if self.show_qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.ERROR_CORRECT_L,
                box_size=2,
                border=1,
            )
            qr.add_data(f"http://{self.network_info.ip_addr}/")
            qr.make(fit=True)

            img = qr.make_image(fill_color="#888888", back_color="#000000")
            image_width_px = (img.width + img.border * 2) * img.box_size
            padding = (64 - image_width_px) // 2
            image.paste(img.get_image(), (padding, padding))

        else:
            draw.text((2, 1), text="Network Info", font=font, fill="#ffffff")
            draw.line((0, 8, 64, 8), fill="#888888")

            draw.text((1, 12), text="SSID", font=font, fill="#888888")
            draw.text((1, 20), text=self.network_info.ssid, font=font, fill="#ffffff")

            draw.text((1, 30), text="IP Address", font=font, fill="#888888")
            draw.text(
                (1, 38), text=self.network_info.ip_addr, font=font, fill="#ffffff"
            )

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
