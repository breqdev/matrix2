from typing import TYPE_CHECKING

from PIL import Image, ImageDraw
from matrix.modes.mode import BaseMode, ChangeMode, ModeType
from matrix.resources.fonts import font, bigfont

if TYPE_CHECKING:
    from matrix.utils.hardware import Hardware


BRIGHTNESS_STEP = 10


class Brightness(BaseMode):
    def __init__(self, change_mode: ChangeMode, *, hardware: "Hardware | None"):
        super().__init__(change_mode)
        if hardware:
            self.matrix = hardware.matrix
        else:
            self.matrix = None

    def handle_encoder_push(self):
        self.change_mode(ModeType.MAIN)

    def handle_encoder_clockwise(self):
        if self.matrix.brightness + BRIGHTNESS_STEP >= 100:
            self.matrix.brightness = 100
        else:
            self.matrix.brightness += 10

    def handle_encoder_counterclockwise(self):
        if self.matrix.brightness - BRIGHTNESS_STEP <= 0:
            self.matrix.brightness = 0
        else:
            self.matrix.brightness -= 10

    def get_image(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((2, 1), text=" Brightness ", font=font, fill="#888888")
        draw.line((0, 8, 64, 8), fill="#888888")

        draw.text(
            (32 - 3 * len(f"{self.matrix.brightness}%"), 16),
            text=f"{self.matrix.brightness}%",
            font=bigfont,
            fill="#ffffff",
        )

        draw.rectangle((1, 32, 62, 40), outline="#ffffff")
        draw.rectangle(
            (1, 32, 1 + int(61 * self.matrix.brightness / 100), 40), fill="#ffffff"
        )

        return image
