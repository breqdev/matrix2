# stdlib
from dataclasses import dataclass

# 3p
from gpiozero import RotaryEncoder, Button
from PIL import Image, ImageDraw

# project
from matrix.fonts import font


OPTIONS = [
    "Brightness",
    "Scenes",
    "Network",
    "Power Off",
    "Home",
]

SELECTED_OPTION = 0


def handle_rotation_clockwise():
    global SELECTED_OPTION
    SELECTED_OPTION = (SELECTED_OPTION + 1) % len(OPTIONS)


def handle_rotation_counter_clockwise():
    global SELECTED_OPTION
    SELECTED_OPTION = (SELECTED_OPTION - 1 + len(OPTIONS)) % len(OPTIONS)


def draw_menu(encoder: RotaryEncoder) -> Image.Image:
    global SELECTED_OPTION

    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    encoder.when_rotated_clockwise = handle_rotation_clockwise
    encoder.when_rotated_counter_clockwise = handle_rotation_counter_clockwise

    draw.text((0, 1), text="  Settings   ", font=font, fill="#00ffff")

    for i, name in enumerate(OPTIONS):
        if SELECTED_OPTION == i:
            color = "#ffffff"
        else:
            color = "#888888"
        draw.text((1, 12 + 10 * i), text=">", font=font, fill=color)
        draw.text((12, 12 + 10 * i), text=name, font=font, fill=color)

    draw.rectangle((0, 10 + 10 * SELECTED_OPTION, 63, 10 + 10 * SELECTED_OPTION + 9))

    return image
