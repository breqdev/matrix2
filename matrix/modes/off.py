from PIL import Image
from matrix.modes.mode import BaseMode, ModeType

BLANK_IMAGE = Image.new("RGB", (64, 64))


class Off(BaseMode):
    def handle_encoder_push(self):
        self.change_mode(ModeType.MAIN)

    def get_image(self):
        return BLANK_IMAGE
