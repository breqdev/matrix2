from abc import ABC, abstractmethod
from PIL import Image
from typing import Callable, TypeAlias
import enum


class ModeType(enum.StrEnum):
    MAIN = enum.auto()
    MENU = enum.auto()
    OFF = enum.auto()
    BRIGHTNESS = enum.auto()
    NETWORK = enum.auto()
    CONFIG = enum.auto()


ChangeMode: TypeAlias = Callable[[ModeType], None]


class BaseMode(ABC):
    change_mode: ChangeMode

    def __init__(self, change_mode: ChangeMode) -> None:
        self.change_mode = change_mode

    @abstractmethod
    def handle_encoder_push(self) -> None:
        pass

    def handle_encoder_clockwise(self) -> None:
        pass

    def handle_encoder_counterclockwise(self) -> None:
        pass

    @abstractmethod
    def get_image(self) -> Image.Image:
        pass
