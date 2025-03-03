# stdlib
from collections.abc import Callable
from dataclasses import field
from functools import lru_cache

# 3p
from gpiozero import RotaryEncoder, Button
from PIL import Image, ImageDraw

# project
from matrix.fonts import font, bigfont
from matrix.network import get_network_info
from matrix.config import Config

BLANK_IMAGE = Image.new("RGB", (64, 64))


@lru_cache()
def unimplemented():
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    draw.text((0, 1), text="Unimplemented", font=font, fill="#00ffff")

    return image


class Menu:
    dial: RotaryEncoder
    button: Button
    config: Config

    options: list[str] = field(init=False)
    option_displays: list[Callable[[], Image.Image]] = field(init=False)
    selected_option: int = 0  # which option is selected
    is_option_selected: bool = False  # true if we are in a sub-menu

    def __init__(self, dial: RotaryEncoder, button: Button, config: Config):
        self.dial = dial
        self.button = button
        self.config = config

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
            self.selected_option = (self.selected_option - 1 + len(self.options)) % len(
                self.options
            )

    def draw(self) -> Image.Image:
        if self.is_option_selected:
            return self.option_displays[self.selected_option]()
        return self.draw_main_menu()

    def draw_main_menu(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((0, 1), text="  Settings   ", font=font, fill="#ffffff")
        draw.line((0, 8, 64, 8), fill="#888888")

        for i, name in enumerate(self.options):
            color = "#ffffff" if self.selected_option == i else "#888888"
            draw.text((1, 12 + 10 * i), text=">", font=font, fill=color)
            draw.text((12, 12 + 10 * i), text=name, font=font, fill=color)

        draw.rectangle(
            (0, 10 + 10 * self.selected_option, 63, 10 + 10 * self.selected_option + 9),
            outline="#00ffff",
        )

        return image

    def draw_brightness(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((2, 1), text=" Brightness ", font=font, fill="#888888")
        draw.line((0, 8, 64, 8), fill="#888888")

        draw.text((8, 16), text="100%", font=bigfont, fill="#ffffff")

        return image

    def draw_network(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        draw.text((2, 1), text="Network Info", font=font, fill="#ffffff")
        draw.line((0, 8, 64, 8), fill="#888888")

        network_info = get_network_info()

        draw.text((1, 12), text="SSID", font=font, fill="#888888")
        draw.text((1, 20), text=network_info.ssid, font=font, fill="#ffffff")

        draw.text((1, 30), text="IP Address", font=font, fill="#888888")
        draw.text((1, 38), text=network_info.ip_addr, font=font, fill="#ffffff")

        # draw.text((1, 48), text="IP Address", font=font, fill="#888888")
        # draw.text((1, 56), text=network_info.ip_addr, font=font, fill="#ffffff")

        return image

    def draw_scenes(self) -> Image.Image:
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
