import time
from PIL import Image, ImageDraw, ImageFont

from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore


matrix_options = RGBMatrixOptions()
matrix_options.rows = 64
matrix_options.columns = 64
# options.drop_privileges = False

matrix = RGBMatrix(options=matrix_options)

font = ImageFont.load("6x13.pil")

try:
    while True:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)
        draw.text((16, 1), "Hello World!", font=font, fill="#FFFFFF")

        matrix.SetImage(image.convert("RGB"))
        time.sleep(0.1)

finally:
    matrix.Clear()
