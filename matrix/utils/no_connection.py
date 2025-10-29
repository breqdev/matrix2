import datetime

from PIL import Image, ImageDraw

from matrix.resources.fonts import font, bigfont, smallfont
from matrix.utils.panels import PanelSize


def get_image_no_connection(panel: PanelSize) -> Image.Image:
    match panel:
        case PanelSize.PANEL_64x64:
            image = Image.new("RGB", (64, 64))
            draw = ImageDraw.Draw(image)

            time_str = datetime.datetime.now().strftime("%H:%M")
            date_str = datetime.datetime.now().strftime("%m/%d/%y")

            draw.text((18, 10), text=f"{time_str:0>5}", font=bigfont, fill="#ffffff")
            draw.text((12, 28), text=f"{date_str:0>8}", font=font, fill="#ffffff")
            draw.text((7, 52), text="no connection", font=smallfont, fill="#888888")

            return image

        case PanelSize.PANEL_64x32:
            image = Image.new("RGB", (64, 32))
            draw = ImageDraw.Draw(image)

            time_str = datetime.datetime.now().strftime("%H:%M")
            date_str = datetime.datetime.now().strftime("%m/%d/%y")

            draw.text((18, 2), text=f"{time_str:0>5}", font=bigfont, fill="#ffffff")
            draw.text((12, 12), text=f"{date_str:0>8}", font=font, fill="#ffffff")
            draw.text((7, 24), text="no connection", font=smallfont, fill="#888888")

            return image
