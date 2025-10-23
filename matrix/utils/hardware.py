from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore
from gpiozero import RotaryEncoder, Button

from matrix.utils.panels import PanelSize


class Hardware:
    matrix: RGBMatrix
    dial: RotaryEncoder
    button: Button

    def __init__(self, size: PanelSize, brightness: int | None = None):
        matrix_options = RGBMatrixOptions()
        matrix_options.rows = size.value.rows
        matrix_options.cols = size.value.cols
        matrix_options.drop_privileges = False

        self.matrix = RGBMatrix(options=matrix_options)
        self.matrix.brightness = brightness or 60

        self.dial = RotaryEncoder(7, 19, max_steps=1024, wrap=True, bounce_time=0.1)
        self.button = Button(25, bounce_time=0.1)
