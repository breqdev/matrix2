from enum import Enum
from typing import NamedTuple
from PIL import Image


class Size(NamedTuple):
    rows: int
    cols: int

    def image(self) -> Image.Image:
        """Create a new RGB image with the correct size for this panel."""
        return Image.new("RGB", (self.cols, self.rows))


class PanelSize(Enum):
    PANEL_64x64 = Size(64, 64)
    PANEL_64x32 = Size(32, 64)
