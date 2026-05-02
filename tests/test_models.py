"""Tests for data models."""
from datetime import datetime
from src.core.models import Game, BackupEntry


def test_game_dataclass():
    """Game dataclass stores all fields correctly."""
    game = Game(
        id="test-uuid-1234",
        name="Test Game",
        source_path="C:/Games/TestGame/saves",
        backup_path="C:/Backups/TestGame"
    )
    assert game.id == "test-uuid-1234"
    assert game.name == "Test Game"
    assert game.source_path == "C:/Games/TestGame/saves"
    assert game.backup_path == "C:/Backups/TestGame"


def test_backup_entry_dataclass():
    """BackupEntry dataclass stores all fields correctly."""
    now = datetime.now()
    entry = BackupEntry(
        name="TestGame-20250502_143000",
        path="C:/Backups/TestGame/TestGame-20250502_143000",
        created_at=now,
        size_bytes=1024000
    )
    assert entry.name == "TestGame-20250502_143000"
    assert entry.created_at == now
    assert entry.size_bytes == 1024000