# Backup Manager

App de escritorio para Windows que permite hacer backup y restore de saves de cualquier juego PC. Interfaz gráfica moderna, sin terminal, sin configuración compleja.

## Características

- **Registrar juegos** — Nombre, carpeta de saves, destino de backups
- **Backup con un click** — Copia automática con timestamp
- **Restaurar** — Recuperar任何一个 backup anterior
- **Eliminar backups** — Gestionar espacio
- **Settings** — Agregar/editar/eliminar juegos

## Requisitos

- Python 3.11+
- CustomTkinter

## Instalación

```bash
# Clonar el repo
git clone https://github.com/814942/backup-manager.git

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

```bash
python src/app.py
```

O generar el .exe:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name BackupManager src/app.py
```

El .exe estará en `dist/BackupManager.exe`.

## Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar tests
pytest tests/ -v

# Contribuir
1. Crear branch: `git checkout -b feature/nombre`
2. Hacer cambios
3. Commitear: `git commit -m "descripción"`
4. Push: `git push origin feature/nombre`
```

## Tech Stack

| Componente | Tecnología |
|-----------|-----------|
| Lenguaje | Python 3.11+ |
| UI | CustomTkinter |
| Tests | pytest |
| Build | PyInstaller |

## Licencia

MIT