import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from matrix.utils.panels import PanelSize


@dataclass
class Config:
    """Typed configuration for the matrix application."""

    # Panel configuration
    panel_size_str: str = "64x64"
    panel_brightness: int = 60
    panel_simulation: bool = True

    # Screen configurations (from TOML)
    screens: dict[str, Any] = field(default_factory=dict)

    # Command-line arguments
    simulate: bool = False

    # File paths for configuration
    config_paths: list[Path] = field(default_factory=list)

    # Computed properties
    panel_size: PanelSize = None
    is_simulated: bool = False

    def __post_init__(self):
        """Initialize the configuration with defaults."""
        # Set the config paths to try
        self.config_paths = [Path.cwd() / "matrix.toml"]
        if sys.platform == "linux":
            self.config_paths.append(Path("/etc/matrix/matrix.toml"))

        # Set computed properties based on configuration
        self._compute_properties()

    def _compute_properties(self):
        """Compute derived properties from configuration."""
        # Convert panel size string to PanelSize enum
        if self.panel_size_str == "64x64":
            self.panel_size = PanelSize.PANEL_64x64
        elif self.panel_size_str == "64x32":
            self.panel_size = PanelSize.PANEL_64x32
        else:
            raise ValueError(f"Unexpected panel size: {self.panel_size_str}")

        # Determine if simulation is active
        self.is_simulated = self.simulate or self.panel_simulation


def load_config() -> Config:
    """Load configuration from TOML file."""
    config = Config()

    # Load TOML configuration
    for path in config.config_paths:
        if path.exists():
            with path.open("rb") as file:
                toml_config = tomllib.load(file)
                # Update panel configuration
                panel_config = toml_config.get("panel", {})
                config.panel_size_str = panel_config.get("size", "64x64")
                config.panel_brightness = panel_config.get("brightness", 60)
                config.panel_simulation = panel_config.get("simulation", True)

                # Update screen configurations
                config.screens = toml_config.get("screens", {})
                break
    else:
        # If no config file found, we'll use defaults
        raise FileNotFoundError(f"Failed to locate path at any of: {config.config_paths}")

    # Compute derived properties
    config._compute_properties()

    return config


# Global singleton instance
_config_instance: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance


def set_config(config: Config) -> None:
    """Set the global configuration instance (useful for testing)."""
    global _config_instance
    # For command-line arguments, we should merge them with the loaded config
    if _config_instance is not None:
        # If we already have a config, merge the simulate flag
        config.panel_size_str = _config_instance.panel_size_str
        config.panel_brightness = _config_instance.panel_brightness
        config.panel_simulation = _config_instance.panel_simulation
        config.screens = _config_instance.screens

    # Recompute properties after merge
    config._compute_properties()

    _config_instance = config
