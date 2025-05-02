import tkinter as tk
from tkinter import ttk  # Import ttk
from tkinter import filedialog, messagebox
from datetime import datetime  # Import datetime module
import tkinter.font as tkFont  # Import tkinter font module
import argparse # <-- Import argparse
from tkinterdnd2 import DND_FILES, TkinterDnD # <-- Import TkinterDnD2
import os # <-- Import os module

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
    def __init__(self, root, initial_file=None):
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
            undo=True,  # <-- Enable undo/redo stack
            maxundo=0,  # <-- 0 means unlimited undo levels
            autoseparators=True,  # <-- Automatically separate undo operations
            yscrollcommand=self.scrollbar.set, # Link text area scroll to scrollbar
            selectbackground="lightgrey", # <-- Set selection background color
            selectforeground="black"      # <-- Set selection foreground color
        )
        self.text_area.pack(expand=True, fill='both', side=tk.LEFT) # Pack text area after scrollbar

        # --- Configure Line Color Tags ---
        self.text_area.tag_configure("green_line", foreground="green")
        self.text_area.tag_configure("blue_line", foreground="blue")
        self.text_area.tag_configure("grey_line", foreground="grey") # <-- Add grey tag
        self.text_area.tag_configure("normal_line", foreground="black") # Explicitly define black
        # --- End Tag Configuration ---

        # --- Drag and Drop Setup ---
        self.text_area.drop_target_register(DND_FILES)
        self.text_area.dnd_bind('<<Drop>>', self.handle_drop) # Use generic <<Drop>>
        # --- End Drag and Drop Setup ---

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

        # --- Bind KeyRelease for Line Coloring ---
        self.text_area.bind("<KeyRelease>", self._update_line_colors_event) # Use _event suffix for direct bindings
        # --- End KeyRelease Binding ---

        # Load initial file if provided
        if initial_file:
            self._load_file(initial_file)
        else:
            # Ensure initial coloring is applied even for an empty new file
            self._update_line_colors()

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
        self.root.title("Notething") # <-- Reset the window title
        status_text = "Status: Untitled" # <-- Updated status message
        self.status_bar.config(text=status_text)
        self.tooltip.set_text(status_text)
        self._update_line_colors() # Update colors for the empty area

    def _load_file(self, file_path):
        """Loads the content of the specified file into the text area."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
                self.current_file = file_path
                # Update title to include filename only
                filename = os.path.basename(file_path) # <-- Get filename
                self.root.title(f"Notething - {filename}") # <-- Use filename in title
                status_text = f"Status: Opened {file_path}"
                self.status_bar.config(text=status_text)
                self.tooltip.set_text(status_text)
                self._update_line_colors() # <-- Add call here
        except FileNotFoundError:
             messagebox.showerror("Error Opening File", f"File not found:\n{file_path}")
             self.new_file() # Reset to a new file state if initial file not found
             self.root.title("Notething") # Reset title
        except Exception as e:
            messagebox.showerror("Error Opening File", f"Could not open file:\n{e}")
            self.new_file() # Reset on other errors too
            self.root.title("Notething") # Reset title

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"),
                                                           ("All files", "*.*")])
        if file_path:
            self._load_file(file_path)

    def save_file(self):
        if self.current_file:  # If a file is already opened
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file: # Added encoding
                    file.write(self.text_area.get(1.0, tk.END).rstrip('\n') + '\n') # Ensure single newline at end
                    # Get the current date and time in 12-hour format with seconds
                    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p") # <-- Added :%S
                    status_text = f"Status: Saved to {self.current_file} at {timestamp}"
                    self.status_bar.config(text=status_text)
                    self.tooltip.set_text(status_text)
                    # Update title after saving with filename only
                    filename = os.path.basename(self.current_file) # <-- Get filename
                    self.root.title(f"Notething - {filename}") # <-- Use filename in title
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
                        # Get the current date and time in 12-hour format with seconds
                        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p") # <-- Added :%S
                        status_text = f"Status: Saved to {self.current_file} at {timestamp}"
                        self.status_bar.config(text=status_text)
                        self.tooltip.set_text(status_text)
                        # Update title after saving with filename only
                        filename = os.path.basename(self.current_file) # <-- Get filename
                        self.root.title(f"Notething - {filename}") # <-- Use filename in title
                except Exception as e:
                    messagebox.showerror("Error Saving File", f"Could not save file:\n{e}")

    def handle_drop(self, event):
        """Handles files dropped onto the text area, supporting spaces in filenames."""
        # event.data contains a string with file path(s)
        # Paths with spaces are often enclosed in curly braces {}
        file_path_str = event.data.strip() # Remove leading/trailing whitespace

        print(f"Raw dropped data: '{file_path_str}'") # Debug print

        file_path = None

        # Check if the path is enclosed in curly braces
        if file_path_str.startswith('{') and file_path_str.endswith('}'):
            # Extract the path from within the braces
            # This assumes only ONE file path is dropped within braces.
            # Handling multiple braced paths like '{path one} {path two}' would need more complex parsing.
            file_path = file_path_str[1:-1]
        else:
            # If no braces, assume it's a single path without spaces,
            # or the OS/drag source didn't add braces.
            # We still only handle the first potential path if multiple are somehow passed without braces.
            # A simple split might still be wrong here if un-braced paths have spaces,
            # but it's the best guess without more complex parsing.
            # For robustness, we'll just take the whole string if no braces.
            file_path = file_path_str

        # Ensure we actually got a path
        if file_path:
            # Further check: Sometimes TkinterDnD might return paths with extra quotes
            file_path = file_path.strip('"')

            print(f"Parsed file path: '{file_path}'") # Debug print
            # Check if the path seems valid (basic check)
            if file_path: # Ensure it's not empty after stripping
                 # Consider adding os.path.exists(file_path) if needed,
                 # but _load_file already handles FileNotFoundError
                self._load_file(file_path)
            else:
                print(f"Could not extract a valid path from dropped data: {event.data}")
        else:
            print(f"Could not parse dropped data: {event.data}")

    # --- Add the new method to update line colors ---
    def _update_line_colors(self):
        """Applies color tags based on line content."""
        # Remove existing tags first to reset colors
        self.text_area.tag_remove("green_line", "1.0", tk.END)
        self.text_area.tag_remove("blue_line", "1.0", tk.END)
        self.text_area.tag_remove("grey_line", "1.0", tk.END)
        self.text_area.tag_remove("normal_line", "1.0", tk.END)

        # Iterate through each line
        # Get the index of the last character + 1 line (the line count)
        last_line_str = self.text_area.index(f"{tk.END}-1c").split('.')[0]
        # Handle empty text area case
        if not last_line_str:
             return
        last_line = int(last_line_str)


        for i in range(1, last_line + 1):
            line_start = f"{i}.0"
            line_end = f"{i}.end"
            line_content = self.text_area.get(line_start, line_end)
            stripped_line = line_content.lstrip() # Strip whitespace once

            # Check conditions after stripping leading whitespace
            # Combine X and C for the grey tag
            if stripped_line.startswith("X ") or stripped_line.startswith("C "):
                self.text_area.tag_add("grey_line", line_start, line_end) # Apply GREY tag
            elif stripped_line.startswith("N "): # Check for N second
                self.text_area.tag_add("green_line", line_start, line_end) # Apply GREEN tag
            elif stripped_line.startswith("T "): # Check for T third
                self.text_area.tag_add("blue_line", line_start, line_end) # Apply BLUE tag
            else:
                # Apply normal color tag if none of the conditions are met
                self.text_area.tag_add("normal_line", line_start, line_end)

    def _update_line_colors_event(self, event=None):
        """Callback for KeyRelease event to update line colors."""
        # Optional: Add checks here if needed (e.g., ignore certain keys)
        self._update_line_colors()
    # --- End new method ---

if __name__ == "__main__":
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Notething - A simple Tkinter notepad.")
    parser.add_argument('filepath', nargs='?', default=None, # Optional positional argument
                        help='Optional path to a text file to open.')
    args = parser.parse_args()
    # --- End Argument Parsing ---

    root = TkinterDnD.Tk()
    # Optional: Apply a theme if desired (e.g., 'clam', 'alt', 'default', 'classic')
    style = ttk.Style(root)
    try:
        # Try a theme that might look better on the specific OS
        if root.tk.call('tk', 'windowingsystem') == 'win32':
            style.theme_use('vista') # Or 'xpnative'
        elif root.tk.call('tk', 'windowingsystem') == 'aqua':
            style.theme_use('aqua') # macOS
        else:
            style.theme_use('clam') # A reasonable default for Linux/others
    except tk.TclError:
        style.theme_use("default") # Fallback

    # Pass the filepath from arguments to the Notepad constructor
    notepad = Notepad(root, initial_file=args.filepath)
    root.mainloop()