import pytest
from pathlib import Path
from datetime import datetime
from src.core.models import Game, BackupEntry
from src.core.backup import do_backup, do_restore, list_backups, delete_backup
from src.core.utils import timestamp


def make_game(tmp_path: Path) -> Game:
    source = tmp_path / "save"
    source.mkdir()
    (source / "world.bin").write_bytes(b"save data")
    backups = tmp_path / "backups"
    backups.mkdir()
    return Game(id="test", name="Test", source_path=str(source), backup_path=str(backups))


def test_do_backup_creates_folder(tmp_path):
    game = make_game(tmp_path)
    entry = do_backup(game)
    assert Path(entry.path).exists()
    assert (Path(entry.path) / "world.bin").read_bytes() == b"save data"


def test_do_restore_replaces_source(tmp_path):
    game = make_game(tmp_path)
    entry = do_backup(game)
    # Corrupt source
    (Path(game.source_path) / "world.bin").write_bytes(b"corrupted")
    do_restore(game, entry)
    assert (Path(game.source_path) / "world.bin").read_bytes() == b"save data"


def test_list_backups_sorted(tmp_path):
    game = make_game(tmp_path)
    entry = do_backup(game)
    # Create older backup manually (wait 1 sec to get different timestamp)
    import time
    time.sleep(1.1)
    old = Path(game.backup_path) / f"Test-{timestamp()}"
    old.mkdir()
    (old / "old.bin").write_bytes(b"old")
    backups = list_backups(game)
    assert len(backups) == 2
    assert backups[0].created_at >= backups[1].created_at


def test_delete_backup_removes(tmp_path):
    game = make_game(tmp_path)
    entry = do_backup(game)
    delete_backup(entry)
    assert not Path(entry.path).exists()