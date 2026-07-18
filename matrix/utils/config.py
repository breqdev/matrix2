import sys
import tomllib
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal, Self

from PIL import Image
from pydantic import BaseModel, BeforeValidator, Field, WithJsonSchema


class PanelSize(Enum):
    PANEL_64x64 = (64, 64)
    PANEL_64x32 = (64, 32)

    @classmethod
    def from_str(cls, s: str) -> "PanelSize":
        """Create a PanelSize from a string name (e.g. "64x64" -> PanelSize.PANEL_64x64)."""
        return cls["PANEL_" + s]

    def empty_image(self) -> Image.Image:
        """Create a new RGB image with the correct size for this panel."""
        return Image.new("RGB", self.value)


class PanelConfig(BaseModel):
    size: Annotated[
        PanelSize,
        BeforeValidator(lambda v: PanelSize.from_str(v)),
        WithJsonSchema({"type": "string", "enum": ["64x64", "64x32"]}),
    ] = PanelSize.PANEL_64x64
    brightness: int = 60
    simulation: bool = True


class BlueBikesStation(BaseModel):
    id: str
    label: str


class BlueBikesConfig(BaseModel):
    stations: list[BlueBikesStation] = [
        BlueBikesStation(id="S32022", label="Cedar St"),
        BlueBikesStation(id="S32013", label="Trum Field"),
        BlueBikesStation(id="S32040", label="Lowell St"),
        # BlueBikesStation(id="S32007", label="Ball Sq"),
    ]


class MbtaLine(BaseModel):
    symbol: str
    headsign: str
    label: str
    color: str
    stop_id: str
    route_id: str
    direction_id: int


class MbtaConfig(BaseModel):
    api_key: str | None = None
    lines: list[MbtaLine] = Field(default_factory=list)


class SpotifyConfig(BaseModel):
    users: list[str] = Field(default_factory=list)


class Position(BaseModel):
    latitude: float
    longitude: float


class OctoprintConfig(BaseModel):
    api_key: str
    endpoint: str
    printer_name: str


class FishConfig(BaseModel):
    provider: Literal["makeafish", "amy"] = "makeafish"


class ScreensConfig(BaseModel):
    fish: FishConfig = Field(default_factory=FishConfig)
    bluebikes: BlueBikesConfig = Field(default_factory=BlueBikesConfig)
    mbta: MbtaConfig = Field(default_factory=MbtaConfig)
    spotify: SpotifyConfig = Field(default_factory=SpotifyConfig)
    weather: Position
    forecast: Position
    octoprint: OctoprintConfig
    matter: bool = False


class Config(BaseModel):
    """Typed configuration for the matrix application."""

    panel: PanelConfig
    screens: ScreensConfig

    _simulate: bool = False

    @property
    def is_simulated(self) -> bool:
        return self._simulate or self.panel.simulation

    @classmethod
    def load(cls, path: Path) -> Self:
        """Load configuration from TOML file."""
        with path.open("rb") as file:
            toml_config = tomllib.load(file)
        return cls.model_validate(toml_config)


def load_config() -> Config:
    """Load configuration from TOML file."""
    # Set the config paths to try
    config_paths = [Path.cwd() / "matrix.toml"]
    if sys.platform == "linux":
        config_paths.append(Path("/etc/matrix/matrix.toml"))

    # Load TOML configuration
    for path in config_paths:
        if path.exists():
            return Config.load(path)
    else:
        raise FileNotFoundError(f"Failed to locate path at any of: {config_paths}")


_config_instance: Config | None = None


def get_config(simulate_arg: bool | None = None) -> Config:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    if simulate_arg is not None:
        _config_instance._simulate = simulate_arg
    return _config_instance


def get_panel_size() -> PanelSize:
    """Get the panel size from the global configuration."""
    return get_config().panel.size
