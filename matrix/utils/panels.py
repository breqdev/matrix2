from enum import Enum
from typing import NamedTuple

from PIL import Image


class Size(NamedTuple):
    cols: int
    rows: int

    def image(self) -> Image.Image:
        """Create a new RGB image with the correct size for this panel."""
        return Image.new("RGB", (self.cols, self.rows))


class PanelSize(Enum):
    PANEL_64x64 = Size(64, 64)
    PANEL_64x32 = Size(64, 32)

    @classmethod
    def from_str(cls, s: str) -> "PanelSize":
        """Create a PanelSize from a string name (e.g. "64x64" -> PanelSize.PANEL_64x64)."""
        return cls["PANEL_" + s]


class Drawable:
    size: PanelSize

    def __init__(self, size: PanelSize) -> None:
        self.size = size

    def get_image(self) -> Image.Image | None:
        """Get the current image for this screen. Delegates to size-specific methods by default.

        Screens can either:
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
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_image_64x64() or override get_image()")

    def get_image_64x32(self) -> Image.Image:
        """Get image for 64x32 panel. Override in subclasses for size-specific rendering."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_image_64x32() or override get_image()")
