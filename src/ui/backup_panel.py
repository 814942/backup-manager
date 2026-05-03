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
        """Reload backups for the selected game - in background thread."""
        # Clear existing items
        for widget in self.backup_list.winfo_children():
            widget.destroy()

        if not self.game:
            return

        # Show loading state
        loading = ctk.CTkLabel(
            self.backup_list,
            text="Loading backups...",
            text_color="gray"
        )
        loading.pack(pady=10)
        
        # Load in background thread to avoid UI freeze
        def load_backups():
            try:
                backups = list_backups(self.game)
                self.after(0, lambda: self._display_backups(backups))
            except Exception as e:
                self.after(0, lambda: self._display_error(str(e)))
        
        thread = threading.Thread(target=load_backups, daemon=True)
        thread.start()

    def _display_backups(self, backups):
        """Display the loaded backups."""
        # Clear loading
        for widget in self.backup_list.winfo_children():
            widget.destroy()
        
        self.backups = backups

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

    def _display_error(self, error_msg):
        """Display error state."""
        for widget in self.backup_list.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self.backup_list,
            text=f"Error: {error_msg}",
            text_color="red"
        ).pack(pady=10)

    def _on_backup_select(self, backup: BackupEntry):
        """Handle backup selection - only the clicked one."""
        # First, deselect all others
        for widget in self.backup_list.winfo_children():
            if isinstance(widget, BackupListItem):
                widget.set_selected(False)
        
        # Then select only this one
        self.selected_backup = backup
        for widget in self.backup_list.winfo_children():
            if isinstance(widget, BackupListItem) and widget.backup == backup:
                widget.set_selected(True)
                break

        # Enable action buttons only if we have a selection
        has_selection = backup is not None
        self.restore_btn.configure(state="normal" if has_selection else "disabled")
        self.delete_btn.configure(state="normal" if has_selection else "disabled")

    def backup(self):
        """Run backup operation in a background thread."""
        if not self.game:
            return
        
        # Disable buttons during operation
        self._set_buttons_enabled(False)
        
        # Show progress dialog
        progress = show_progress(self, "Creating Backup")
        progress.update("[1/2] Preparing...")
        
        def run_backup():
            try:
                def update_progress(msg: str):
                    # Simple string callback
                    self.after(0, lambda m=msg: progress.update(m))
                
                progress.update("[2/2] Copying files...")
                entry = do_backup(self.game, on_progress=update_progress)
                
                self.after(0, lambda: (
                    progress.close(),
                    self.refresh(),
                    self._set_buttons_enabled(True),
                    alert(self, "Backup Complete", f"Saved: {entry.name} ({self._format_size(entry.size_bytes)})")
                ))
            except Exception as e:
                self.after(0, lambda: (
                    progress.close(),
                    self._set_buttons_enabled(True),
                    alert(self, "Backup Failed", str(e))
                ))
        
        thread = threading.Thread(target=run_backup, daemon=True)
        thread.start()

    def _set_buttons_enabled(self, enabled: bool):
        """Enable/disable all action buttons."""
        state = "normal" if enabled else "disabled"
        self.backup_btn.configure(state=state)
        self.restore_btn.configure(state=state)
        self.delete_btn.configure(state=state)

    def restore(self):
        """Show confirmation dialog, then restore in background."""
        if not self.game or not self.selected_backup:
            return

        def handle_confirm(result: bool):
            if not result:
                return

            self._set_buttons_enabled(False)
            progress = show_progress(self, "Restoring Backup")
            progress.update("[1/2] Preparing...")

            def run_restore():
                try:
                    def update_progress(msg: str):
                        self.after(0, lambda m=msg: progress.update(m))

                    progress.update("[2/2] Restoring files...")
                    do_restore(self.game, self.selected_backup, on_progress=update_progress)

                    self.after(0, lambda: (
                        progress.close(),
                        self._set_buttons_enabled(True),
                        alert(self, "Restore Complete", f"Restored from: {self.selected_backup.name}")
                    ))
                except Exception as e:
                    self.after(0, lambda: (
                        progress.close(),
                        self._set_buttons_enabled(True),
                        alert(self, "Restore Failed", str(e))
                    ))

            thread = threading.Thread(target=run_restore, daemon=True)
            thread.start()

        confirm(
            self,
            title="Confirm Restore",
            message=f"Restore '{self.selected_backup.name}'? This will overwrite current save data.",
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
    """Single backup item in the list with improved styling."""

    SELECTED_COLOR = "#49F0F0"  # CTk blue
    HOVER_COLOR = ("gray75", "gray30")
    
    def __init__(
        self,
        parent,
        backup: BackupEntry,
        on_select: callable
    ):
        super().__init__(
            parent, 
            fg_color="transparent",
            corner_radius=8
        )
        self.backup = backup
        self.on_select = on_select
        self.is_selected = False

        # Make entire row clickable with full-width hitbox
        # Use CTkFrame with proper size that expands
        self.hitbox = ctk.CTkFrame(
            self,
            fg_color="transparent",
            cursor="hand2",
            corner_radius=8,
            width=300,
            height=40
        )
        self.hitbox.pack(fill="x", padx=2, pady=2)
        self.hitbox.pack_propagate(False)  # Don't shrink to content
        
        # Bind click directly to the hitbox frame
        self.hitbox.bind("<Button-1>", lambda e: self._on_click())
        self.hitbox.bind("<Enter>", lambda e: self._on_hover(True))
        self.hitbox.bind("<Leave>", lambda e: self._on_hover(False))

        # Content layout - placed inside hitbox
        content = ctk.CTkFrame(self.hitbox, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)

        # Left: backup name - also clickable
        name_label = ctk.CTkLabel(
            content,
            text=backup.name,
            anchor="w",
            font=ctk.CTkFont(size=11, weight="bold"),
            cursor="hand2"
        )
        name_label.pack(side="left", padx=5)
        name_label.bind("<Button-1>", lambda e: self._on_click())
        name_label.bind("<Enter>", lambda e: self._on_hover(True))
        name_label.bind("<Leave>", lambda e: self._on_hover(False))

        # Right: date and size - also clickable
        date_str = backup.created_at.strftime("%Y-%m-%d %H:%M")
        size_str = self._format_size(backup.size_bytes)
        
        size_label = ctk.CTkLabel(
            content,
            text=f"{size_str} | {date_str}",
            anchor="e",
            text_color="#49F0F0",
            font=ctk.CTkFont(size=10),
            cursor="hand2"
        )
        size_label.pack(side="right", padx=5)
        size_label.bind("<Button-1>", lambda e: self._on_click())
        size_label.bind("<Enter>", lambda e: self._on_hover(True))
        size_label.bind("<Leave>", lambda e: self._on_hover(False))

    def _on_click(self):
        """Handle click on the backup item."""
        self.on_select(self.backup)

    def _on_hover(self, entering: bool):
        """Handle hover effect."""
        if not self.is_selected and entering:
            self.hitbox.configure(fg_color=self.HOVER_COLOR)
        elif not self.is_selected:
            self.hitbox.configure(fg_color="transparent")

    def set_selected(self, selected: bool):
        """Update visual state for selection."""
        self.is_selected = selected
        if selected:
            self.hitbox.configure(fg_color=self.SELECTED_COLOR)
        else:
            self.hitbox.configure(fg_color="transparent")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format size in human-readable form."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"