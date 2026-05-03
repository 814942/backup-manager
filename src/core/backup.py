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
    """Copy source_path to backup_path/<game-name>-YYYYMMDD_HHmmss."""
    ts = timestamp()
    folder_name = f"{game.name}-{ts}"
    dest = Path(game.backup_path) / folder_name
    
    # Ensure backup dir exists
    Path(game.backup_path).mkdir(parents=True, exist_ok=True)
    
    if on_progress:
        on_progress(f"Preparing backup of {game.name}...")
        
        # Count files for progress
        total_files = sum(1 for _ in Path(game.source_path).rglob('*') if _.is_file())
        
        copied = 0
        for file in Path(game.source_path).rglob('*'):
            if file.is_file():
                rel_path = file.relative_to(Path(game.source_path))
                dest_file = dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest_file)
                copied += 1
                # Update progress every 50 files or at end
                if copied % 50 == 0 or copied == total_files:
                    pct = int(copied * 100 / total_files)
                    on_progress(f"Copying files... {pct}% ({copied}/{total_files})")
        
        on_progress("Complete!")
    else:
        shutil.copytree(Path(game.source_path), dest)
    
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
        on_progress("Preparing restore...")
        
        # Count files in backup
        total_files = sum(1 for _ in backup_path.rglob('*') if _.is_file())
        
        if source.exists():
            on_progress("Removing old files...")
            shutil.rmtree(source)
        
        copied = 0
        for file in backup_path.rglob('*'):
            if file.is_file():
                rel_path = file.relative_to(backup_path)
                dest_file = source / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest_file)
                copied += 1
                if copied % 50 == 0 or copied == total_files:
                    pct = int(copied * 100 / total_files)
                    on_progress(f"Restoring files... {pct}% ({copied}/{total_files})")
        
        on_progress("Restore complete!")
    else:
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