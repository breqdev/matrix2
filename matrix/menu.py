# stdlib
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import lru_cache

# 3p
from gpiozero import RotaryEncoder, Button
from PIL import Image, ImageDraw

# project
from matrix.fonts import font

BLANK_IMAGE = Image.new("RGB", (64, 64))


@lru_cache()
def unimplemented():
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    draw.text((0, 1), text="Unimplemented", font=font, fill="#00ffff")

    return image


@dataclass
class Menu:
    dial: RotaryEncoder
    button: Button

    options: list[str] = field(init=False)
    option_displays: list[Callable[[], Image.Image]] = field(init=False)
    selected_option: int = 0  # which option is selected
    is_option_selected: bool = False  # true if we are in a sub-menu

    def __post_init__(self):
        self.options = [
            "Home",
            "Screen Off",
            "Brightness",
            "Scenes",
            "Network",
        ]
        self.option_displays = [
            unimplemented,  # placeholder, Home has custom logic
            self.draw_display_off,
            self.draw_brightness,
            self.draw_scenes,
            self.draw_network,
        ]

    def handle_rotation_clockwise(self):
        if not self.is_option_selected:
            self.selected_option = (self.selected_option + 1) % len(self.options)

    def handle_rotation_counter_clockwise(self):
        if not self.is_option_selected:
            self.selected_option = (self.selected_option - 1 + len(self.options)) % len(self.options)

    def draw(self) -> Image.Image:
        if self.is_option_selected:
            return self.option_displays[self.selected_option]()
        return self.draw_main_menu()

    def draw_main_menu(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((0, 1), text="  Settings   ", font=font, fill="#00ffff")

        for i, name in enumerate(self.options):
            color = "#ffffff" if self.selected_option == i else "#888888"
            draw.text((1, 12 + 10 * i), text=">", font=font, fill=color)
            draw.text((12, 12 + 10 * i), text=name, font=font, fill=color)

        draw.rectangle((0, 10 + 10 * self.selected_option, 63, 10 + 10 * self.selected_option + 9))

        return image

    def draw_brightness(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((0, 1), text="Brightness", font=font, fill="#00ffff")

        return image

    def draw_scenes(self) -> Image.Image:
        return unimplemented()

    def draw_network(self) -> Image.Image:
        return unimplemented()

    def draw_display_off(self) -> Image.Image:
        return BLANK_IMAGE

    def wait_for_button(self) -> bool:
        """Poll for a button press, returning True we should exit the menu."""
        self.button.wait_for_active(timeout=0.05)
        if not self.button.is_active:
            return False
        self.button.wait_for_inactive()

        # Home button
        if self.selected_option == 0:
            return True

        self.is_option_selected = not self.is_option_selected

        # waking up from screen off
        if self.selected_option == 1 and not self.is_option_selected:
            return True
        return False
