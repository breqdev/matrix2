from abc import ABC, abstractmethod
from PIL import Image
from typing import Callable, TypeAlias
import enum

from matrix.utils.panels import PanelSize


class ModeType(enum.StrEnum):
    MAIN = enum.auto()
    MENU = enum.auto()
    OFF = enum.auto()
    BRIGHTNESS = enum.auto()
    NETWORK = enum.auto()
    SCREENS = enum.auto()


ChangeMode: TypeAlias = Callable[[ModeType], None]


class BaseMode(ABC):
    change_mode: ChangeMode
    size: PanelSize

    def __init__(self, change_mode: ChangeMode, size: PanelSize) -> None:
        self.change_mode = change_mode
        self.size = size

    def create_image(self) -> Image.Image:
        """Create a new RGB image with the correct size for this panel."""
        size = self.size.value
        return Image.new("RGB", (size.cols, size.rows))

    @abstractmethod
    def handle_encoder_push(self) -> None:
        pass

    def handle_encoder_clockwise(self) -> None:
        pass

    def handle_encoder_counterclockwise(self) -> None:
        pass

    def get_image(self) -> Image.Image:
        """Get the current image for this mode. Delegates to size-specific methods by default.

        Modes can either:
        1. Override this method directly for size-agnostic rendering, or
        2. Override get_image_64x64() and get_image_64x32() for size-specific rendering
        """
        match self.size:
            case PanelSize.PANEL_64x64:
                return self.get_image_64x64()
            case PanelSize.PANEL_64x32:
                return self.get_image_64x32()

    def get_image_64x64(self) -> Image.Image:
        """Get image for 64x64 panel. Override in subclasses for size-specific rendering."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_image_64x64() or override get_image()"
        )

    def get_image_64x32(self) -> Image.Image:
        """Get image for 64x32 panel. Override in subclasses for size-specific rendering."""
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_image_64x32() or override get_image()"
        )
