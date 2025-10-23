from PIL import Image
from matrix.modes.mode import BaseMode, ModeType


class Off(BaseMode):
    def handle_encoder_push(self):
        self.change_mode(ModeType.MAIN)

    def get_image_64x64(self):
        return Image.new("RGB", (64, 64))

    def get_image_64x32(self):
        return Image.new("RGB", (64, 32))
