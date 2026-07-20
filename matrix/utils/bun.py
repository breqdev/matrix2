import shutil
from pathlib import Path


def find_bun() -> Path:
    # If Bun is on PATH, always use that
    if bun_on_path := shutil.which("bun"):
        return Path(bun_on_path)

    # If this user has an installation of Bun, use it
    if (Path.home() / ".bun").exists():
        return Path.home() / ".bun" / "bin" / "bun"

    # If the owner of the current working directory has an
    # installation of Bun, use it
    # (Useful when bun is installed as "pi" but script is "root")
    owner_path = Path(f"~{Path.cwd().owner()}").expanduser()
    if (owner_path / ".bun").exists():
        return owner_path / ".bun" / "bin" / "bun"

    raise RuntimeError("Failed to find Bun executable")
