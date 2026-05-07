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


def do_restore(
    game: Game,
    backup: BackupEntry,
    on_progress: Callable[[str], None] | None = None
) -> None:
    """
    Restore from backup by merging/overwriting the backup contents into the existing save directory.
    Only files and folders present in the backup are overwritten; unrelated saves are preserved.
    """
    source = Path(game.source_path)
    backup_path = Path(backup.path)

    if on_progress:
        on_progress("Preparing restore...")

    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup.path}")



    if on_progress:
        on_progress("Restoring backup (without deleting existing saves)...")

    # Copy the contents of the backup to the destination, overwriting only matching files/folders
    def copy_contents(src: Path, dst: Path) -> None:
        """
        Recursively copy contents from src to dst, overwriting files/folders and handling file/dir type mismatches.
        """
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            dest_item = dst / item.name
            if item.is_dir():
                if dest_item.exists():
                    if dest_item.is_dir():
                        # Both are directories: merge contents recursively
                        copy_contents(item, dest_item)
                    else:
                        # dest_item is a file but source is a dir: remove it first
                        dest_item.unlink()
                        shutil.copytree(item, dest_item)
                else:
                    shutil.copytree(item, dest_item)
            else:
                if dest_item.exists():
                    if dest_item.is_dir():
                        # dest_item is a directory but source is a file: remove it first
                        shutil.rmtree(dest_item)
                shutil.copy2(item, dest_item)

    items = [i for i in backup_path.iterdir()]
    try:
        # Si el backup contiene una sola carpeta (el save), copiar esa carpeta dentro del destino
        if len(items) == 1 and items[0].is_dir():
            dest = source / items[0].name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            shutil.copytree(items[0], dest)
        else:
            copy_contents(backup_path, source)
    except PermissionError as e:
        raise PermissionError(
            f"Acceso denegado al restaurar archivos.\n"
            f"Es posible que OneDrive, antivirus u otro proceso esté usando los archivos o la carpeta.\n"
            f"Cierre OneDrive, espere a que termine la sincronización, o cierre cualquier programa que use la carpeta y vuelva a intentar.\n\n"
            f"Detalle: {e}"
        ) from e

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
    import os
    import stat
    path = Path(backup.path)
    if not path.exists():
        raise FileNotFoundError(f"Backup not found: {backup.path}")

    def onerror(func, path_str, exc_info):
        # Forzar la eliminación de archivos solo lectura
        try:
            os.chmod(path_str, stat.S_IWRITE)
            func(path_str)
        except Exception as e:
            raise PermissionError(f"No se pudo eliminar '{path_str}': {e}") from e

    try:
        shutil.rmtree(path, onerror=onerror)
    except PermissionError as e:
        raise PermissionError(f"Acceso denegado al eliminar el backup: {path}\n{e}") from e
    except Exception as e:
        raise RuntimeError(f"Error inesperado al eliminar el backup: {path}\n{e}") from e