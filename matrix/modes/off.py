from matrix.modes.mode import BaseMode, ModeType


class Off(BaseMode):
    def handle_encoder_push(self):
        self.change_mode(ModeType.MAIN)

    def get_image(self):
        return self.create_image()
