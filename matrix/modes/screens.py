from typing import Any
from PIL import Image, ImageDraw
from matrix.resources.colors import BLUE, GREEN, LIGHT_GREY, WHITE
from matrix.resources.fonts import font
from matrix.modes.mode import BaseMode, ChangeMode, ModeType
from matrix.screens.screen import Screen
from matrix.utils.panels import PanelSize


class Screens(BaseMode):
    def __init__(self, change_mode: ChangeMode, size: PanelSize, screens: list[Screen]) -> None:
        super().__init__(change_mode, size)
        self.screens = screens
        self.selected_option: int = 0
        self.total_options = len(self.screens) + 1  # +1 for the "back" option

    @property
    def is_back_selected(self) -> bool:
        return self.selected_option == self.total_options - 1

    def handle_encoder_push(self):
        if self.is_back_selected:
            self.change_mode(ModeType.MENU)
        else:
            self.screens[self.selected_option].is_enabled = not self.screens[
                self.selected_option
            ].is_enabled

    def handle_encoder_clockwise(self):
        self.selected_option = (self.selected_option + 1) % self.total_options

    def handle_encoder_counterclockwise(self):
        self.selected_option = (self.selected_option - 1) % self.total_options

    def get_image(self) -> Image.Image:
        # TODO: make sure everything can fit or implement scrolling?
        image = self.create_image()
        draw = ImageDraw.Draw(image)

        draw.text((0, 1), text="   Screens   ", font=font, fill=WHITE)

        # back arrow
        arrow_middle_y = 5
        draw.line((2, arrow_middle_y, 8, arrow_middle_y), fill=LIGHT_GREY)
        draw.line((2, arrow_middle_y, 5, 8), fill=LIGHT_GREY)
        draw.line((2, arrow_middle_y, 5, 2), fill=LIGHT_GREY)

        draw.line((0, 10, 64, 10), fill=LIGHT_GREY)  # separator

        for i, screen in enumerate(self.screens):
            box_kwargs: dict[str, Any] = {"outline": LIGHT_GREY}
            if screen.is_enabled:
                box_kwargs["fill"] = GREEN
            draw.rectangle((1, 13 + 10 * i, 8, 20 + 10 * i), **box_kwargs)
            if screen.is_enabled:
                # check mark
                draw.line((3, 18 + 10 * i, 2, 17 + 10 * i), fill=WHITE)
                draw.line((3, 18 + 10 * i, 7, 14 + 10 * i), fill=WHITE)

            draw.text(
                (12, 14 + 10 * i),
                text=screen.__class__.__name__,
                font=font,
                fill=(WHITE if self.selected_option == i else LIGHT_GREY),
            )

        if self.is_back_selected:
            draw.rectangle((0, 0, 10, 10), outline=BLUE)
        else:
            draw.rectangle(
                (
                    0,
                    12 + 10 * self.selected_option,
                    63,
                    12 + 10 * self.selected_option + 9,
                ),
                outline=BLUE,
            )

        return image
