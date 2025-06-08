import tkinter as tk
from tkinter import ttk

class Tooltip:
    """Create a tooltip for a given widget."""
    def __init__(self, widget):
        self.widget = widget
        self.tooltip_window = None
        self.text = ""

        # Bind mouse events
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window is not None:
            return  # Tooltip is already shown

        # Create a new tooltip window (tk.Toplevel is fine)
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Use ttk.Label for the tooltip text
        label = ttk.Label(self.tooltip_window, text=self.text, background="#F5F5DC", padding=(5, 2)) # Use padding instead of borderwidth/relief
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window is not None:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def set_text(self, text):
        self.text = text