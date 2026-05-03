# Backup Manager

A Windows desktop app for backing up and restoring PC game saves. Modern GUI, no terminal, no complex setup required.

## Features

- **Register games** — Name, save folder, backup destination
- **One-click backup** — Automatic copy with timestamp
- **Restore** — Recover from any previous backup
- **Delete backups** — Manage storage space
- **Settings** — Add/edit/remove games

## Requirements

- Python 3.11+
- CustomTkinter

## Installation

```bash
# Clone the repo
git clone https://github.com/814942/backup-manager.git

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python src/app.py
```

Or build the .exe:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name BackupManager src/app.py
```

The .exe will be in `dist/BackupManager.exe`.

## Ejecución recomendada

Para ejecutar la aplicación correctamente (con imports absolutos y sin errores de módulo):

```
python -m src.app
```

Ejecuta este comando desde la raíz del proyecto (donde está la carpeta `src/`).

- Si ejecutas `python src/app.py` directamente, los imports absolutos fallarán.
- Este método es compatible con PyInstaller y otras herramientas de empaquetado.

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Contributing
1. Create branch: git checkout -b feature/name
2. Make changes
3. Commit: git commit -m "description"
4. Push: git push origin feature/name
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| UI | CustomTkinter |
| Tests | pytest |
| Build | PyInstaller |

## License

MIT