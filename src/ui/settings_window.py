"""Settings window for managing games."""
import customtkinter as ctk
import tkinter.filedialog as fd
from typing import List

from src.core.config import load_config, save_config, add_game, remove_game
from src.core.models import Game
from src.ui.dialogs import confirm, alert


class SettingsWindow(ctk.CTkToplevel):
    """Settings window for managing game configurations."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("550x450")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        ctk.CTkLabel(
            self,
            text="Manage Games",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.game_listbox = ctk.CTkScrollableFrame(list_frame, label_text="Configured Games")
        self.game_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        add_frame = ctk.CTkFrame(self)
        add_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            add_frame, text="Add New Game:", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=5, sticky="w")

        ctk.CTkLabel(add_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ctk.CTkEntry(add_frame, width=150)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(add_frame, text="Save Folder:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.source_entry = ctk.CTkEntry(add_frame, width=200)
        self.source_entry.grid(row=2, column=1, padx=5, pady=5)
        ctk.CTkButton(add_frame, text="Browse", command=self.browse_source, width=80).grid(row=2, column=2, padx=5, pady=5)

        ctk.CTkLabel(add_frame, text="Backup Folder:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.backup_entry = ctk.CTkEntry(add_frame, width=200)
        self.backup_entry.grid(row=3, column=1, padx=5, pady=5)
        ctk.CTkButton(add_frame, text="Browse", command=self.browse_backup, width=80).grid(row=3, column=2, padx=5, pady=5)

        ctk.CTkButton(add_frame, text="Add Game", command=self.add_game, width=100).grid(row=4, column=1, pady=10)

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(pady=10)

        ctk.CTkButton(
            bottom_frame, text="Remove Selected", command=self.remove_selected,
            width=120, fg_color="#d9534f", hover_color="#c9302c"
        ).pack(side="left", padx=5)

        ctk.CTkButton(bottom_frame, text="Close", command=self.destroy, width=80).pack(side="left", padx=20)

        self.refresh()

    def refresh(self):
        """Reload the game list from config."""
        for widget in self.game_listbox.winfo_children():
            widget.destroy()

        config = load_config()
        self.games: List[Game] = config.games

        if not self.games:
            ctk.CTkLabel(self.game_listbox, text="No games configured", text_color="gray").pack(pady=10)
            return

        for game in self.games:
            GameListItem(self.game_listbox, game).pack(fill="x", padx=5, pady=2)

    def browse_source(self):
        """Open dialog to select game save folder."""
        path = fd.askdirectory(title="Select Game Save Folder")
        if path:
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, path)

    def browse_backup(self):
        """Open dialog to select backup destination folder."""
        path = fd.askdirectory(title="Select Backup Destination")
        if path:
            self.backup_entry.delete(0, "end")
            self.backup_entry.insert(0, path)

    def add_game(self):
        """Add a new game from form inputs."""
        name = self.name_entry.get().strip()
        source = self.source_entry.get().strip()
        backup = self.backup_entry.get().strip()

        if not name or not source or not backup:
            err_label = ctk.CTkLabel(self, text="All fields are required!", text_color="red")
            err_label.place(relx=0.5, rely=0.95, anchor="center")
            self.after(2000, err_label.destroy)
            return

        config = load_config()
        add_game(config, name, source, backup)

        self.name_entry.delete(0, "end")
        self.source_entry.delete(0, "end")
        self.backup_entry.delete(0, "end")

        self.refresh()

    def remove_selected(self):
        """Remove selected game from config."""
        selected = None
        for widget in self.game_listbox.winfo_children():
            if isinstance(widget, GameListItem) and widget.is_selected:
                selected = widget.game
                break

        if not selected:
            alert(self, "No Selection", "Please select a game to remove.")
            return

        def handle_confirm(result: bool):
            if result:
                config = load_config()
                remove_game(config, selected.id)
                self.refresh()

        confirm(
            self,
            title="Remove Game",
            message=f"Remove '{selected.name}' from the list?",
            on_result=handle_confirm
        )


class GameListItem(ctk.CTkFrame):
    """Single game item in the settings list."""

    def __init__(self, parent, game: Game):
        super().__init__(parent, fg_color="transparent")
        self.game = game
        self.is_selected = False

        self.btn = ctk.CTkButton(
            self, text="", command=self._on_click,
            fg_color="transparent", border_width=1,
            height=50, text_color=("gray10", "gray90")
        )
        self.btn.pack(fill="x")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.place(relx=0.02, rely=0.1, relwidth=0.96, relheight=0.8)

        ctk.CTkLabel(
            content, text=game.name,
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w"
        ).pack(side="left", padx=5)

        src_text = f"Src: {game.source_path[:30]}..." if len(game.source_path) > 30 else f"Src: {game.source_path}"
        ctk.CTkLabel(
            content, text=src_text,
            text_color="gray", font=ctk.CTkFont(size=10), anchor="w"
        ).pack(side="left", padx=10)

    def _on_click(self):
        for widget in self.winfo_parent().winfo_children():
            if isinstance(widget, GameListItem) and widget != self:
                widget.set_selected(False)
        self.set_selected(not self.is_selected)

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.btn.configure(fg_color=("gray75", "gray25") if selected else "transparent")