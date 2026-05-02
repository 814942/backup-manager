import json
import uuid
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List
from src.core.models import Game

# Store config in user's app data folder on Windows
def get_config_dir() -> Path:
    """Get the app config directory."""
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:  # macOS/Linux
        base = Path.home() / ".config"
    return base / "backup-manager"


def ensure_config_dir() -> Path:
    """Ensure config directory exists."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


CONFIG_FILE = get_config_dir() / "config.json"


@dataclass
class Config:
    """Configuration container for backup-manager."""
    games: List[Game] = None

    def __post_init__(self):
        if self.games is None:
            self.games = []


def load_config() -> Config:
    """Load config.json. Returns default if not found."""
    ensure_config_dir()
    config_path = get_config_dir() / "config.json"
    if not config_path.exists():
        return Config(games=[])
    with open(config_path) as f:
        data = json.load(f)
    games = [Game(**g) for g in data.get("games", [])]
    return Config(games=games)


def save_config(config: Config) -> None:
    """Write config.json."""
    ensure_config_dir()
    config_path = get_config_dir() / "config.json"
    data = {"games": [asdict(g) for g in config.games]}
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)


def add_game(config: Config, name: str, source_path: str, backup_path: str) -> Game:
    """Add game to config. Returns new Game."""
    game = Game(
        id=str(uuid.uuid4()),
        name=name,
        source_path=source_path,
        backup_path=backup_path
    )
    config.games.append(game)
    save_config(config)
    return game


def remove_game(config: Config, game_id: str) -> None:
    """Remove game from config."""
    config.games = [g for g in config.games if g.id != game_id]
    save_config(config)