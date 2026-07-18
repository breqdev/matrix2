from matrix.modes.mode import BaseMode, ModeType
from matrix.utils.config import get_panel_size


class Off(BaseMode):
    def handle_encoder_push(self):
        self.change_mode(ModeType.MAIN)

    def get_image(self):
        return get_panel_size().empty_image()
