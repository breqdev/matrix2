from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore
from gpiozero import RotaryEncoder, Button


class Hardware:
    matrix: RGBMatrix
    dial: RotaryEncoder
    button: Button

    def __init__(self):
        matrix_options = RGBMatrixOptions()
        matrix_options.rows = 64
        matrix_options.cols = 64
        matrix_options.drop_privileges = False

        self.matrix = RGBMatrix(options=matrix_options)
        self.matrix.brightness = 0.6

        self.dial = RotaryEncoder(8, 7, max_steps=1024, wrap=True, bounce_time=0.1)
        self.button = Button(25, bounce_time=0.1)
