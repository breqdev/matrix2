import datetime

from PIL import ImageDraw

from matrix.resources.fonts import font
from matrix.screens.screen import Screen
from matrix.utils.panels import PanelSize


EVENTS: dict[PanelSize, list[tuple[str, datetime.timedelta]]] = {
    PanelSize.PANEL_64x64: [
        ("dial a fish", datetime.timedelta(minutes=5)),
        ("make a fish", datetime.timedelta(minutes=5)),
        # "make a wiish", datetime.timedelta(minutes=5),
        ("ssh a fish", datetime.timedelta(minutes=5)),
        ("spin a fish", datetime.timedelta(minutes=5)),
        # "X11:11 a fish", datetime.timedelta(minutes=5),
        ("bake a dish", datetime.timedelta(minutes=5)),
        ("make a seq.", datetime.timedelta(minutes=5)),
    ],
    PanelSize.PANEL_64x32: [
        ("make a fish", datetime.timedelta(minutes=5)),
        ("bake a dish", datetime.timedelta(minutes=5)),
        ("make a seq.", datetime.timedelta(minutes=5)),
    ],
}


class Approaching(Screen[None]):
    def fetch_data(self) -> None:
        return None

    def fallback_data(self):
        return None

    def get_image(self):
        image = self.size.value.image()
        draw = ImageDraw.Draw(image)

        time_str = datetime.datetime.now().strftime("%H:%M")
        draw.text((39, 1), f"{time_str:>5}", font=font, fill="#FFAA00")

        for i, (label, wait) in list(enumerate(EVENTS[self.size])):
            time_str = str(int(wait / datetime.timedelta(minutes=1)))
            draw.text((1, 12 + 9 * i), f"{label:<8}", font=font, fill="#FFAA00")
            draw.text((47, 12 + 9 * i), f"{time_str:>2}", font=font, fill="#FFAA00")
            draw.text((59, 12 + 9 * i), "m", font=font, fill="#FFAA00")

        return image
