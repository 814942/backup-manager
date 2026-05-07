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
    # Ahora el backup debe contener la subcarpeta "save" con el archivo dentro
    save_folder = Path(entry.path) / "save"
    assert save_folder.exists() and save_folder.is_dir()
    assert (save_folder / "world.bin").read_bytes() == b"save data"


def test_do_restore_replaces_source(tmp_path):
    game = make_game(tmp_path)
    entry = do_backup(game)
    # Corrupt source
    (Path(game.source_path) / "world.bin").write_bytes(b"corrupted")
    do_restore(game, entry)
    # El restore ahora debe restaurar la subcarpeta "save" dentro de source
    restored = Path(game.source_path) / "save"
    assert (restored / "world.bin").read_bytes() == b"save data"


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


def test_restore_save_folder_as_subfolder(tmp_path):
    """
    Verifica que al restaurar un backup que contiene una carpeta de save, se restaure como subcarpeta y no solo su contenido.
    """
    # Simula estructura: backup/PZ-20260504_184430/ARK_v1.4.0_2026-04-28_11-10-15/*
    source = tmp_path / "game_saves"
    source.mkdir()
    (source / "dummy.txt").write_text("original")
    backup_root = tmp_path / "backups"
    backup_root.mkdir()
    save_folder = backup_root / "PZ-20260504_184430"
    save_folder.mkdir()
    save_subfolder = save_folder / "ARK_v1.4.0_2026-04-28_11-10-15"
    save_subfolder.mkdir()
    (save_subfolder / "world1.bin").write_text("save1")
    (save_subfolder / "world2.bin").write_text("save2")
    # Game y BackupEntry
    game = Game(id="pz", name="PZ", source_path=str(source), backup_path=str(backup_root))
    entry = BackupEntry(path=str(save_folder), created_at=None, size=None)
    # Restaurar
    do_restore(game, entry)
    # Debe existir la subcarpeta ARK_v1.4.0_2026-04-28_11-10-15 dentro de game_saves
    restored = source / "ARK_v1.4.0_2026-04-28_11-10-15"
    assert restored.exists() and restored.is_dir()
    assert (restored / "world1.bin").read_text() == "save1"
    assert (restored / "world2.bin").read_text() == "save2"
    # El archivo original debe seguir existiendo
    assert (source / "dummy.txt").read_text() == "original"


def test_delete_backup_removes(tmp_path):
    def test_restore_save_folder_as_subfolder(tmp_path):
        """
        Verifica que al restaurar un backup que contiene una carpeta de save, se restaure como subcarpeta y no solo su contenido.
        """
        from src.core.models import Game, BackupEntry
        from src.core.backup import do_restore
        # Simula estructura: backup/PZ-20260504_184430/ARK_v1.4.0_2026-04-28_11-10-15/*
        source = tmp_path / "game_saves"
        source.mkdir()
        (source / "dummy.txt").write_text("original")
        backup_root = tmp_path / "backups"
        backup_root.mkdir()
        save_folder = backup_root / "PZ-20260504_184430"
        save_folder.mkdir()
        save_subfolder = save_folder / "ARK_v1.4.0_2026-04-28_11-10-15"
        save_subfolder.mkdir()
        (save_subfolder / "world1.bin").write_text("save1")
        (save_subfolder / "world2.bin").write_text("save2")
        # Game y BackupEntry
        game = Game(id="pz", name="PZ", source_path=str(source), backup_path=str(backup_root))
        entry = BackupEntry(
            name=save_folder.name,
            path=str(save_folder),
            created_at=datetime.now(),
            size_bytes=(save_subfolder / "world1.bin").stat().st_size + (save_subfolder / "world2.bin").stat().st_size,
        )
        # Restaurar
        do_restore(game, entry)
        # Debe existir la subcarpeta ARK_v1.4.0_2026-04-28_11-10-15 dentro de game_saves
        restored = source / "ARK_v1.4.0_2026-04-28_11-10-15"
        assert restored.exists() and restored.is_dir()
        assert (restored / "world1.bin").read_text() == "save1"
        assert (restored / "world2.bin").read_text() == "save2"
        # El archivo original debe seguir existiendo
        assert (source / "dummy.txt").read_text() == "original"
    game = make_game(tmp_path)
    entry = do_backup(game)
    delete_backup(entry)
    assert not Path(entry.path).exists()