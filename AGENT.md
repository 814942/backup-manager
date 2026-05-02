**Game Save Backup Manager**

AGENT.MD — Tech Stack, Conventions & Standards

# **1\. Tech Stack**

| Layer | Choice | Reason |
| :---- | :---- | :---- |
| Language | Python 3.11+ | Cross-skill, easy packaging with PyInstaller, stdlib covers most needs |
| UI Framework | CustomTkinter | Modern look on top of Tkinter, no external DLLs, ships inside .exe |
| Packaging | PyInstaller | Produces a single .exe, no Python install required on target machine |
| Config storage | JSON (stdlib) | No database, human-readable, portable |
| File ops | shutil \+ pathlib (stdlib) | No extra dependencies |
| Unique IDs | uuid (stdlib) | Game entries need stable IDs |
| Tests | pytest | Standard, simple, widely supported |

# **2\. Project Structure**

| game-backup-manager/   src/     app.py              \# Entry point — launches the CTk window     ui/       main\_window.py    \# Root window, layout, navigation       game\_panel.py     \# Left panel: game list \+ add/remove       backup\_panel.py   \# Right panel: backup list \+ action buttons       settings\_window.py\# Settings screen (Toplevel window)       dialogs.py        \# Reusable confirm / progress dialogs     core/       backup.py         \# do\_backup(), do\_restore(), list\_backups(), delete\_backup()       config.py         \# load\_config(), save\_config(), add\_game(), remove\_game()       utils.py          \# human\_size(), folder\_size(), timestamp()     models.py           \# Dataclasses: Game, BackupEntry   tests/     test\_backup.py     test\_config.py     test\_utils.py   build.py              \# PyInstaller build script   requirements.txt   requirements-dev.txt   README.md   AGENT.md |
| :---- |

# **3\. Architecture Decisions**

## **Separation of concerns**

The core/ package contains zero UI code. All file system operations, config reads/writes, and business logic live there. The ui/ package consumes core/ but never the reverse. This makes core/ fully testable without a display.

## **Threading**

Backup and restore operations run in a background thread (threading.Thread). The UI must never block. Progress is communicated to the UI via a callback or a thread-safe queue. The action buttons are disabled during any running operation.

## **Config file location**

config.json is stored next to the executable (sys.executable for packaged builds, \_\_file\_\_ for dev). This keeps the tool fully portable — copy the folder to another machine and it works.

## **No global state**

The App class holds all state. No module-level globals. core/ functions are stateless and receive config/paths as arguments.

# **4\. Coding Conventions**

## **Python style**

* PEP 8\. Line length: 100 characters.

* Type hints on all function signatures.

* Dataclasses (from dataclasses import dataclass) for Game and BackupEntry models.

* f-strings for string formatting. No % formatting, no .format().

* Pathlib (Path) for all file paths. No os.path.join() in new code.

## **Naming**

* Files and modules: snake\_case

* Classes: PascalCase

* Functions and variables: snake\_case

* Constants: UPPER\_SNAKE\_CASE

* UI widget variables: descriptive names, e.g. btn\_backup, lbl\_status, frame\_left

## **No bare except**

Always catch specific exceptions. Log or surface the error — never silently swallow it.

| \# BAD try:     shutil.copytree(src, dst) except:     pass \# GOOD try:     shutil.copytree(src, dst) except PermissionError as e:     show\_error(f"No permission to write to {dst}: {e}") except OSError as e:     show\_error(f"Copy failed: {e}") |
| :---- |

# **5\. Data Models**

| from dataclasses import dataclass, field from datetime import datetime @dataclass class Game:     id: str                \# uuid4     name: str     source\_path: str       \# Absolute path to active save folder     backup\_path: str       \# Absolute path to backup destination folder @dataclass class BackupEntry:     name: str              \# Folder name (includes timestamp suffix)     path: str              \# Absolute path     created\_at: datetime     size\_bytes: int |
| :---- |

# **6\. Core API Contract**

All functions in core/backup.py follow this contract:

| def do\_backup(game: Game, on\_progress: Callable\[\[str\], None\] | None \= None) \-\> BackupEntry:     """Copy source\_path to backup\_path/\<name\>-YYYYMMDD\_HHmmss.     Calls on\_progress(message) periodically if provided.     Returns the BackupEntry for the created backup.     Raises OSError on failure.""" def do\_restore(game: Game, backup: BackupEntry,                on\_progress: Callable\[\[str\], None\] | None \= None) \-\> None:     """Delete source\_path, then copy backup.path \-\> source\_path.     Raises OSError on failure.""" def list\_backups(game: Game) \-\> list\[BackupEntry\]:     """Return all backups for this game, sorted newest first.     Returns \[\] if backup\_path does not exist.""" def delete\_backup(backup: BackupEntry) \-\> None:     """Delete backup.path from disk.     Raises OSError if deletion fails.""" |
| :---- |

# **7\. Testing**

## **Framework**

pytest. Run with: pytest tests/ \-v

## **What to test**

* core/backup.py: all four functions using tmp\_path fixture (real filesystem, temp dir)

* core/config.py: load, save, add\_game, remove\_game with temp files

* core/utils.py: human\_size(), folder\_size(), timestamp format

## **What NOT to test**

* UI code (CustomTkinter widgets) — too coupled to the event loop

* PyInstaller packaging

## **Test structure**

| \# tests/test\_backup.py import pytest from pathlib import Path from src.models import Game from src.core.backup import do\_backup, do\_restore, list\_backups, delete\_backup def make\_game(tmp\_path: Path) \-\> Game:     source \= tmp\_path / 'save'     source.mkdir()     (source / 'world.bin').write\_bytes(b'data')     return Game(id='test-id', name='Test Game',                 source\_path=str(source),                 backup\_path=str(tmp\_path / 'backups')) def test\_backup\_creates\_folder(tmp\_path):     game \= make\_game(tmp\_path)     entry \= do\_backup(game)     assert Path(entry.path).exists()     assert (Path(entry.path) / 'world.bin').exists() def test\_restore\_replaces\_source(tmp\_path):     game \= make\_game(tmp\_path)     entry \= do\_backup(game)     \# Modify source     (Path(game.source\_path) / 'world.bin').write\_bytes(b'corrupted')     do\_restore(game, entry)     assert (Path(game.source\_path) / 'world.bin').read\_bytes() \== b'data' |
| :---- |

# **8\. Build & Distribution**

## **Requirements**

| \# requirements.txt customtkinter\>=5.2.0 \# requirements-dev.txt \-r requirements.txt pyinstaller\>=6.0 pytest\>=8.0 |
| :---- |

## **PyInstaller command**

| pyinstaller \\   \--onefile \\   \--windowed \\   \--name GameBackupManager \\   \--icon assets/icon.ico \\   \--add-data "assets;assets" \\   src/app.py |
| :---- |

## **Output**

dist/GameBackupManager.exe — single file, \~20 MB, no install required. config.json is created on first run next to the .exe.

| ⚠  Always test the packaged .exe on a clean Windows machine (or VM) before distributing. CustomTkinter occasionally has hidden data file dependencies. |
| :---- |

# **9\. Git Conventions**

## **Branches**

* main — stable, always buildable

* dev — integration branch

* feature/\<name\> — individual features

* fix/\<name\> — bug fixes

## **Commit messages**

| feat: add delete backup confirmation dialog fix: restore crash when backup path has spaces refactor: extract folder\_size to utils test: add restore replaces source test chore: update pyinstaller to 6.1 |
| :---- |

## **.gitignore**

| \_\_pycache\_\_/ \*.pyc dist/ build/ \*.spec config.json .venv/ |
| :---- |

