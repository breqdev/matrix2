from enum import Enum
from typing import NamedTuple


class Size(NamedTuple):
    rows: int
    cols: int


class PanelSize(Enum):
    PANEL_64x64 = Size(64, 64)
    PANEL_64x32 = Size(32, 64)
