from dataclasses import dataclass
from datetime import datetime


@dataclass
class Game:
    """Represents a game with save data to backup/restore."""
    id: str                # uuid4
    name: str
    source_path: str       # Absolute path to active save folder
    backup_path: str       # Absolute path to backup destination folder


@dataclass
class BackupEntry:
    """Represents a single backup of a game's save data."""
    name: str              # Folder name (includes timestamp suffix)
    path: str              # Absolute path
    created_at: datetime
    size_bytes: int