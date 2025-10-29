import enum
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeAlias

from matrix.utils.panels import Drawable, PanelSize


class ModeType(enum.StrEnum):
    MAIN = enum.auto()
    MENU = enum.auto()
    OFF = enum.auto()
    BRIGHTNESS = enum.auto()
    NETWORK = enum.auto()
    SCREENS = enum.auto()


ChangeMode: TypeAlias = Callable[[ModeType], None]


class BaseMode(ABC, Drawable):
    change_mode: ChangeMode

    def __init__(self, change_mode: ChangeMode, size: PanelSize) -> None:
        super().__init__(size)
        self.change_mode = change_mode

    @abstractmethod
    def handle_encoder_push(self) -> None:
        pass

    def handle_encoder_clockwise(self) -> None:
        pass

    def handle_encoder_counterclockwise(self) -> None:
        pass
