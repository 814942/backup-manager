"""Right panel displaying backups for the selected game."""
import customtkinter as ctk
import threading
from typing import Optional, List
from datetime import datetime

from src.core.models import Game, BackupEntry
from src.core.backup import list_backups, do_backup, do_restore, delete_backup, list_files_for_backup

from src.ui.dialogs import confirm, show_progress, alert

# --- UTILITIES ---
def format_size(size_bytes: int) -> str:
    """Format size in human-readable form."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


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

        # Action buttons frame (hidden by default)
        self.btn_frame = ctk.CTkFrame(self)
        # No pack yet: will be packed only when a game is selected

        self.backup_btn = ctk.CTkButton(
            self.btn_frame,
            text="Backup",
            command=self.backup,
            width=80
        )
        self.backup_btn.pack(side="left", padx=2)

        self.restore_btn = ctk.CTkButton(
            self.btn_frame,
            text="Restore",
            command=self.restore,
            width=80,
            state="disabled"
        )
        self.restore_btn.pack(side="left", padx=2)

        self.delete_btn = ctk.CTkButton(
            self.btn_frame,
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

        # Hide action buttons if no game selected
        self.btn_frame.pack_forget()

        if game:
            self.info_label.configure(text=f"Backups for: {game.name}")
            self.backup_btn.configure(state="normal")
            self.btn_frame.pack(pady=5)
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
        """Prompt user to select a folder to backup, then run backup operation in a background thread."""
        if not self.game:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Select file to backup")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Select the file or folder to backup:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)

        spinner = ctk.CTkLabel(dialog, text="Loading...", text_color="gray")
        spinner.pack(pady=20)

        def load_folders():
            try:
                folders = list_files_for_backup(self.game)
                self.after(0, lambda: show_folders(folders))
            except Exception as e:
                self.after(0, lambda: show_folders([], str(e)))

        def show_folders(folders, error=None):
            spinner.destroy()
            if error:
                ctk.CTkLabel(dialog, text=f"Error: {error}", text_color="red").pack(pady=10)
                return
            if not folders:
                ctk.CTkLabel(dialog, text="No folders found", text_color="gray").pack(pady=10)
                return
            table_frame = ctk.CTkFrame(dialog)
            table_frame.pack(padx=10, pady=10, fill="both", expand=True)
            ctk.CTkLabel(table_frame, text="Nombre", font=ctk.CTkFont(weight="bold"), width=30, anchor="w").grid(row=0, column=0, sticky="w", padx=5)
            ctk.CTkLabel(table_frame, text="Fecha", font=ctk.CTkFont(weight="bold"), width=20, anchor="w").grid(row=0, column=1, sticky="w", padx=5)
            for idx, folder in enumerate(folders, start=1):
                fecha = datetime.fromtimestamp(folder.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                btn = ctk.CTkButton(table_frame, text=folder.name, width=30, anchor="w", fg_color="transparent", hover_color="#e0eaff",
                                    command=lambda f=folder: select_folder(f))
                btn.grid(row=idx, column=0, sticky="w", padx=5, pady=1)
                ctk.CTkLabel(table_frame, text=fecha, width=20, anchor="w").grid(row=idx, column=1, sticky="w", padx=5, pady=1)

        def select_folder(folder_to_backup):
            dialog.destroy()
            self._run_backup_with_file(folder_to_backup)

        thread = threading.Thread(target=load_folders, daemon=True)
        thread.start()

    def _run_backup_with_file(self, file_to_backup):
        self._set_buttons_enabled(False)
        progress = show_progress(self, "Creating Backup")
        progress.update("[1/2] Preparing...")

        def run_backup():
            try:
                def update_progress(msg: str):
                    self.after(0, lambda m=msg: progress.update(m))
                progress.update(f"[2/2] Copying {file_to_backup.name} ...")
                entry = do_backup(self.game, file_to_backup, on_progress=update_progress)
                self.after(0, lambda: (
                    progress.close(),
                    self.refresh(),
                    self._set_buttons_enabled(True),
                    alert(self, "Backup Complete", f"Saved: {entry.name} ({format_size(entry.size_bytes)})")
                ))
            except PermissionError as exc:
                err_msg = f"Permission denied: {exc}\n\nMake sure the file is not in use by another program."
                self.after(0, lambda err_msg=err_msg: (
                    progress.close(),
                    self._set_buttons_enabled(True),
                    alert(self, "Backup Failed", err_msg)
                ))
            except Exception as exc:
                err_msg = str(exc)
                self.after(0, lambda err_msg=err_msg: (
                    progress.close(),
                    self._set_buttons_enabled(True),
                    alert(self, "Backup Failed", err_msg)
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

    SELECTED_COLOR = "#3B8ED0"  # CTk blue when selected
    HOVER_COLOR = ("#3B8ED0", "#1f5a8a")  # Same blue as button hover
    NORMAL_TEXT_COLOR = "#ffffff"  # White text like games
    SIZE_TEXT_COLOR = "#3B8ED0"  # CTk blue for size
    
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

        # Full-width clickable area with border like games
        self.hitbox = ctk.CTkFrame(
            self,
            fg_color="transparent",
            cursor="hand2",
            corner_radius=8,
            border_width=1,
            border_color=("gray50", "gray30"),
            width=300,
            height=40
        )
        self.hitbox.pack(fill="x", padx=2, pady=2)
        self.hitbox.pack_propagate(False)
        self.hitbox.bind("<Button-1>", lambda e: self._on_click())
        self.hitbox.bind("<Enter>", lambda e: self._on_hover(True))
        self.hitbox.bind("<Leave>", lambda e: self._on_hover(False))

        content = ctk.CTkFrame(self.hitbox, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)

        # White text like games list
        self.name_label = ctk.CTkLabel(
            content,
            text=backup.name,
            anchor="w",
            font=ctk.CTkFont(size=11, weight="bold"),
            cursor="hand2",
            text_color=self.NORMAL_TEXT_COLOR
        )
        self.name_label.pack(side="left", padx=5)
        self.name_label.bind("<Button-1>", lambda e: self._on_click())
        self.name_label.bind("<Enter>", lambda e: self._on_hover(True))
        self.name_label.bind("<Leave>", lambda e: self._on_hover(False))

        date_str = backup.created_at.strftime("%Y-%m-%d %H:%M")
        size_str = format_size(backup.size_bytes)
        
        # Blue like other UI elements
        self.size_label = ctk.CTkLabel(
            content,
            text=f"{size_str} | {date_str}",
            anchor="e",
            text_color=self.SIZE_TEXT_COLOR,
            font=ctk.CTkFont(size=10, weight="bold"),
            cursor="hand2"
        )
        self.size_label.pack(side="right", padx=5)
        self.size_label.bind("<Button-1>", lambda e: self._on_click())
        self.size_label.bind("<Enter>", lambda e: self._on_hover(True))
        self.size_label.bind("<Leave>", lambda e: self._on_hover(False))

    def _on_click(self):
        """Handle click on the backup item."""
        self.on_select(self.backup)

    def _on_hover(self, entering: bool):
        """Hover effect - clean blue fill, not gradient."""
        if not self.is_selected and entering:
            self.hitbox.configure(fg_color="#3B8ED0")
        elif not self.is_selected:
            self.hitbox.configure(fg_color="transparent")

    def set_selected(self, selected: bool):
        self.is_selected = selected
        if selected:
            self.hitbox.configure(fg_color=self.SELECTED_COLOR)
        else:
            self.hitbox.configure(fg_color="transparent")

