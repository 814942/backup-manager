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
    """Backup ONE single file (not entire folder) - the actual save file.
    
    This is much faster as it only backups the critical save file,
    not temp files, cache, logs, etc.
    """
    ts = timestamp()
    folder_name = f"{game.name}-{ts}"
    dest = Path(game.backup_path) / folder_name
    
    # Ensure backup dir exists
    Path(game.backup_path).mkdir(parents=True, exist_ok=True)
    
    source = Path(game.source_path)
    
    if on_progress:
        on_progress("Preparing backup...")
    
    # Check if source is a file or directory
    if source.is_file():
        # Single file backup - just copy it
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest / source.name)
        size = source.stat().st_size
    else:
        # Directory - find the actual save file (not all files!)
        # Look for common save file patterns
        save_file = None
        for pattern in ["*.sav", "*.save", "*.bak", "*.dat"]:
            matches = list(source.glob(pattern))
            if matches:
                save_file = matches[0]
                break
        
        # If no pattern match, try first file in directory
        if not save_file and source.exists():
            files = [f for f in source.iterdir() if f.is_file()]
            if files:
                # Pick the largest file (likely the save)
                save_file = max(files, key=lambda f: f.stat().st_size)
        
        if save_file:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(save_file, dest / save_file.name)
            size = save_file.stat().st_size
            if on_progress:
                on_progress(f"Backed up: {save_file.name}")
        else:
            # No save file found - create empty backup
            dest.mkdir(parents=True, exist_ok=True)
            size = 0
            if on_progress:
                on_progress("No save file found - created empty backup")
    
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
    """Restore ONE single file from backup (not entire folder)."""
    source = Path(game.source_path)
    backup_path = Path(backup.path)
    
    if on_progress:
        on_progress("Preparing restore...")
    
    # Find the save file in backup
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
        # Restore single file
        source.parent.mkdir(parents=True, exist_ok=True)
        
        # If source is a file, restore to same location
        if source.is_file():
            shutil.copy2(save_file, source)
        else:
            # It's a directory, restore to directory with same name
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