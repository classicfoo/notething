import tkinter as tk
from tkinter import ttk  # Import ttk
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

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Notething")

        # Center the window on the screen
        window_width = 800
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # --- Scrollbar and Text Area Setup ---
        # Create a frame to hold the text area and scrollbar
        text_frame = ttk.Frame(self.root)
        text_frame.pack(expand=True, fill='both', side=tk.TOP) # Pack frame first

        # Create the scrollbar (ttk)
        self.scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the text area (tk)
        self.font = tkFont.Font(family="Consolas", size=11)
        self.text_area = tk.Text(
            text_frame, # Place text area in the frame
            wrap='word',
            font=self.font,
            padx=10,
            pady=10,
            yscrollcommand=self.scrollbar.set # Link text area scroll to scrollbar
        )
        self.text_area.pack(expand=True, fill='both', side=tk.LEFT) # Pack text area after scrollbar

        # Configure scrollbar to control text area
        self.scrollbar.config(command=self.text_area.yview)
        # --- End Scrollbar Setup ---


        # Use ttk.Label for the status bar
        self.status_bar = ttk.Label(self.root, text="Status: Ready", anchor='w', padding=(5, 5))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X) # Pack status bar last

        self.current_file = None

        # Create a tooltip for the status bar
        self.tooltip = Tooltip(self.status_bar)
        self.tooltip.set_text(self.status_bar.cget("text"))

        self.create_menu()
        self.bind_hotkeys()

        # Bind Ctrl + Backspace to delete the previous word
        self.text_area.bind("<Control-BackSpace>", self.delete_previous_word)

    def create_menu(self):
        # tk.Menu is standard, ttk doesn't replace it
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

    def delete_previous_word(self, event):
        # Get the current cursor position
        cursor_index = self.text_area.index(tk.INSERT)
        # Get the text from the start to the cursor position
        text = self.text_area.get("1.0", cursor_index)

        # Find the last space before cursor
        last_space_index = text.rfind(" ")

        if last_space_index == -1:
            # If no space found, delete everything up to cursor
            self.text_area.delete("1.0", cursor_index)
        else:
            # Delete from after the last space up to cursor
            # If the last character is a space, delete until beginning of previous word
            if text and text[-1] == " ": # Check if text is not empty
                # Find the second to last space
                second_last_space = text.rstrip().rfind(" ") # Find space before the word
                if second_last_space != -1:
                    delete_start = f"1.0+{second_last_space + 1}c" # Start after the space before the word
                else:
                    delete_start = "1.0" # Delete from the beginning if it's the first word
            else:
                # If cursor is after a word, delete from the space before it
                 delete_start = f"1.0+{last_space_index + 1}c" # Start after the last space

            self.text_area.delete(delete_start, cursor_index)
        return "break" # Prevent default Backspace behavior

    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None  # Reset current file
        status_text = "Status: New file created"
        self.status_bar.config(text=status_text)
        self.tooltip.set_text(status_text)

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"),
                                                           ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file: # Added encoding
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, file.read())
                    self.current_file = file_path  # Set current file
                    status_text = f"Status: Opened {file_path}"
                    self.status_bar.config(text=status_text)
                    self.tooltip.set_text(status_text)
            except Exception as e:
                messagebox.showerror("Error Opening File", f"Could not open file:\n{e}")

    def save_file(self):
        if self.current_file:  # If a file is already opened
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file: # Added encoding
                    file.write(self.text_area.get(1.0, tk.END).rstrip('\n') + '\n') # Ensure single newline at end
                    # Get the current date and time in 12-hour format
                    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    status_text = f"Status: Saved to {self.current_file} at {timestamp}"
                    self.status_bar.config(text=status_text)
                    self.tooltip.set_text(status_text)
            except Exception as e:
                 messagebox.showerror("Error Saving File", f"Could not save file:\n{e}")

        else:  # If no file is opened, prompt to save as
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                       filetypes=[("Text files", "*.txt"),
                                                                  ("All files", "*.*")])
            if file_path:  # Check if the user didn't cancel
                try:
                    with open(file_path, 'w', encoding='utf-8') as file: # Added encoding
                        file.write(self.text_area.get(1.0, tk.END).rstrip('\n') + '\n') # Ensure single newline at end
                        self.current_file = file_path # Update current file path
                        # Get the current date and time in 12-hour format
                        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        status_text = f"Status: Saved to {self.current_file} at {timestamp}"
                        self.status_bar.config(text=status_text)
                        self.tooltip.set_text(status_text)
                except Exception as e:
                    messagebox.showerror("Error Saving File", f"Could not save file:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    # Optional: Apply a theme if desired (e.g., 'clam', 'alt', 'default', 'classic')
    # style = ttk.Style(root)
    # style.theme_use("vista") # Example theme: vista often looks good on Windows
    notepad = Notepad(root)
    root.mainloop()