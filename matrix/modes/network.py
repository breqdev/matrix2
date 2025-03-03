from PIL import Image, ImageDraw
from matrix.utils.network import get_network_info
from matrix.modes.mode import BaseMode, ModeName
from matrix.resources.fonts import font


class Network(BaseMode):
    def handle_encoder_clockwise(self):
        pass

    def handle_encoder_counterclockwise(self):
        pass

    def handle_encoder_push(self):
        self.change_mode(ModeName.MAIN)

    def get_image(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((2, 1), text="Network Info", font=font, fill="#ffffff")
        draw.line((0, 8, 64, 8), fill="#888888")

        network_info = get_network_info()

        draw.text((1, 12), text="SSID", font=font, fill="#888888")
        draw.text((1, 20), text=network_info.ssid, font=font, fill="#ffffff")

        draw.text((1, 30), text="IP Address", font=font, fill="#888888")
        draw.text((1, 38), text=network_info.ip_addr, font=font, fill="#ffffff")

        # draw.text((1, 48), text="IP Address", font=font, fill="#888888")
        # draw.text((1, 56), text=network_info.ip_addr, font=font, fill="#ffffff")

        return image
