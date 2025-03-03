from PIL import Image, ImageDraw
from matrix.modes.mode import BaseMode, ModeName
from matrix.resources.fonts import font, bigfont


class Brightness(BaseMode):
    def handle_encoder_push(self):
        self.change_mode(ModeName.MAIN)

    def get_image(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((2, 1), text=" Brightness ", font=font, fill="#888888")
        draw.line((0, 8, 64, 8), fill="#888888")

        draw.text((8, 16), text="100%", font=bigfont, fill="#ffffff")

        return image
