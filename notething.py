import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime  # Import datetime module
import tkinter.font as tkFont  # Import tkinter font module

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

        # Create a new tooltip window
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, background="#F5F5DC", relief="solid", borderwidth=1)  # Cream color
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window is not None:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def set_text(self, text):
        self.text = text

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Notething")

        # Center the window on the screen
        window_width = 600
        window_height = 450  # Increased height for the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Set a monospace font for the text area
        self.font = tkFont.Font(family="Consolas", size=11)  # You can change the font family and size here
        self.text_area = tk.Text(self.root, wrap='word', font=self.font, padx=10, pady=10)
        self.text_area.pack(expand=True, fill='both')

        # Add padding to the status bar
        self.status_bar = tk.Label(self.root, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor='w', padx=5, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.current_file = None  # Track the current file path

        # Create a tooltip for the status bar
        self.tooltip = Tooltip(self.status_bar)
        self.tooltip.set_text(self.status_bar.cget("text"))

        self.create_menu()
        self.bind_hotkeys()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator='Ctrl+N')
        file_menu.add_command(label="Open", command=self.open_file, accelerator='Ctrl+O')
        file_menu.add_command(label="Save", command=self.save_file, accelerator='Ctrl+S')
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def bind_hotkeys(self):
        self.root.bind('<Control-n>', lambda event: self.new_file())
        self.root.bind('<Control-o>', lambda event: self.open_file())
        self.root.bind('<Control-s>', lambda event: self.save_file())

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None  # Reset current file
        self.status_bar.config(text="Status: New file created")
        self.tooltip.set_text(self.status_bar.cget("text"))

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"),
                                                           ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
                self.current_file = file_path  # Set current file
                self.status_bar.config(text=f"Status: Opened {file_path}")
                self.tooltip.set_text(self.status_bar.cget("text"))

    def save_file(self):
        if self.current_file:  # If a file is already opened
            with open(self.current_file, 'w') as file:
                file.write(self.text_area.get(1.0, tk.END))
                # Get the current date and time in 12-hour format
                timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")  # 12-hour format with AM/PM
                self.status_bar.config(text=f"Status: Saved to {self.current_file} at {timestamp}")
                self.tooltip.set_text(self.status_bar.cget("text"))
        else:  # If no file is opened, prompt to save as
            self.current_file = filedialog.asksaveasfilename(defaultextension=".txt",
                                                               filetypes=[("Text files", "*.txt"),
                                                                          ("All files", "*.*")])
            if self.current_file:  # Check if the user didn't cancel
                with open(self.current_file, 'w') as file:
                    file.write(self.text_area.get(1.0, tk.END))
                    # Get the current date and time in 12-hour format
                    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")  # 12-hour format with AM/PM
                    self.status_bar.config(text=f"Status: Saved to {self.current_file} at {timestamp}")
                    self.tooltip.set_text(self.status_bar.cget("text"))

if __name__ == "__main__":
    root = tk.Tk()
    notepad = Notepad(root)
    root.mainloop()