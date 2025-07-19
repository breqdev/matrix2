from dataclasses import dataclass
from PIL import Image, ImageDraw
from matrix.resources.fonts import font
from matrix.modes.mode import BaseMode, ChangeMode, ModeType
import sys


@dataclass
class MenuOption:
    name: str
    next_mode: ModeType


class Menu(BaseMode):
    def __init__(self, change_mode: ChangeMode) -> None:
        super().__init__(change_mode)

        self.options: list[MenuOption] = [
            MenuOption("Home", ModeType.MAIN),
            MenuOption("Screen Off", ModeType.OFF),
            MenuOption("Brightness", ModeType.BRIGHTNESS),
            MenuOption("Screens", ModeType.SCREENS),
        ]

        if sys.platform == "linux":
            self.options.append(MenuOption("Network", ModeType.NETWORK))

        self.selected_option: int = 0  # which option is selected

    def handle_encoder_push(self):
        self.change_mode(self.options[self.selected_option].next_mode)

    def handle_encoder_clockwise(self):
        self.selected_option = (self.selected_option + 1) % len(self.options)

    def handle_encoder_counterclockwise(self):
        self.selected_option = (self.selected_option - 1) % len(self.options)

    def get_image(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((0, 1), text="  Settings   ", font=font, fill="#ffffff")
        draw.line((0, 8, 64, 8), fill="#888888")

        for i, option in enumerate(self.options):
            color = "#ffffff" if self.selected_option == i else "#888888"
            draw.text((1, 12 + 10 * i), text=">", font=font, fill=color)
            draw.text((12, 12 + 10 * i), text=option.name, font=font, fill=color)

        draw.rectangle(
            (0, 10 + 10 * self.selected_option, 63, 10 + 10 * self.selected_option + 9),
            outline="#00ffff",
        )

        return image
