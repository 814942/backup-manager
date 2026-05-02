#!/usr/bin/env python3
"""Backup Manager - Desktop app entry point for backing up and restoring PC game saves."""
import sys
from pathlib import Path

# Add src to path for relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import customtkinter as ctk
from src.ui.main_window import MainWindow
from src.core.config import load_config


def main():
    """Launch the Backup Manager application."""
    # Configure CustomTkinter appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and launch the main window
    app = MainWindow()
    
    # Check if first run (no games configured)
    config = load_config()
    if not config.games:
        # First run: prompt user to add their first game
        app.after(100, lambda: app.game_panel.show_first_run_prompt())
    
    # Start the application main loop
    app.mainloop()


if __name__ == "__main__":
    main()