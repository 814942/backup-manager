"""Reusable dialog windows for the backup manager."""
import customtkinter as ctk
from typing import Callable, Optional


class ConfirmDialog(ctk.CTkToplevel):
    """Confirmation dialog with Yes/No buttons."""

    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)
        self.result: bool = False
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)

        # Center the dialog
        self.transient(parent)
        self.grab_set()

        # Message
        ctk.CTkLabel(
            self,
            text=message,
            wraplength=350
        ).pack(pady=20)

        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Yes",
            command=self.on_yes,
            width=80
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="No",
            command=self.on_no,
            width=80
        ).pack(side="left", padx=5)

    def on_yes(self):
        self.result = True
        self.destroy()

    def on_no(self):
        self.result = False
        self.destroy()


class ProgressDialog(ctk.CTkToplevel):
    """Progress dialog showing status message with indeterminate progress bar."""

    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x120")
        self.resizable(False, False)

        # Center the dialog
        self.transient(parent)
        self.grab_set()

        self.label = ctk.CTkLabel(self, text="Working...")
        self.label.pack(pady=20)

        self.progress = ctk.CTkProgressBar(
            self,
            orientation="horizontal",
            mode="indeterminate"
        )
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.start()

    def update(self, message: str):
        """Update the progress message."""
        self.label.configure(text=message)
        self.update_idletasks()

    def close(self):
        """Close the progress dialog."""
        self.progress.stop()
        self.destroy()


class AlertDialog(ctk.CTkToplevel):
    """Simple alert dialog with OK button."""

    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)

        # Center the dialog
        self.transient(parent)
        self.grab_set()

        # Message
        ctk.CTkLabel(
            self,
            text=message,
            wraplength=350
        ).pack(pady=20)

        # Button
        ctk.CTkButton(
            self,
            text="OK",
            command=self.destroy,
            width=80
        ).pack(pady=10)


def confirm(
    parent,
    title: str,
    message: str,
    on_result: Optional[Callable[[bool], None]] = None
) -> bool:
    """Show a confirmation dialog and return the result synchronously."""
    dialog = ConfirmDialog(parent, title, message)
    parent.wait_window(dialog)
    if on_result:
        on_result(dialog.result)
    return dialog.result


def show_progress(
    parent,
    title: str,
    on_close: Optional[Callable[[], None]] = None
) -> ProgressDialog:
    """Show a progress dialog and return the dialog object."""
    dialog = ProgressDialog(parent, title)
    return dialog


def alert(parent, title: str, message: str):
    """Show an alert dialog."""
    AlertDialog(parent, title, message)