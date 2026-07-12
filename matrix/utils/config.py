import sys
import tomllib
from pathlib import Path
from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, Field

from matrix.utils.panels import PanelSize


class PanelConfig(BaseModel):
    size: Annotated[PanelSize, BeforeValidator(lambda v: PanelSize.from_str(v))] = PanelSize.PANEL_64x64
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


class WeatherConfig(BaseModel):
    latitude: float
    longitude: float


class ForecastConfig(BaseModel):
    latitude: float
    longitude: float


class OctoprintConfig(BaseModel):
    api_key: str
    endpoint: str
    printer_name: str


class ScreensConfig(BaseModel):
    bluebikes: BlueBikesConfig = Field(default_factory=BlueBikesConfig)
    mbta: MbtaConfig = Field(default_factory=MbtaConfig)
    spotify: SpotifyConfig = Field(default_factory=SpotifyConfig)
    weather: WeatherConfig
    forecast: ForecastConfig
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
