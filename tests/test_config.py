import pytest
import json
from src.core.config import load_config, save_config, add_game, remove_game, Config
from pathlib import Path


def test_load_config_default(tmp_path, monkeypatch):
    # No config file exists
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert config.games == []


def test_save_and_load_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = Config(games=[])
    save_config(config)
    loaded = load_config()
    assert loaded.games == []


def test_add_game(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = load_config()
    game = add_game(config, "Project Zomboid", "C:/Games/Zomboid", "C:/Backups/Zomboid")
    assert game.name == "Project Zomboid"
    assert game.source_path == "C:/Games/Zomboid"
    assert len(config.games) == 1


def test_remove_game(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = load_config()
    game = add_game(config, "Game", "C:/Game", "C:/Backups")
    remove_game(config, game.id)
    assert len(config.games) == 0