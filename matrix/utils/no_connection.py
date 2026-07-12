import datetime
from typing import assert_never

from PIL import Image, ImageDraw

from matrix.resources.fonts import bigfont, font, smallfont
from matrix.utils.config import get_panel_size
from matrix.utils.panels import PanelSize


def get_image_no_connection() -> Image.Image:
    panel = get_panel_size()
    match panel:
        case PanelSize.PANEL_64x64:
            image = panel.value.image()
            draw = ImageDraw.Draw(image)

            time_str = datetime.datetime.now().strftime("%H:%M")
            date_str = datetime.datetime.now().strftime("%m/%d/%y")

            draw.text((18, 10), text=f"{time_str:0>5}", font=bigfont, fill="#ffffff")
            draw.text((12, 28), text=f"{date_str:0>8}", font=font, fill="#ffffff")
            draw.text((7, 52), text="no connection", font=smallfont, fill="#888888")

            return image

        case PanelSize.PANEL_64x32:
            image = panel.value.image()
            draw = ImageDraw.Draw(image)

            time_str = datetime.datetime.now().strftime("%H:%M")
            date_str = datetime.datetime.now().strftime("%m/%d/%y")

            draw.text((18, 2), text=f"{time_str:0>5}", font=bigfont, fill="#ffffff")
            draw.text((12, 12), text=f"{date_str:0>8}", font=font, fill="#ffffff")
            draw.text((7, 24), text="no connection", font=smallfont, fill="#888888")

            return image
        case _:
            assert_never(panel)
