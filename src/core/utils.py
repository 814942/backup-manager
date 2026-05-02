from pathlib import Path
from datetime import datetime


def human_size(size_bytes: int) -> str:
    """Convert bytes to human-readable string."""
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            if unit == 'B':
                return f"{int(size_bytes)} B"
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def folder_size(path: Path) -> int:
    """Calculate total size of folder in bytes."""
    total = 0
    for file in path.rglob('*'):
        if file.is_file():
            total += file.stat().st_size
    return total


def timestamp(dt: datetime | None = None) -> str:
    """Generate folder-safe timestamp. Format: YYYYMMDD_HHmmss"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y%m%d_%H%M%S")