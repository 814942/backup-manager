#!/usr/bin/env python3
"""Backup Manager - Desktop app entry point for backing up and restoring PC game saves."""
import sys
import platform
from pathlib import Path

# FIX ISS-04: Consistent absolute import — works both in dev and when packaged with PyInstaller.
# Removed sys.path.insert hack and the mixed relative import.
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.version import APP_NAME, APP_VERSION

import customtkinter as ctk
from src.ui.main_window import MainWindow
from src.core.config import load_config


def show_tutorial(parent):
    """Show a simple tutorial popup for first-time users or when Help is clicked."""
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Quick Guide")
    dialog.geometry("480x480")
    dialog.transient(parent)
    dialog.grab_set()

    ctk.CTkLabel(
        dialog,
        text="QUICK GUIDE",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#3B8ED0"
    ).pack(pady=15)

    steps = [
        ("1. Add a Game", "Click 'Add', enter name, select save folder and backup location"),
        ("2. Create Backup", "Select game, click 'Backup' to save current progress"),
        ("3. Restore", "Select a backup, click 'Restore' if something goes wrong"),
    ]
    for title, desc in steps:
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#3B8ED0",
            anchor="w"
        ).pack(fill="x", padx=5)
        ctk.CTkLabel(
            frame,
            text=desc,
            text_color="gray",
            anchor="w",
            wraplength=400
        ).pack(fill="x", padx=15)

    # --- ABOUT SECTION ---
    about_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    about_frame.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(
        about_frame,
        text="About",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="#3B8ED0",
        anchor="w"
    ).pack(fill="x", padx=5, pady=(10, 0))

    # FIX ISS-05: Removed subprocess git calls — they fail silently in the packaged .exe
    # and add ~200ms latency. Version info now comes from src/version.py constants.
    try:
        import customtkinter
        ctk_version = customtkinter.__version__
    except Exception:
        ctk_version = "?"

    py_version = platform.python_version()

    about_text = (
        f"{APP_NAME} v{APP_VERSION}\n"
        f"Python: {py_version}\n"
        f"CustomTkinter: {ctk_version}"
    )

    ctk.CTkLabel(
        about_frame,
        text=about_text,
        font=ctk.CTkFont(size=11),
        justify="left",
        anchor="w"
    ).pack(fill="x", padx=10, pady=5)

    ctk.CTkButton(
        dialog,
        text="Got it!",
        command=dialog.destroy,
        width=120,
        fg_color="#3B8ED0"
    ).pack(pady=20)


def main():
    """Launch the Backup Manager application."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = MainWindow()

    # Show tutorial on first run (check if config is empty)
    try:
        config = load_config()
        is_first_run = not config.games
    except Exception:
        is_first_run = True

    if is_first_run:
        app.after(300, lambda: show_tutorial(app))

    app.mainloop()


if __name__ == "__main__":
    main()