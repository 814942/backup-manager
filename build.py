#!/usr/bin/env python3
"""Build script for Backup Manager using PyInstaller."""
import PyInstaller.__main__
from pathlib import Path
import sys
import shutil

APP_NAME = "BackupManager"
VERSION = "1.0.0"


def build():
    """Build the .exe using PyInstaller."""
    print(f"Building {APP_NAME} v{VERSION}...")

    # Create assets directory if needed
    assets = Path("assets")
    assets.mkdir(exist_ok=True)

    # Check if icon exists
    icon_path = assets / "icon.ico"
    icon_args = []
    if icon_path.exists():
        icon_args = ["--icon", str(icon_path)]

    args = [
        "--name", APP_NAME,
        "--onefile",           # Single .exe
        "--windowed",         # No console window
        "--clean",           # Clean build cache
        "--add-data", "src:src",  # Include src package
        "--hidden-import", "customtkinter",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL._tkinter_finder",
        "--collect-all", "ctk",
        "src/app.py",
    ] + icon_args

    # Remove icon arg if icon doesn't exist
    if not icon_path.exists():
        args = [a for a in args if a != "--icon" and args[args.index(a)-1] != "--icon"]

    PyInstaller.__main__.run(args)
    print(f"\nBuild complete: dist/{APP_NAME}.exe")

    # Copy the exe to a more accessible location
    dist_exe = Path("dist") / f"{APP_NAME}.exe"
    if dist_exe.exists():
        print(f"Executable size: {dist_exe.stat().st_size / (1024*1024):.2f} MB")


if __name__ == "__main__":
    build()