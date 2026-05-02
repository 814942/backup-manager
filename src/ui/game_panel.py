"""Left panel displaying the list of registered games."""
import customtkinter as ctk
from typing import Callable, Optional, List
from src.core.config import load_config, save_config, add_game, remove_game
from src.core.models import Game


class GamePanel(ctk.CTkFrame):
    """Left panel with game list and Add/Remove buttons."""

    def __init__(self, parent, on_select: Callable[[Game], None]):
        super().__init__(parent)
        self.on_select = on_select
        self.selected_game: Optional[Game] = None

        # Title
        ctk.CTkLabel(
            self,
            text="Games",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)

        # Game list (scrollable)
        self.game_list = ctk.CTkScrollableFrame(
            self,
            label_text="Registered Games"
        )
        self.game_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5)

        ctk.CTkButton(
            btn_frame,
            text="Add",
            command=self.add_game,
            width=80
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="Remove",
            command=self.remove_game,
            width=80
        ).pack(side="left", padx=2)

        # Store button references for enable/disable
        self._remove_btn = btn_frame.winfo_children()[1]

        # Initial load
        self.refresh()

    def refresh(self):
        """Reload games from config and rebuild the list."""
        # Clear existing items
        for widget in self.game_list.winfo_children():
            widget.destroy()

        # Load games
        config = load_config()
        self.games: List[Game] = config.games

        # Create buttons for each game
        for game in self.games:
            btn = ctk.CTkButton(
                self.game_list,
                text=game.name,
                command=lambda g=game: self._on_game_click(g),
                fg_color="transparent",
                border_width=1,
                height=35
            )
            btn.pack(fill="x", padx=5, pady=2)

        # Update remove button state
        self._update_buttons()

    def _on_game_click(self, game: Game):
        """Handle game selection."""
        self.selected_game = game
        self._update_buttons()
        # Update visual selection
        for widget in self.game_list.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                if widget.cget("text") == game.name:
                    widget.configure(fg_color=("gray75", "gray25"))
                else:
                    widget.configure(fg_color="transparent")
        # Trigger callback
        self.on_select(game)

    def _update_buttons(self):
        """Update button states based on selection."""
        has_selection = self.selected_game is not None
        self._remove_btn.configure(state="normal" if has_selection else "disabled")

    def add_game(self):
        """Open inline form to add a new game."""
        # Check if form already exists
        if hasattr(self, '_add_form') and self._add_form.winfo_exists():
            return

        # Create a toplevel for adding game
        form = ctk.CTkToplevel(self)
        form.title("Add Game")
        form.geometry("500x280")
        form.transient(self)
        form.grab_set()

        # Store reference for later checks
        self._add_form = form

        ctk.CTkLabel(
            form,
            text="Add New Game",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)

        # Name entry
        name_frame = ctk.CTkFrame(form)
        name_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(name_frame, text="Game Name:").pack(side="left", padx=5)
        name_entry = ctk.CTkEntry(name_frame, width=250)
        name_entry.pack(side="left", padx=5)

        # Path entries
        source_path = ctk.StringVar()
        backup_path = ctk.StringVar()

        source_frame = ctk.CTkFrame(form)
        source_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(source_frame, text="Save Folder:").pack(side="left", padx=5)
        ctk.CTkLabel(source_frame, textvariable=source_path, width=30).pack(side="left", padx=5)

        backup_frame = ctk.CTkFrame(form)
        backup_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(backup_frame, text="Backup Folder:").pack(side="left", padx=5)
        ctk.CTkLabel(backup_frame, textvariable=backup_path, width=30).pack(side="left", padx=5)

        def browse_source():
            import tkinter.filedialog as fd
            path = fd.askdirectory(title="Select Game Save Folder")
            if path:
                source_path.set(path)

        def browse_backup():
            import tkinter.filedialog as fd
            path = fd.askdirectory(title="Select Backup Destination")
            if path:
                backup_path.set(path)

        # Button frame
        btn_frame = ctk.CTkFrame(form)
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Browse",
            command=browse_source,
            width=80
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="Browse",
            command=browse_backup,
            width=80
        ).pack(side="left", padx=2)

        def do_add():
            name = name_entry.get().strip()
            src = source_path.get().strip()
            dst = backup_path.get().strip()

            if not name or not src or not dst:
                # Show error
                ctk.CTkLabel(
                    form,
                    text="All fields required!",
                    text_color="red"
                ).pack(pady=5)
                return

            config = load_config()
            add_game(config, name, src, dst)
            form.destroy()
            self.refresh()

        ctk.CTkButton(
            btn_frame,
            text="Add Game",
            command=do_add,
            width=100
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=form.destroy,
            width=80
        ).pack(side="left", padx=2)

    def remove_game(self):
        """Remove selected game after confirmation."""
        from src.ui.dialogs import confirm

        if not self.selected_game:
            return

        def handle_confirm(result: bool):
            if result:
                config = load_config()
                remove_game(config, self.selected_game.id)
                self.selected_game = None
                self.refresh()
                # Clear backup panel
                self.on_select(None)

        confirm(
            self,
            title="Remove Game",
            message=f"Remove '{self.selected_game.name}' from the list?",
            on_result=handle_confirm
        )

    def show_first_run_prompt(self):
        """Show the add game form on first run."""
        self.add_game()