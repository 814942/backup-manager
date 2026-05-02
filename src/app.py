#!/usr/bin/env python3
"""Backup Manager - Desktop app entry point for backing up and restoring PC game saves."""
import sys
from pathlib import Path

# Add src to path for relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk
from src.ui.main_window import MainWindow
from src.ui.game_panel import GamePanel
from src.core.config import load_config


def show_tutorial(parent):
    """Show a simple tutorial popup for first-time users."""
    # Check if already seen
    import json
    from pathlib import Path
    
    config_dir = Path.home() / ".config" / "backup-manager"
    config_dir.mkdir(parents=True, exist_ok=True)
    seen_file = config_dir / ".tutorial_seen"
    
    if seen_file.exists():
        return  # Already seen
    
    # Create tutorial dialog
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Cómo usar Backup Manager")
    dialog.geometry("500x400")
    dialog.transient(parent)
    dialog.grab_set()
    
    ctk.CTkLabel(
        dialog,
        text="📦 Guía Rápida",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#00B4D8"
    ).pack(pady=15)
    
    # Steps
    steps = [
        ("1️⃣ Agregar un Juego", "Clickeá 'Add', completá nombre del juego y seleccioná las carpetas"),
        ("2️⃣ Crear Backup", "Seleccioná el juego y clickeá 'Backup' para guardar"),
        ("3️⃣ Restore", "Si algo sale mal, seleccioná un backup y clickeá 'Restore'"),
    ]
    
    for title, desc in steps:
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00B4D8",
            anchor="w"
        ).pack(fill="x", padx=5)
        
        ctk.CTkLabel(
            frame,
            text=desc,
            text_color="gray",
            anchor="w",
            wraplength=420
        ).pack(fill="x", padx=15)
    
    # Close button
    ctk.CTkButton(
        dialog,
        text="Entendido ✓",
        command=lambda: (seen_file.write_text("1"), dialog.destroy()),
        width=150,
        fg_color="#00B4D8"
    ).pack(pady=20)
    
    # Open Add Game after closing tutorial
    dialog.bind("<Destroy>", lambda e: parent.after(200, lambda: parent.game_panel.add_game()))


def main():
    """Launch the Backup Manager application."""
    # Configure CustomTkinter appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("cyan")
    
    # Create and launch the main window
    app = MainWindow()
    
    # Show tutorial on first run (check if config is empty)
    try:
        config = load_config()
        is_first_run = not config.games
    except:
        is_first_run = True
    
    if is_first_run:
        app.after(300, lambda: show_tutorial(app))
    
    app.mainloop()


if __name__ == "__main__":
    main()