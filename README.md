# 🎮 Game Save Backup Manager

> A simple, open-source Windows desktop app to back up and restore PC game saves — no terminal, no scripts, just point and click.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Build](https://img.shields.io/github/actions/workflow/status/814942/backup-manager/build.yml?label=Build&style=flat)
![Release](https://img.shields.io/github/v/release/814942/backup-manager?style=flat)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Download](#download)
- [Screenshots](#screenshots)
- [Getting Started (Development)](#getting-started-development)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Building the .exe](#building-the-exe)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

PC game saves are fragile. A bad update, a corrupted file, or an accidental overwrite can wipe hours of progress.

**Game Save Backup Manager** solves this with a clean desktop UI — register your game, pick a backup folder, and keep as many timestamped snapshots as you want. Restore any of them with two clicks.

Works with **any PC game** — not tied to Steam, Epic, or any platform.

---

## Features

- **Any game** — point the app to any save folder, works everywhere
- **One-click backup** — timestamped copy created instantly
- **Restore from any backup** — select from a list sorted newest first
- **Delete old backups** — manage disk space easily
- **Manage multiple games** — switch between them from the sidebar
- **No terminal required** — fully graphical, designed for non-technical users
- **No install needed** — download the `.exe` and run

---

## Download

Go to the [**Releases**](https://github.com/814942/backup-manager/releases) page and download the latest `GameBackupManager.exe`.

**Requirements:** Windows 10 or later. No Python or other dependencies needed.

---

## Screenshots

> _Coming soon_

---

## Getting Started (Development)

### Prerequisites

- Python 3.11+
- Git

### Setup

```bash
# Clone the repo
git clone https://github.com/814942/backup-manager.git
cd backup-manager

# Install dependencies
pip install -r requirements.txt

# Run the app
python -m src.app
```

> **Note:** Always run with `python -m src.app` from the project root, not `python src/app.py`. This ensures absolute imports resolve correctly.

### Install dev dependencies

```bash
pip install -r requirements-dev.txt
```

---

## Project Structure

```
backup-manager/
  src/
    app.py                  # Entry point
    version.py              # App version constants
    ui/
      main_window.py        # Root window and layout
      game_panel.py         # Left panel: game list
      backup_panel.py       # Right panel: backup list + actions
      settings_window.py    # Settings screen
      dialogs.py            # Confirm / progress / alert dialogs
    core/
      backup.py             # Backup, restore, list, delete logic
      config.py             # Load/save config.json
      utils.py              # Helpers: size, timestamp
      models.py             # Game and BackupEntry dataclasses
  tests/
    test_backup.py
    test_config.py
    test_utils.py
  .github/
    workflows/
      build.yml             # GitHub Actions: auto-build .exe on tag
  requirements.txt
  requirements-dev.txt
  release.ps1               # Release automation script
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests cover core logic only (`core/`). UI code is not tested directly.

---

## Building the .exe

To build manually:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name GameBackupManager src/app.py
```

Output: `dist/GameBackupManager.exe`

### Automated releases

Releases are built automatically via GitHub Actions. To publish a new version:

```bash
.\release.ps1
```

The script updates `version.py`, commits, tags, and pushes. GitHub Actions then builds the `.exe` and attaches it to the release automatically.

---

## Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repo
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the conventions in [`AGENT.md`](AGENT.md)
4. **Run tests** to make sure nothing broke:
   ```bash
   pytest tests/ -v
   ```
5. **Open a Pull Request** against `main` with a clear description of what you changed and why

### Guidelines

- Follow [PEP 8](https://pep8.org/) — line length 100
- Use type hints on all function signatures
- Use `pathlib.Path` for file paths, not `os.path`
- No bare `except` — always catch specific exceptions
- Keep UI and core logic strictly separated (`ui/` never imports from itself into `core/`)
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
  ```
  feat: add auto-backup on schedule
  fix: restore crash when path has spaces
  chore: bump customtkinter to 5.2.1
  ```

### Reporting bugs

Open an [issue](https://github.com/814942/backup-manager/issues) and include:
- What you did
- What you expected
- What actually happened
- Your Windows version

---

## Roadmap

| Version | Features |
|---------|----------|
| **v1.0** | Backup, restore, delete, multi-game support ✅ |
| **v1.1** | Auto-backup on a schedule, max retention (keep last N) |
| **v1.2** | Backup compression (.zip) |
| **v2.0** | Cloud backup destination (Google Drive, OneDrive) |
| **v2.0** | Game auto-detection from known save paths |

Have an idea? Open an [issue](https://github.com/814942/backup-manager/issues) and tag it `enhancement`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| UI | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| Packaging | PyInstaller |
| Tests | pytest |
| CI/CD | GitHub Actions |

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ☕ — contributions welcome
</p>