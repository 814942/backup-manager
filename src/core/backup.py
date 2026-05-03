import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Callable
from src.core.models import Game, BackupEntry
from src.core.utils import timestamp, folder_size



def list_files_for_backup(game: Game) -> list[Path]:
    """
    List all files and folders in source_path, sorted by last modified (newest first).
    """
    source = Path(game.source_path)
    if source.is_file():
        return [source]
    if source.is_dir():
        items = [f for f in source.iterdir() if f.is_file() or f.is_dir()]
        return sorted(items, key=lambda f: f.stat().st_mtime, reverse=True)
    return []

def do_backup(
    game: Game,
    file_to_backup: Path | None = None,
    on_progress: Callable[[str], None] | None = None
) -> BackupEntry:
    """
    Backup a specific file or the entire source_path if file_to_backup is None.
    Uses copy with error handling for locked files.
    """
    target = file_to_backup or Path(game.source_path)
    ts = timestamp()
    folder_name = f"{game.name}-{ts}"
    dest = Path(game.backup_path) / folder_name
    Path(game.backup_path).mkdir(parents=True, exist_ok=True)
    dest.mkdir(parents=True, exist_ok=True)

    if on_progress:
        on_progress(f"Backing up: {target.name}")

    try:
        if target.is_dir():
            # Use copytree for directories
            shutil.copytree(target, dest / target.name)
            size = folder_size(dest / target.name)
        else:
            # Try copy2 first (preserves metadata)
            shutil.copy2(target, dest / target.name)
            size = target.stat().st_size
    except PermissionError:
        # If PermissionError, try regular copy (less strict)
        try:
            if target.is_dir():
                shutil.copytree(target, dest / target.name)
            else:
                shutil.copy(target, dest / target.name)
            size = folder_size(dest / target.name) if target.is_dir() else target.stat().st_size
        except Exception as e:
            raise PermissionError(f"Cannot access: {target.name}. It may be in use by another program.") from e
    except Exception as e:
        # Try with lower-level copy as last resort (for files only)
        if target.is_file():
            try:
                with open(target, 'rb') as src:
                    with open(dest / target.name, 'wb') as dst:
                        dst.write(src.read())
                size = target.stat().st_size
            except Exception as e2:
                raise PermissionError(f"Cannot copy {target.name}: {e2}") from e2
        else:
            raise PermissionError(f"Cannot copy {target.name}: {e}") from e

    if on_progress:
        on_progress("Complete!")

    return BackupEntry(
        name=folder_name,
        path=str(dest),
        created_at=datetime.now(),
        size_bytes=size
    )


def do_restore(
    game: Game,
    backup: BackupEntry,
    on_progress: Callable[[str], None] | None = None
) -> None:
    """Restore from backup: reemplaza toda la carpeta source_path con el backup."""
    source = Path(game.source_path)
    backup_path = Path(backup.path)
    if on_progress:
        on_progress("Preparing restore...")
    if source.exists():
        shutil.rmtree(source)
    shutil.copytree(backup_path, source)
    if on_progress:
        on_progress("Restore complete!")


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
    """Delete backup folder, verifica existencia antes de borrar."""
    path = Path(backup.path)
    if not path.exists():
        raise FileNotFoundError(f'Backup not found: {backup.path}')
    shutil.rmtree(path)