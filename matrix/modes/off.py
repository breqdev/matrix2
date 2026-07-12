from matrix.modes.mode import BaseMode, ModeType
from matrix.utils.config import get_base_image


class Off(BaseMode):
    def handle_encoder_push(self):
        self.change_mode(ModeType.MAIN)

    def get_image(self):
        return get_base_image()
