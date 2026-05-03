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
    file_to_backup: Path,
    on_progress: Callable[[str], None] | None = None
) -> BackupEntry:
    """
    Backup a specific file from the game's source_path.
    Uses copy with error handling for locked files.
    """
    ts = timestamp()
    folder_name = f"{game.name}-{ts}"
    dest = Path(game.backup_path) / folder_name
    Path(game.backup_path).mkdir(parents=True, exist_ok=True)
    dest.mkdir(parents=True, exist_ok=True)

    if on_progress:
        on_progress(f"Backing up: {file_to_backup.name}")

    try:
        if file_to_backup.is_dir():
            # Use copytree for directories
            shutil.copytree(file_to_backup, dest / file_to_backup.name)
            size = folder_size(dest / file_to_backup.name)
        else:
            # Try copy2 first (preserves metadata)
            shutil.copy2(file_to_backup, dest / file_to_backup.name)
            size = file_to_backup.stat().st_size
    except PermissionError:
        # If PermissionError, try regular copy (less strict)
        try:
            if file_to_backup.is_dir():
                shutil.copytree(file_to_backup, dest / file_to_backup.name)
            else:
                shutil.copy(file_to_backup, dest / file_to_backup.name)
            size = folder_size(dest / file_to_backup.name) if file_to_backup.is_dir() else file_to_backup.stat().st_size
        except Exception as e:
            raise PermissionError(f"Cannot access: {file_to_backup.name}. It may be in use by another program.") from e
    except Exception as e:
        # Try with lower-level copy as last resort (for files only)
        if file_to_backup.is_file():
            try:
                with open(file_to_backup, 'rb') as src:
                    with open(dest / file_to_backup.name, 'wb') as dst:
                        dst.write(src.read())
                size = file_to_backup.stat().st_size
            except Exception as e2:
                raise PermissionError(f"Cannot copy {file_to_backup.name}: {e2}") from e2
        else:
            raise PermissionError(f"Cannot copy {file_to_backup.name}: {e}") from e

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
    """Restore from backup - handles both files and folders."""
    source = Path(game.source_path)
    backup_path = Path(backup.path)
    
    if on_progress:
        on_progress("Preparing restore...")
    
    # Handle folder restore (if backup is a folder)
    if backup_path.is_dir():
        # Find content to restore - could be a subfolder or files
        items = list(backup_path.iterdir())
        
        if items:
            # If there's a single item that's a folder, restore it
            for item in items:
                if item.is_dir():
                    # Restore entire folder to source location
                    source.mkdir(parents=True, exist_ok=True)
                    dest = source / item.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    # Restore individual files
                    source.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, source / item.name)
            
            if on_progress:
                on_progress("Restore complete!")
            return
    
    # Original logic for single file restore
    save_file = None
    if backup_path.is_file():
        save_file = backup_path
    else:
        files = list(backup_path.glob("*sav*")) + list(backup_path.glob("*save*")) + list(backup_path.glob("*.bak"))
        if files:
            save_file = files[0]
        else:
            files = [f for f in backup_path.iterdir() if f.is_file()]
            if files:
                save_file = files[0]
    
    if save_file and save_file.exists():
        if source.is_file():
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(save_file, source)
        else:
            source.mkdir(parents=True, exist_ok=True)
            dest_file = source / save_file.name
            shutil.copy2(save_file, dest_file)
        
        if on_progress:
            on_progress(f"Restored: {save_file.name}")
    else:
        if on_progress:
            on_progress("No save file found in backup")
    
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
    """Delete backup folder."""
    shutil.rmtree(backup.path)