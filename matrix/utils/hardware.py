from gpiozero import Button, RotaryEncoder
from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore

from matrix.utils.config import get_config


class Hardware:
    matrix: RGBMatrix
    dial: RotaryEncoder
    button: Button

    def __init__(self):
        config = get_config()
        matrix_options = RGBMatrixOptions()
        matrix_options.cols, matrix_options.rows = config.panel.size.value
        matrix_options.drop_privileges = False
        matrix_options.hardware_mapping = "adafruit-hat-pwm"

        self.matrix = RGBMatrix(options=matrix_options)
        self.matrix.brightness = config.panel.brightness or 60

        self.dial = RotaryEncoder(7, 19, max_steps=1024, wrap=True, bounce_time=0.1)
        self.button = Button(25, bounce_time=0.1)
