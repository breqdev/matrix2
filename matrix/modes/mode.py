from abc import ABC, abstractmethod
from PIL import Image
from typing import Callable
import enum


class ModeName(enum.Enum):
    MAIN = "main"
    MENU = "menu"
    OFF = "off"
    BRIGHTNESS = "brightness"
    NETWORK = "network"


class BaseMode(ABC):
    change_mode: Callable[[ModeName], None]

    def __init__(
        self,
        change_mode: Callable[[ModeName], None],
    ) -> None:
        self.change_mode = change_mode

    @abstractmethod
    def handle_encoder_push(self) -> None:
        pass

    @abstractmethod
    def handle_encoder_clockwise(self) -> None:
        pass

    @abstractmethod
    def handle_encoder_counterclockwise(self) -> None:
        pass

    @abstractmethod
    def get_image(self) -> Image.Image:
        pass
