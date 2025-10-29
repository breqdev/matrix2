import sys
import tomllib
from pathlib import Path


def parse_config():
    config_paths = [Path.cwd() / "matrix.toml"]

    if sys.platform == "linux":
        config_paths.append(Path("/etc/matrix/matrix.toml"))

    for path in config_paths:
        if path.exists():
            with path.open("rb") as file:
                return tomllib.load(file)
    else:
        raise FileNotFoundError(f"Failed to locate path at any of: {config_paths}")
