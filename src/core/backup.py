import shutil
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


# FIX ISS-01: file_to_backup is now optional (default None).
# When None, the entire source_path folder is backed up (original PowerShell behavior).
def do_backup(
    game: Game,
    file_to_backup: Path | None = None,
    on_progress: Callable[[str], None] | None = None
) -> BackupEntry:
    """
    Backup a specific file/folder from the game's source_path.
    If file_to_backup is None, backs up the entire source_path folder.
    Uses copy with error handling for locked files.
    """
    ts = timestamp()
    folder_name = f"{game.name}-{ts}"
    dest = Path(game.backup_path) / folder_name
    Path(game.backup_path).mkdir(parents=True, exist_ok=True)
    dest.mkdir(parents=True, exist_ok=True)

    # If no specific file given, back up the whole source folder
    target = file_to_backup if file_to_backup is not None else Path(game.source_path)

    if on_progress:
        on_progress(f"Backing up: {target.name}")

    try:
        if target.is_dir():
            shutil.copytree(target, dest / target.name)
            size = folder_size(dest / target.name)
        else:
            shutil.copy2(target, dest / target.name)
            size = target.stat().st_size
    except PermissionError:
        try:
            if target.is_dir():
                shutil.copytree(target, dest / target.name)
            else:
                shutil.copy(target, dest / target.name)
            size = folder_size(dest / target.name) if target.is_dir() else target.stat().st_size
        except Exception as e:
            raise PermissionError(f"Cannot access: {target.name}. It may be in use by another program.") from e
    except Exception as e:
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


# FIX ISS-02: Removed fragile glob("*sav*") fallback.
# do_backup always copies the entire source folder, so do_restore
# simply replaces it entirely — no file-matching needed.
def do_restore(
    game: Game,
    backup: BackupEntry,
    on_progress: Callable[[str], None] | None = None
) -> None:
    """
    Restore from backup by replacing the entire source_path folder.
    Deletes the current save and copies the backup in its place.
    """
    source = Path(game.source_path)
    backup_path = Path(backup.path)

    if on_progress:
        on_progress("Preparing restore...")

    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup.path}")

    # Remove current save
    if source.exists():
        if source.is_dir():
            shutil.rmtree(source)
        else:
            source.unlink()

    if on_progress:
        on_progress("Copying files...")

    # The backup folder contains a single subfolder with the original save name.
    # Copy that subfolder back to the source location.
    items = [i for i in backup_path.iterdir()]
    if len(items) == 1 and items[0].is_dir():
        shutil.copytree(items[0], source)
    else:
        # Fallback: copy the entire backup folder to source
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


# FIX ISS-03: Check path exists before deleting to avoid FileNotFoundError on double-click.
def delete_backup(backup: BackupEntry) -> None:
    """Delete backup folder from disk."""
    path = Path(backup.path)
    if not path.exists():
        raise FileNotFoundError(f"Backup not found: {backup.path}")
    shutil.rmtree(path)