"""Right panel displaying backups for the selected game."""
import customtkinter as ctk
import threading
from typing import Optional, List
from datetime import datetime

from src.core.models import Game, BackupEntry
from src.core.backup import list_backups, do_backup, do_restore, delete_backup
from src.ui.dialogs import confirm, show_progress, alert


class BackupPanel(ctk.CTkFrame):
    """Right panel with backup list and action buttons."""

    def __init__(self, parent, game: Optional[Game] = None):
        super().__init__(parent)
        self.game: Optional[Game] = None
        self.selected_backup: Optional[BackupEntry] = None
        self.backups: List[BackupEntry] = []

        # Title
        ctk.CTkLabel(
            self,
            text="Backups",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)

        # Backup list (scrollable)
        self.backup_list = ctk.CTkScrollableFrame(
            self,
            label_text="Available Backups"
        )
        self.backup_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Info label
        self.info_label = ctk.CTkLabel(
            self,
            text="Select a game to see backups",
            text_color="gray"
        )
        self.info_label.pack(pady=5)

        # Action buttons frame
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5)

        self.backup_btn = ctk.CTkButton(
            btn_frame,
            text="Backup",
            command=self.backup,
            width=80
        )
        self.backup_btn.pack(side="left", padx=2)

        self.restore_btn = ctk.CTkButton(
            btn_frame,
            text="Restore",
            command=self.restore,
            width=80,
            state="disabled"
        )
        self.restore_btn.pack(side="left", padx=2)

        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=self.delete,
            width=80,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=2)

        # Set initial state
        if game:
            self.set_game(game)

    def set_game(self, game: Optional[Game]):
        """Set the current game and refresh the backup list."""
        self.game = game
        self.selected_backup = None

        if game:
            self.info_label.configure(text=f"Backups for: {game.name}")
            self.backup_btn.configure(state="normal")
        else:
            self.info_label.configure(text="Select a game to see backups")
            self.backup_btn.configure(state="disabled")

        self.restore_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")

        self.refresh()

    def refresh(self):
        """Reload backups for the selected game."""
        # Clear existing items
        for widget in self.backup_list.winfo_children():
            widget.destroy()

        if not self.game:
            return

        # Load backups
        self.backups = list_backups(self.game)

        if not self.backups:
            ctk.CTkLabel(
                self.backup_list,
                text="No backups yet",
                text_color="gray"
            ).pack(pady=10)
            return

        # Create items for each backup
        for backup in self.backups:
            item = BackupListItem(
                self.backup_list,
                backup,
                on_select=self._on_backup_select
            )
            item.pack(fill="x", padx=5, pady=2)

    def _on_backup_select(self, backup: BackupEntry):
        """Handle backup selection."""
        self.selected_backup = backup

        # Update visual selection
        for widget in self.backup_list.winfo_children():
            if isinstance(widget, BackupListItem):
                widget.set_selected(backup == self.selected_backup)

        # Enable action buttons
        self.restore_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")

    def backup(self):
        """Run backup operation in a background thread."""
        if not self.game:
            return

        # Show progress dialog
        progress = show_progress(self, "Backup in Progress")
        progress.update("Starting backup...")

        def run_backup():
            try:
                def update_progress(msg: str):
                    self.after(0, lambda: progress.update(msg))

                entry = do_backup(self.game, on_progress=update_progress)

                self.after(0, lambda: (
                    progress.close(),
                    self.refresh(),
                    alert(self, "Backup Complete", f"Backup created: {entry.name}")
                ))
            except Exception as e:
                self.after(0, lambda: (
                    progress.close(),
                    alert(self, "Backup Failed", str(e))
                ))

        thread = threading.Thread(target=run_backup, daemon=True)
        thread.start()

    def restore(self):
        """Show confirmation dialog, then restore in background."""
        if not self.game or not self.selected_backup:
            return

        def handle_confirm(result: bool):
            if not result:
                return

            progress = show_progress(self, "Restore in Progress")
            progress.update("Restoring backup...")

            def run_restore():
                try:
                    def update_progress(msg: str):
                        self.after(0, lambda: progress.update(msg))

                    do_restore(self.game, self.selected_backup, on_progress=update_progress)

                    self.after(0, lambda: (
                        progress.close(),
                        alert(self, "Restore Complete", "Backup restored successfully!")
                    ))
                except Exception as e:
                    self.after(0, lambda: (
                        progress.close(),
                        alert(self, "Restore Failed", str(e))
                    ))

            thread = threading.Thread(target=run_restore, daemon=True)
            thread.start()

        confirm(
            self,
            title="Confirm Restore",
            message=f"Restore backup '{self.selected_backup.name}'? This will overwrite current save data.",
            on_result=handle_confirm
        )

    def delete(self):
        """Show confirmation dialog, then delete backup."""
        if not self.selected_backup:
            return

        def handle_confirm(result: bool):
            if not result:
                return

            try:
                delete_backup(self.selected_backup)
                self.selected_backup = None
                self.restore_btn.configure(state="disabled")
                self.delete_btn.configure(state="disabled")
                self.refresh()
                alert(self, "Delete Complete", "Backup deleted successfully!")
            except Exception as e:
                alert(self, "Delete Failed", str(e))

        confirm(
            self,
            title="Confirm Delete",
            message=f"Delete backup '{self.selected_backup.name}'? This cannot be undone.",
            on_result=handle_confirm
        )


class BackupListItem(ctk.CTkFrame):
    """Single backup item in the list."""

    def __init__(
        self,
        parent,
        backup: BackupEntry,
        on_select: callable
    ):
        super().__init__(parent, fg_color="transparent")
        self.backup = backup
        self.on_select = on_select
        self.is_selected = False

        # Clickable button
        self.btn = ctk.CTkButton(
            self,
            text="",
            command=self._on_click,
            fg_color="transparent",
            border_width=1,
            height=40,
            text_color=("gray10", "gray90")
        )
        self.btn.pack(fill="x")

        # Layout: name on left, date/size on right
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.place(relx=0.02, rely=0.1, relwidth=0.96, relheight=0.8)

        # Left side: backup name
        ctk.CTkLabel(
            info_frame,
            text=backup.name,
            anchor="w",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=5)

        # Right side: date and size
        date_str = backup.created_at.strftime("%Y-%m-%d %H:%M")
        size_str = self._format_size(backup.size_bytes)
        info_frame.pack_configure()

        ctk.CTkLabel(
            info_frame,
            text=f"{date_str} | {size_str}",
            anchor="e",
            text_color="gray"
        ).pack(side="right", padx=5)

    def _on_click(self):
        """Handle click on the backup item."""
        self.on_select(self.backup)

    def set_selected(self, selected: bool):
        """Update visual state for selection."""
        self.is_selected = selected
        if selected:
            self.btn.configure(fg_color=("gray75", "gray25"))
        else:
            self.btn.configure(fg_color="transparent")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format size in human-readable form."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"