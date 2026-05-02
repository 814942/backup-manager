import pytest
from src.core.utils import human_size, folder_size, timestamp
from datetime import datetime


def test_human_size_bytes():
    assert human_size(0) == "0 B"
    assert human_size(512) == "512 B"
    assert human_size(1024) == "1.0 KB"
    assert human_size(1536) == "1.5 KB"
    assert human_size(1048576) == "1.0 MB"
    assert human_size(1073741824) == "1.0 GB"


def test_timestamp():
    dt = datetime(2026, 5, 2, 14, 30, 22)
    assert timestamp(dt) == "20260502_143022"


def test_folder_size(tmp_path):
    # Create test folder with files
    (tmp_path / "file1.txt").write_bytes(b"hello")
    (tmp_path / "file2.txt").write_bytes(b"world")
    size = folder_size(tmp_path)
    assert size == 10  # 5 + 5 bytes