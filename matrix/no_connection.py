import datetime

from PIL import Image, ImageDraw

from matrix.fonts import font, bigfont, smallfont

def get_image_no_connection() -> Image.Image:
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    time_str = datetime.datetime.now().strftime("%H:%M")
    date_str = datetime.datetime.now().strftime("%m/%d/%y")

    draw.text((18, 10), text=f"{time_str:0>5}", font=bigfont, fill="#ffffff")
    draw.text((12, 28), text=f"{date_str:0>8}", font=font, fill="#ffffff")
    draw.text((7, 52), text="no connection", font=smallfont, fill="#888888")

    return image
