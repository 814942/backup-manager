from pathlib import Path
from src.core.models import Game
from src.core.backup import do_backup, do_restore

def make_game_with_multiple_saves(tmp_path: Path) -> Game:
    source = tmp_path / "save"
    source.mkdir()
    (source / "main_save.bin").write_bytes(b"main save data")
    (source / "other_save.bin").write_bytes(b"other save data")
    backups = tmp_path / "backups"
    backups.mkdir()
    return Game(id="test", name="Test", source_path=str(source), backup_path=str(backups))

def test_restore_does_not_delete_other_saves(tmp_path: Path) -> None:
    game = make_game_with_multiple_saves(tmp_path)
    # Backup only main_save.bin
    entry = do_backup(game, file_to_backup=Path(game.source_path) / "main_save.bin")
    # Corrupt main_save, and add a third file
    (Path(game.source_path) / "main_save.bin").write_bytes(b"corrupted")
    (Path(game.source_path) / "third_save.bin").write_bytes(b"third save data")
    do_restore(game, entry)
    # main_save.bin restored, other_save.bin and third_save.bin untouched
    assert (Path(game.source_path) / "main_save.bin").read_bytes() == b"main save data"
    assert (Path(game.source_path) / "other_save.bin").read_bytes() == b"other save data"
    assert (Path(game.source_path) / "third_save.bin").read_bytes() == b"third save data"
