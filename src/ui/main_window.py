"""Main application window for the backup manager."""
import customtkinter as ctk

from src.ui.game_panel import GamePanel
from src.ui.backup_panel import BackupPanel
from src.ui.settings_window import SettingsWindow
from src.core.models import Game


class MainWindow(ctk.CTk):
    """Main application window with two-panel layout."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Backup Manager")
        self.geometry("850x550")
        self.minsize(650, 450)

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create layout
        self._create_menu_bar()
        self._create_panels()

    def _create_menu_bar(self):
        """Create the bottom menu bar."""
        menu = ctk.CTkFrame(self)
        menu.pack(side="bottom", fill="x", pady=0)

        # Status label - more visible
        self.status_label = ctk.CTkLabel(
            menu,
            text="Ready",
            anchor="w",
            text_color="#3B8ED0",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.status_label.pack(side="left", padx=10, pady=8)

        # Help/Tutorial button
        ctk.CTkButton(
            menu,
            text="Help",
            command=self.show_help,
            width=80,
            fg_color=("gray70", "gray30")
        ).pack(side="right", padx=10, pady=5)

    def show_help(self):
        """Show the tutorial/help dialog."""
        from src.app import show_tutorial
        show_tutorial(self)

    def _create_panels(self):
        """Create left and right panels."""
        # Main content frame
        content = ctk.CTkFrame(self)
        content.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # Left panel: Game list
        self.game_panel = GamePanel(
            content,
            on_select=self.on_game_select
        )
        self.game_panel.pack(side="left", fill="both", padx=(0, 5), pady=0)

        # Right content: header + backup list
        right_content = ctk.CTkFrame(content)
        right_content.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=0)

        # Game selection indicator (more visible)
        self.game_header = ctk.CTkLabel(
            right_content,
            text="▶ Select a game to see backups",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#3B8ED0"
        )
        self.game_header.pack(pady=(5, 0))

        # Right panel: Backup list
        self.backup_panel = BackupPanel(
            right_content,
            game=None
        )
        self.backup_panel.pack(side="top", fill="both", expand=True, padx=0, pady=5)

    def on_game_select(self, game: Game):
        """Handle game selection from the game panel."""
        if game:
            self.backup_panel.set_game(game)
            self.game_header.configure(text=f"▶ {game.name} • {game.source_path}")
        else:
            self.backup_panel.set_game(None)
            self.game_header.configure(text="▶ Seleccioná un juego para ver backups")

    def open_settings(self):
        """Open the settings window."""
        SettingsWindow(self)
        # Refresh game list after settings window closes
        self.game_panel.refresh()
        self.status_label.configure(text="Settings closed, game list refreshed")

    def run(self):
        """Start the application main loop."""
        self.mainloop()


def main():
    """Entry point for running the application."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()