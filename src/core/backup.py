import shutil
from pathlib import Path
from datetime import datetime
from typing import Callable
from src.core.models import Game, BackupEntry
from src.core.utils import timestamp, folder_size


def do_backup(
    game: Game,
    on_progress: Callable[[str], None] | None = None
) -> BackupEntry:
    """Copy source_path to backup_path/<name>-YYYYMMDD_HHmmss."""
    ts = timestamp()
    folder_name = f"{game.name}-{ts}"
    dest = Path(game.backup_path) / folder_name
    if on_progress:
        on_progress(f"Backing up to {dest.name}...")
    shutil.copytree(game.source_path, dest)
    return BackupEntry(
        name=folder_name,
        path=str(dest),
        created_at=datetime.now(),
        size_bytes=folder_size(dest)
    )


def do_restore(
    game: Game,
    backup: BackupEntry,
    on_progress: Callable[[str], None] | None = None
) -> None:
    """Delete source, copy backup to source."""
    source = Path(game.source_path)
    backup_path = Path(backup.path)
    if on_progress:
        on_progress("Restoring...")
    if source.exists():
        shutil.rmtree(source)
    shutil.copytree(backup_path, source)


def list_backups(game: Game) -> list[BackupEntry]:
    """Return backups sorted newest first."""
    backup_dir = Path(game.backup_path)
    if not backup_dir.exists():
        return []
    backups = []
    for folder in backup_dir.iterdir():
        if folder.is_dir() and folder.name.startswith(game.name):
            created = datetime.fromtimestamp(folder.stat().st_ctime)
            backups.append(BackupEntry(
                name=folder.name,
                path=str(folder),
                created_at=created,
                size_bytes=folder_size(folder)
            ))
    return sorted(backups, key=lambda b: b.created_at, reverse=True)


def delete_backup(backup: BackupEntry) -> None:
    """Delete backup folder."""
    shutil.rmtree(backup.path)