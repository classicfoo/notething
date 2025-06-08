import tkinter as tk
from tkinter import ttk  # Import ttk
from tkinter import filedialog, messagebox, simpledialog # <-- Import simpledialog
from datetime import datetime  # Import datetime module
import tkinter.font as tkFont  # Import tkinter font module
import argparse # <-- Import argparse
from tkinterdnd2 import DND_FILES, TkinterDnD # <-- Import TkinterDnD2
import os # <-- Import os module
import pytz # <-- Import pytz for timezone handling
import tkinter.simpledialog # Already imported, but ensure it's there
import calendar # <-- Import calendar for month names
from tkcalendar import Calendar # <-- Import the Calendar widget
import time # <-- Import time module
import re
import webbrowser # <-- Import webbrowser for opening URLs
import subprocess # <-- Import subprocess for opening files
from utils.highlighting import HighlightingManager
from ui.mixins import CenterDialogMixin
from ui.calendar_dialog import CalendarDialog
from ui.find_replace_dialog import FindReplaceDialog
from ui.tooltip import Tooltip
from ui.settings_dialog import SettingsDialog
from utils.line_formatting import LineFormatter

class Notepad:
    # --- Class variables for window management and cascading ---
    open_window_count = 0
    cascade_offset = 30  # Pixels to offset each new window
    first_window_x = None
    first_window_y = None
    default_window_width = 800
    default_window_height = 500
    # ---

    # Add this as a class variable
    recent_files = []
    MAX_RECENT_FILES = 5
    reopen_last_file = True 

    # Add this with other class variables at the start of Notepad class
    last_match_case_setting = False  # Default to case-insensitive search

    # Change the variable name to be more accurate
    line_formatting_enabled = True  # Default to enabled

    # Add a class variable to track if first window has been initialized
    first_window_initialized = False

    # Add this with other class variables at the start of Notepad class
    auto_capitalize_headings = True  # Default to enabled

    # Add this with other class variables at the start of Notepad class
    auto_capitalize_first_word = True  # Default to enabled

    # Add this with other class variables at the start of Notepad class
    auto_capitalize_indented = False  # Default to disabled

    # Add after other class variables in Notepad class
    highlight_enabled = True  # Default to enabled

    # In Notepad class, add after other class variables
    auto_full_stop = True  # Default to disabled

    # In Notepad class, add after other class variables
    default_find_text = ""
    default_replace_text = ""
    readonly_mode = False  # New setting for readonly mode

    def __init__(self, root, initial_file=None):
        """Initialize the notepad."""
        self.root = root
        self.root.title("Notething")
        self.current_file = None
        self.readonly_var = tk.BooleanVar(value=False)  # Initialize readonly variable
        
        Notepad.open_window_count += 1

        # --- Window Positioning and Sizing ---
        window_width = Notepad.default_window_width
        window_height = Notepad.default_window_height

        if Notepad.first_window_x is None or Notepad.open_window_count == 1: # First window logic
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            Notepad.first_window_x = (screen_width // 2) - (window_width // 2)
            Notepad.first_window_y = (screen_height // 2) - (window_height // 2)
            current_x = Notepad.first_window_x
            current_y = Notepad.first_window_y
            # Reset count if this is the first window after all others might have been closed
            if Notepad.open_window_count > 1: # Should only happen if manually reset elsewhere
                 Notepad.open_window_count = 1
        else:
            # Cascade subsequent windows
            offset_multiplier = (Notepad.open_window_count - 1)
            current_x = Notepad.first_window_x + offset_multiplier * Notepad.cascade_offset
            current_y = Notepad.first_window_y + offset_multiplier * Notepad.cascade_offset

            # Optional: Keep window on screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            if current_x + window_width > screen_width:
                current_x = screen_width - window_width
            if current_y + window_height > screen_height:
                current_y = screen_height - window_height
            current_x = max(0, current_x)
            current_y = max(0, current_y)

        self.root.geometry(f"{window_width}x{window_height}+{current_x}+{current_y}")
        # --- End Window Positioning ---

        # --- Scrollbar and Text Area Setup ---
        # Create a frame to hold the text area and scrollbar
        text_frame = ttk.Frame(self.root)
        text_frame.pack(expand=True, fill='both', side=tk.TOP) # Pack frame first

        # Create the scrollbar
        self.scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)

        # Create the text area with custom font
        self.font = tkFont.Font(root=self.root, family="Consolas", size=11)
        self.bold_font = tkFont.Font(root=self.root, family="Consolas", size=11, weight="bold")
        self.text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=self.font,
            padx=10,
            pady=10,
            undo=True,
            maxundo=-1,
            autoseparators=True,
            exportselection=False,
            yscrollcommand=self.scrollbar.set,
            selectbackground="lightgrey",
            selectforeground="black",
            cursor="arrow"  # Change cursor to arrow by default
        )

        
        # Replace the highlight-related code with:
        self.highlight_manager = HighlightingManager(self.text_area)

        
        self.line_formatter = LineFormatter(self.text_area, self)
        self.line_formatter._update_line_formatting()

        # Configure scrollbar to control text area
        self.scrollbar.config(command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(expand=True, fill='both', side=tk.LEFT)

        # Add URL detection and hyperlink functionality
        self.text_area.tag_configure("hyperlink", foreground="blue", underline=1)
        self.text_area.tag_bind("hyperlink", "<Enter>", lambda e: self.text_area.config(cursor="hand2"))
        self.text_area.tag_bind("hyperlink", "<Leave>", lambda e: self.text_area.config(cursor="arrow"))
        self.text_area.bind("<Button-1>", self._handle_click)

        # Bind the combined handler to all relevant events
        self.text_area.bind("<KeyRelease>", self.line_formatter._update_line_formatting_event)
        self.text_area.bind("<<Paste>>", lambda e: self.root.after(1, self.line_formatter._update_line_formatting()))
        self.text_area.bind("<Control-v>", lambda e: self.root.after(1, self.line_formatter._update_line_formatting()))
        self.text_area.bind("<FocusOut>", lambda e: self.line_formatter._update_line_formatting())
        self.text_area.bind("<space>", lambda e: self.line_formatter._update_line_formatting())
        self.text_area.bind("<Return>", lambda e: self.line_formatter._update_line_formatting())
        

        # Remove any old separate bindings for _detect_urls and _update_line_formatting_event
        # (Assume they are not rebound elsewhere)


        # --- Configure Line Color Tags ---
        self.text_area.tag_configure("green_line", foreground="green")
        self.text_area.tag_configure("blue_line", foreground="blue")
        self.text_area.tag_configure("grey_line", foreground="grey")
        self.text_area.tag_configure("normal_line", foreground="black") # Default
        self.text_area.tag_configure("maroon_line", foreground="maroon") # New maroon tag
        self.text_area.tag_configure("bold_line", font=self.bold_font)   # New bold tag
        # --- Add Custom Search Highlight Tag ---
        self.text_area.tag_configure("search_highlight", background="darkorange", foreground="white")
        # --- End Tag Configuration ---

        # --- Drag and Drop Setup ---
        self.text_area.drop_target_register(DND_FILES)
        self.text_area.dnd_bind('<<Drop>>', self.handle_drop) # Use generic <<Drop>>
        # --- End Drag and Drop Setup ---

        # Use ttk.Label for the status bar
        self.status_bar = ttk.Label(self.root, text="Status: Ready", anchor='w', padding=(5, 5))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X) # Pack status bar last

        # Create a tooltip for the status bar
        self.tooltip = Tooltip(self.status_bar)
        self.tooltip.set_text(self.status_bar.cget("text"))

        # --- Find/Replace State ---
        self.find_dialog = None
        self.last_find_text = ""
        self.last_replace_text = ""
        self.last_match_case = False
        # --- End Find/Replace State ---

        self.highlight_manager = HighlightingManager(self.text_area)

        self.create_menu()
        self._setup_key_bindings()
        self.bind_hotkeys()

        # Bind Ctrl + Backspace to delete the previous word
        self.text_area.bind("<Control-BackSpace>", self.delete_previous_word)

        # --- Bind KeyRelease for Line Coloring ---
        self.text_area.bind("<KeyRelease>", self.line_formatter._update_line_formatting_event) # Use _event suffix for direct bindings
        # --- End KeyRelease Binding ---

        # --- Bind Tab and Shift-Tab for Indentation ---
        self.text_area.bind("<Tab>", self._handle_tab_key)
        self.text_area.bind("<Shift-Tab>", self._handle_shift_tab_key)
        # --- End Indentation Bindings ---

        # --- Bind Enter for Auto-Indentation ---
        self.text_area.bind("<Return>", self._handle_enter_key)
        # --- End Enter Binding ---

        # --- Bind Home for Smart Home ---
        self.text_area.bind("<Home>", self._handle_home_key)
        self.text_area.bind("<Shift-Home>", self._handle_home_key)  # Add explicit Shift-Home binding
        # --- End Home Binding ---

        # Set up our keyboard shortcuts/bindings
        self._setup_key_bindings()

        # Load settings and recent files
        self._load_settings()

        # Handle initial file loading based on whether this is the first window
        if not Notepad.first_window_initialized:
            # This is the first window
            Notepad.first_window_initialized = True
            if initial_file:
                self._load_file(initial_file)
            elif Notepad.reopen_last_file and Notepad.recent_files:
                # Reopen the most recently used file
                self._load_file(Notepad.recent_files[0])
            else:
                # Ensure initial coloring is applied even for an empty new file
                self.line_formatter._update_line_formatting()
                self.root.title("Notething - Untitled")
        else:
            # This is a subsequent window - always start blank
            self.line_formatter._update_line_formatting()
            self.root.title("Notething - Untitled")

        # Bind the window close button (X)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_window)

        
        



    def create_menu(self):
        """Create the application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.open_new_window, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        # Add submenu for recent files immediately after Open...
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Open Recent", menu=self.recent_menu)
        self._update_recent_menu()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_command(label="Rename...", command=self.rename_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.text_area.edit_undo(), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.text_area.edit_redo(), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"), accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"), accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"), accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.open_find_dialog, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self.open_replace_dialog, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_checkbutton(label="Read-only", command=self.toggle_readonly, variable=self.readonly_var)
        # Add Settings at the bottom of Edit menu
        edit_menu.add_separator()
        edit_menu.add_command(label="Settings...", command=self.open_settings_dialog)

    def bind_hotkeys(self):
        """Bind keyboard shortcuts."""
        # File menu
        self.root.bind("<Control-n>", lambda e: self.open_new_window())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        
        # Edit menu
        self.root.bind("<Control-f>", lambda e: self.open_find_dialog())
        
        self.text_area.bind("<Control-Shift-H>", self.highlight_manager.handle_highlight)

                
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
        self.current_file = None
        self._update_title()
        self.status_bar.config(text="Status: New file")
        self.tooltip.set_text("Status: New file")
        # Apply line formatting/colors
        self.line_formatter._update_line_formatting()

    def _load_file(self, filepath):
        """Load a file into the text area."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, file.read())
            self.current_file = filepath
            self.root.title(f"Notething - {os.path.basename(filepath)}")
            
            # Check if file is readonly and update the readonly toggle
            is_readonly = not os.access(filepath, os.W_OK)
            self.readonly_var.set(is_readonly)
            
            # Update window title to show readonly status
            self._update_title()
            
            # Update status bar
            timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            status_text = f"Status: Opened {filepath} at {timestamp}"
            self.status_bar.config(text=status_text)
            self.tooltip.set_text(status_text)
            # Apply line formatting/colors
            self.line_formatter._update_line_formatting()
        except Exception as e:
            messagebox.showerror("Error Opening File", f"Could not open file:\n{e}")

    def _update_title(self):
        """Update the window title to show readonly status."""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            readonly_status = " [Read-only]" if self.readonly_var.get() else ""
            self.root.title(f"Notething - {filename}{readonly_status}")
        else:
            self.root.title("Notething")

    def _get_suggested_filename(self):
        """Get a suggested filename based on the first H1 markdown heading."""
        try:
            # Get all text content
            content = self.text_area.get("1.0", tk.END)
            
            # Look for # heading pattern at the start of any line
            import re
            h1_pattern = r'(?m)^#\s+(.+)$'  # Matches '# Heading' at start of any line
            match = re.search(h1_pattern, content)
            
            if match:
                # Get the heading text
                heading = match.group(1).strip()
                
                # Convert to lowercase
                heading = heading.lower()
                
                # Replace invalid filename characters and spaces with underscores
                # First replace spaces with underscores
                heading = heading.replace(' ', '_')
                
                # Replace other invalid characters
                invalid_chars = r'[<>:"/\\|?*]'
                heading = re.sub(invalid_chars, '_', heading)
                
                # Replace multiple underscores with single underscore
                heading = re.sub(r'_+', '_', heading)
                
                # Remove leading/trailing underscores
                heading = heading.strip('_')
                
                # If empty after cleaning, return None
                if not heading:
                    return None
                    
                return heading
        except Exception:
            return None
        
        return None

    def open_file(self):
        """Open a file for editing"""
        # Show the file dialog with "All Files" as the default option
        # Make dialog modal to the main window and ensure it stays on top
        filepath = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All Files", "*.*"),  # This is now first, so it's the default
                ("Text Files", "*.txt"),
                ("Python Files", "*.py;*.pyw"),
                ("Markdown Files", "*.md"),
                ("HTML Files", "*.html;*.htm")
            ],
            parent=self.root  # Make dialog modal to main window
        )
        
        if filepath:  # If a file was selected (not canceled)
            self._load_file(filepath)
            # Ensure main window gets focus back
            self.root.focus_force()
            self.text_area.focus_set()
            self.line_formatter._update_line_formatting()
            self._add_to_recent_files(filepath)
            self._detect_urls()  # Ensure hyperlinks are detected after loading

    def toggle_readonly(self):
        """Toggle the readonly status of the current file."""
        if not self.current_file:
            messagebox.showwarning("Read-only Toggle", "Please save the file first.")
            self.readonly_var.set(False)
            return

        try:
            if self.readonly_var.get():
                # Make file readonly
                os.chmod(self.current_file, 0o444)  # Read-only for all users
            else:
                # Make file writable
                os.chmod(self.current_file, 0o666)  # Read-write for all users
            
            # Update window title
            self._update_title()
            
            # Update status bar
            status = "read-only" if self.readonly_var.get() else "writable"
            status_text = f"Status: File is now {status}"
            self.status_bar.config(text=status_text)
            self.tooltip.set_text(status_text)
            
        except Exception as e:
            messagebox.showerror("Permission Error", f"Could not change file permissions:\n{e}")
            # Revert the checkbox state
            self.readonly_var.set(not self.readonly_var.get())

    def save_file(self):
        if self.current_file:  # If a file is already opened
            try:
                # Check if file is readonly
                if self.readonly_var.get():
                    self.save_as()
                    return
                
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0, tk.END).rstrip('\n') + '\n')
                    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                    status_text = f"Status: Saved to {self.current_file} at {timestamp}"
                    self.status_bar.config(text=status_text)
                    self.tooltip.set_text(status_text)
                    self._update_title()
            except Exception as e:
                messagebox.showerror("Error Saving File", f"Could not save file:\n{e}")
        else:  # If no file is opened, prompt to save as
            self.save_as()

    def save_as(self):
        # Get suggested filename
        suggested_name = self._get_suggested_filename()
        initial_file = f"{suggested_name}.txt" if suggested_name else None
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ],
            initialfile=initial_file,
            parent=self.root
        )
        
        if file_path:
            self.current_file = file_path
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0, tk.END).rstrip('\n') + '\n')
                # Set file to writable after Save As
                import os
                os.chmod(self.current_file, 0o666)
                self.readonly_var.set(False)
                self._update_title()
                timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                status_text = f"Status: Saved to {self.current_file} at {timestamp}"
                self.status_bar.config(text=status_text)
                self.tooltip.set_text(status_text)
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
    def _capitalize_heading_words(self, text):
        """Capitalize the first letter of each word in a heading."""
        # Split into words, keeping spaces intact
        words = text.split(' ')
        capitalized_words = []
        
        for word in words:
            if word:  # Only process non-empty strings
                # Capitalize first letter, lowercase the rest
                capitalized_words.append(word[0].upper() + word[1:].lower())
            else:
                # Preserve empty strings (spaces)
                capitalized_words.append(word)
        
        return ' '.join(capitalized_words)

    def _format_heading_line(self, line):
        """Format a heading line with proper capitalization."""
        # Count leading '#' characters
        heading_level = 0
        for char in line:
            if char == '#':
                heading_level += 1
            else:
                break
            
        # Check if it's a valid heading (# followed by space)
        if heading_level > 0 and heading_level <= 3 and len(line) > heading_level:
            if line[heading_level] == ' ':
                # Split into prefix and content
                prefix = line[:heading_level + 1]  # Include the space
                content = line[heading_level + 1:]  # Get text after '# '
                
                # Capitalize the content
                capitalized_content = self._capitalize_heading_words(content)
                
                # Return the formatted line
                return prefix + capitalized_content
                
        return line
    

    def rename_file(self):
        """Renames the currently open file."""
        if not self.current_file:
            messagebox.showwarning("Rename Error", "Please save the file before renaming.")
            return

        current_dir = os.path.dirname(self.current_file)
        current_basename = os.path.basename(self.current_file)

        new_basename = simpledialog.askstring(
            "Rename File",
            "Enter new filename:",
            initialvalue=current_basename,
            parent=self.root # Make dialog modal to the main window
        )

        # Handle cancellation or empty input
        if not new_basename:
            return # User cancelled or entered nothing

        # Prevent renaming to the same name (optional, but good practice)
        if new_basename == current_basename:
            return # No change needed

        new_file_path = os.path.join(current_dir, new_basename)

        # Check if the new filename already exists
        if os.path.exists(new_file_path):
            if not messagebox.askyesno(
                "Confirm Overwrite",
                f"'{new_basename}' already exists.\nDo you want to replace it?"
            ):
                return # User chose not to overwrite

        try:
            # Attempt to rename the file on disk
            os.rename(self.current_file, new_file_path)

            # Update internal state if rename succeeds
            old_filename = os.path.basename(self.current_file) # For status message
            self.current_file = new_file_path
            new_filename = os.path.basename(self.current_file) # Use the actual new name

            # Update window title
            self.root.title(f"Notething - {new_filename}")

            # Update status bar
            status_text = f"Status: Renamed '{old_filename}' to '{new_filename}'"
            self.status_bar.config(text=status_text)
            self.tooltip.set_text(status_text)

        except OSError as e:
            messagebox.showerror("Rename Error", f"Could not rename file:\n{e}")
        except Exception as e: # Catch other potential errors
             messagebox.showerror("Rename Error", f"An unexpected error occurred:\n{e}")

    # --- Add method to insert Sydney time ---
    def insert_sydney_time(self):
        """Inserts the current time in Sydney, NSW at the cursor position."""
        try:
            sydney_tz = pytz.timezone('Australia/Sydney')
            sydney_time = datetime.now(sydney_tz)
            # Format as HH:MM:SS AM/PM or use 24-hour HH:MM:SS
            time_str = sydney_time.strftime("%I:%M %p") # 12-hour format with AM/PM, no seconds
            # time_str = sydney_time.strftime("%H:%M:%S")   # 24-hour format
            
            self.text_area.insert(tk.INSERT, time_str)
        except Exception as e:
            messagebox.showerror("Time Error", f"Could not get Sydney time:\n{e}")
    # --- End method to insert Sydney time ---

    # --- Method to prompt for date and insert it ---
    def prompt_and_insert_date(self):
        """Opens a calendar dialog and inserts the selected date."""
        dialog = CalendarDialog(self.root) # Use the new CalendarDialog
        self.root.wait_window(dialog) # Make it modal

        if dialog.result_date: # Check the result attribute from CalendarDialog
            date_obj = dialog.result_date
            # Format: e.g., 23 Jul 2024
            date_str = date_obj.strftime("%d %b %Y")
            
            original_autoseparators = self.text_area.cget("autoseparators")
            self.text_area.config(autoseparators=False)
            try:
                self.text_area.insert(tk.INSERT, date_str)
                self.text_area.edit_separator()
            finally:
                self.text_area.config(autoseparators=original_autoseparators)
            
            self.line_formatter._update_line_formatting()
    # --- End method to prompt for date ---

    # --- Methods to Open Find/Replace Dialog ---
    def _launch_find_replace_dialog(self, replace_mode=False):
        if self.find_dialog is not None:
            try:
                self.find_dialog.lift()
                return
            except tk.TclError:
                self.find_dialog = None

        self.find_dialog = FindReplaceDialog(self.root, self.text_area, replace_mode=replace_mode)

        # Set default values for replace dialog
        if replace_mode:
            self.find_dialog.find_what_var.set(Notepad.default_find_text)
            self.find_dialog.replace_with_var.set(Notepad.default_replace_text)
        else:
            self.find_dialog.find_what_var.set(self.last_find_text)
        if replace_mode:
            self.find_dialog.match_case_var.set(Notepad.last_match_case_setting)  # Use class variable

        # Set focus correctly
        if replace_mode:
            self.find_dialog.replace_entry.focus_set()
        else:
            self.find_dialog.find_entry.focus_set()

        # Register callback for when dialog is closed
        self.find_dialog.bind("<Destroy>", self._find_dialog_closed)

    def open_find_dialog(self):
        self._launch_find_replace_dialog(replace_mode=False)

    def open_replace_dialog(self):
        self._launch_find_replace_dialog(replace_mode=True)

    def _find_dialog_closed(self, event=None):
        # Check if the event widget is the dialog we tracked
        if self.find_dialog is not None and event.widget == self.find_dialog:
             try:
                 self.text_area.tag_remove("search_highlight", "1.0", tk.END)
             except tk.TclError:
                 pass

             # Save last values before clearing the reference
             try:
                  self.last_find_text = self.find_dialog.find_what_var.get()
                  if hasattr(self.find_dialog, 'replace_with_var'):
                       self.last_replace_text = self.find_dialog.replace_with_var.get()
                  # Save match case setting to class variable
                  Notepad.last_match_case_setting = self.find_dialog.match_case_var.get()
             except tk.TclError:
                  pass
             finally:
                  self.find_dialog = None
                  self.line_formatter._update_line_formatting()

    # --- End Find/Replace Dialog Methods ---

    # --- Add Tab/Shift-Tab Handlers ---
    def _handle_tab_key(self, event=None):
        """Handles Tab key press for indentation."""
        try:
            sel_first_idx = self.text_area.index(tk.SEL_FIRST)
            sel_last_idx = self.text_area.index(tk.SEL_LAST)
        except tk.TclError: # No selection
            # Default behavior: insert a tab at cursor
            self.text_area.insert(tk.INSERT, "\t")
            self.line_formatter._update_line_formatting() # Update colors if a line prefix changes
            return "break" # Prevent focus change

        first_line_num = int(sel_first_idx.split('.')[0])
        last_line_num_sel = int(sel_last_idx.split('.')[0])
        last_char_num_sel = int(sel_last_idx.split('.')[1])

        # Determine the actual last line to process for indentation
        if last_char_num_sel == 0 and last_line_num_sel > first_line_num:
            # Selection ends at the start of a new line, so process up to the line before it
            last_line_to_process = last_line_num_sel - 1
        else:
            last_line_to_process = last_line_num_sel
        
        # If it's effectively a single line selection where start and end are on the same line,
        # and the selection doesn't span a newline character, insert a tab.
        # This handles selecting part of a single line and pressing tab.
        if first_line_num == last_line_to_process and '\n' not in self.text_area.get(sel_first_idx, sel_last_idx):
            # For single line partial selection, standard tab insertion at cursor might be preferred
            # or indenting the line if cursor is at start.
            # For simplicity, let's indent the line if any part of it is selected.
            # If we want to insert tab at cursor for single line:
            # current_cursor_pos = self.text_area.index(tk.INSERT)
            # self.text_area.insert(current_cursor_pos, "\t")
            # self.text_area.tag_remove(tk.SEL, "1.0", tk.END) # Clear selection
            # self.text_area.mark_set(tk.INSERT, f"{current_cursor_pos}+{len('\t')}c")
            # self.line_formatter._update_line_formatting()
            # return "break"
            #
            # For indenting the single selected line:
            pass # Fall through to multi-line logic which will indent this single line


        original_autoseparators = self.text_area.cget("autoseparators")
        self.text_area.config(autoseparators=False)
        modified = False
        try:
            for i in range(first_line_num, last_line_to_process + 1):
                self.text_area.insert(f"{i}.0", "\t")
                modified = True
            
            if modified:
                self.text_area.edit_separator()
                
                # Re-select the indented block
                self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
                
                adj_sel_first_char_idx = int(sel_first_idx.split('.')[1]) + 1
                adj_sel_first = f"{first_line_num}.{adj_sel_first_char_idx}"
                
                adj_sel_last_char_idx = last_char_num_sel
                if last_line_num_sel <= last_line_to_process: # if the line of sel_last was indented
                    adj_sel_last_char_idx += 1
                adj_sel_last = f"{last_line_num_sel}.{adj_sel_last_char_idx}"

                self.text_area.tag_add(tk.SEL, adj_sel_first, adj_sel_last)
                self.text_area.mark_set(tk.INSERT, adj_sel_last) # Move cursor to end of new selection
                self.line_formatter._update_line_formatting()
        finally:
            self.text_area.config(autoseparators=original_autoseparators)

        return "break"

    def _handle_shift_tab_key(self, event=None):
        """Handles Shift+Tab key press for outdenting."""
        try:
            sel_first_idx = self.text_area.index(tk.SEL_FIRST)
            sel_last_idx = self.text_area.index(tk.SEL_LAST)
        except tk.TclError: # No selection
            # When no selection, try to outdent current line
            current_line = self.text_area.index(tk.INSERT).split('.')[0]
            line_start = f"{current_line}.0"
            
            # Check if line starts with a tab or spaces
            first_char = self.text_area.get(line_start, f"{line_start}+1c")
            if first_char == "\t":
                self.text_area.delete(line_start, f"{line_start}+1c")
                return "break"
            elif self.text_area.get(line_start, f"{line_start}+4c") == "    ":
                self.text_area.delete(line_start, f"{line_start}+4c")
                return "break"
            return "break"

        first_line_num = int(sel_first_idx.split('.')[0])
        last_line_num_sel = int(sel_last_idx.split('.')[0])
        last_char_num_sel = int(sel_last_idx.split('.')[1])

        if last_char_num_sel == 0 and last_line_num_sel > first_line_num:
            last_line_to_process = last_line_num_sel - 1
        else:
            last_line_to_process = last_line_num_sel

        original_autoseparators = self.text_area.cget("autoseparators")
        self.text_area.config(autoseparators=False)
        modified_count = 0
        
        # Track character shift for the lines containing start and end of selection
        sel_first_line_char_shift = 0
        sel_last_line_char_shift = 0

        try:
            for i in range(first_line_num, last_line_to_process + 1):
                current_shift = 0
                line_start = f"{i}.0"
                
                # Check for tab first
                if self.text_area.get(line_start, f"{line_start}+1c") == "\t":
                    self.text_area.delete(line_start, f"{line_start}+1c")
                    current_shift = -1
                    modified_count += 1
                # Then check for spaces
                elif self.text_area.get(line_start, f"{line_start}+4c") == "    ":
                    self.text_area.delete(line_start, f"{line_start}+4c")
                    current_shift = -4
                    modified_count += 1
                
                if i == first_line_num:
                    sel_first_line_char_shift = current_shift
                if i == last_line_num_sel:
                    sel_last_line_char_shift = current_shift
            
            if modified_count > 0:
                self.text_area.edit_separator()
                self.text_area.tag_remove(tk.SEL, "1.0", tk.END)

                # Adjust selection indices based on the shifts
                adj_sel_first_char_idx = max(0, int(sel_first_idx.split('.')[1]) + sel_first_line_char_shift)
                adj_sel_first = f"{first_line_num}.{adj_sel_first_char_idx}"
                
                adj_sel_last_char_idx = max(0, last_char_num_sel + sel_last_line_char_shift)
                adj_sel_last = f"{last_line_num_sel}.{adj_sel_last_char_idx}"
                
                # Ensure selection direction is maintained (start <= end)
                if self.text_area.compare(adj_sel_first, "<=", adj_sel_last):
                    self.text_area.tag_add(tk.SEL, adj_sel_first, adj_sel_last)
                    self.text_area.mark_set(tk.INSERT, adj_sel_last)
                else:
                    # If selection would invert, collapse it to the start
                    self.text_area.mark_set(tk.INSERT, adj_sel_first)
                
                self.self.line_formatter._update_line_formatting()
        finally:
            self.text_area.config(autoseparators=original_autoseparators)
        
        return "break"
    # --- End Tab/Shift-Tab Handlers ---

    # --- Add Enter Key Handler for Auto-Indentation ---
    def _handle_enter_key(self, event=None):
        """Handles Enter key press for auto-indentation."""
        # First handle any existing selection
        try:
            sel_start = self.text_area.index(tk.SEL_FIRST)
            sel_end = self.text_area.index(tk.SEL_LAST)
            # Get the line info for the selection start
            current_cursor_pos = sel_start
            # Delete the selected text
            self.text_area.delete(sel_start, sel_end)
        except tk.TclError:
            # No selection exists
            current_cursor_pos = self.text_area.index(tk.INSERT)

        current_line_start_idx = self.text_area.index(f"{current_cursor_pos} linestart")
        current_line_end_idx = self.text_area.index(f"{current_cursor_pos} lineend")
        current_line_content = self.text_area.get(current_line_start_idx, current_line_end_idx)

        # --- Auto-add full stop if enabled ---
        if getattr(Notepad, 'auto_full_stop', False):
            if current_line_content.strip():
                stripped = current_line_content.rstrip()
                # Skip adding full stop if line starts with # (markdown heading)
                if not stripped.startswith('#') and not stripped.endswith(('.', '!', '?')):
                    self.text_area.delete(current_line_start_idx, current_line_end_idx)
                    self.text_area.insert(current_line_start_idx, stripped + '.')
                    # Update current_line_content and adjust cursor
                    current_line_content = stripped + '.'
                    # If cursor was at end, move it forward by 1
                    if self.text_area.index(current_cursor_pos) == current_line_end_idx:
                        current_cursor_pos = f"{current_cursor_pos.split('.')[0]}.{int(current_cursor_pos.split('.')[1])+1}"
                    current_line_end_idx = self.text_area.index(f"{current_line_start_idx} lineend")
        # --- End auto full stop ---

        # Get the text before and after cursor on the current line
        text_before_cursor = self.text_area.get(current_line_start_idx, current_cursor_pos)
        text_after_cursor = self.text_area.get(current_cursor_pos, current_line_end_idx)

        # Extract leading whitespace
        leading_whitespace = ""
        for char in current_line_content:
            if char.isspace():  # Catches spaces, tabs, etc.
                leading_whitespace += char
            else:
                break

        # Store highlight ranges for the current line
        highlight_ranges = []
        for i in range(0, len(self.text_area.tag_ranges("highlight")), 2):
            start = str(self.text_area.tag_ranges("highlight")[i])
            end = str(self.text_area.tag_ranges("highlight")[i + 1])
            if (self.text_area.compare(start, ">=", current_line_start_idx) and 
                self.text_area.compare(end, "<=", current_line_end_idx)):
                highlight_ranges.append((start, end))

        original_autoseparators = self.text_area.cget("autoseparators")
        self.text_area.config(autoseparators=False)
        
        try:
            # Scenario 1: Pressing Enter on a line that *only* contains whitespace
            if current_line_content.strip() == "":
                self.text_area.delete(current_line_start_idx, current_line_end_idx)
                self.text_area.insert(current_line_start_idx, "\n")
                self.text_area.edit_separator()
            else:
                # Scenario 2: Split the line at cursor position and maintain indentation
                # Delete the current line
                self.text_area.delete(current_line_start_idx, current_line_end_idx)
                # Insert the text before cursor
                self.text_area.insert(current_line_start_idx, text_before_cursor)
                # Insert newline and indented text after cursor
                self.text_area.insert(current_cursor_pos, "\n" + leading_whitespace + text_after_cursor)
                # Move cursor to the start of the indented text
                new_cursor_pos = f"{int(current_cursor_pos.split('.')[0]) + 1}.{len(leading_whitespace)}"
                self.text_area.mark_set(tk.INSERT, new_cursor_pos)
                self.text_area.edit_separator()

                # Restore highlight tags for the split lines
                for start, end in highlight_ranges:
                    # Calculate relative positions within the line
                    start_col = int(start.split('.')[1])
                    end_col = int(end.split('.')[1])
                    
                    # Handle highlight for first line (before cursor)
                    if start_col < len(text_before_cursor):
                        new_start = f"{current_line_start_idx}+{start_col}c"
                        new_end = f"{current_line_start_idx}+{min(end_col, len(text_before_cursor))}c"
                        self.text_area.tag_add("highlight", new_start, new_end)
                    
                    # Handle highlight for second line (after cursor)
                    if end_col > len(text_before_cursor):
                        new_start = f"{new_cursor_pos}+{max(0, start_col - len(text_before_cursor))}c"
                        new_end = f"{new_cursor_pos}+{end_col - len(text_before_cursor)}c"
                        self.text_area.tag_add("highlight", new_start, new_end)
        finally:
            self.text_area.config(autoseparators=original_autoseparators)

        self.line_formatter._update_line_formatting()
        return "break"  # Prevent default Tkinter Enter behavior
    # --- End Enter Key Handler ---

    # --- Add Smart Home Key Handler ---
    def _handle_home_key(self, event=None):
        """Handles Home key press for smart home behavior."""
        current_cursor_pos = self.text_area.index(tk.INSERT)
        current_line_start = self.text_area.index(f"{current_cursor_pos} linestart")
        current_line_end = self.text_area.index(f"{current_cursor_pos} lineend")
        current_line_content = self.text_area.get(current_line_start, current_line_end)

        # Find the first non-whitespace character
        first_non_whitespace = 0
        for i, char in enumerate(current_line_content):
            if not char.isspace():
                first_non_whitespace = i
                break

        # If cursor is already at first non-whitespace, go to start of line
        current_column = int(current_cursor_pos.split('.')[1])
        if current_column == first_non_whitespace:
            target_pos = current_line_start
        else:
            # Go to first non-whitespace
            target_pos = f"{current_line_start}+{first_non_whitespace}c"

        # Check if Shift is being held down
        if event and event.state & 0x1:  # 0x1 is the Shift modifier
            try:
                # Try to get the existing selection anchor
                sel_start = self.text_area.index(tk.SEL_FIRST)
                sel_end = self.text_area.index(tk.SEL_LAST)
                # If we have a selection, use the opposite end from the cursor as the anchor
                if self.text_area.compare(current_cursor_pos, "==", sel_start):
                    anchor = sel_end
                else:
                    anchor = sel_start
            except tk.TclError:
                # If no selection exists, use current cursor position as anchor
                anchor = current_cursor_pos

            # Set the selection from anchor to target
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
            if self.text_area.compare(anchor, "<", target_pos):
                self.text_area.tag_add(tk.SEL, anchor, target_pos)
            else:
                self.text_area.tag_add(tk.SEL, target_pos, anchor)
            self.text_area.mark_set(tk.INSERT, target_pos)

        else:
            # Just move cursor without selection
            self.text_area.mark_set(tk.INSERT, target_pos)

        return "break" # Prevent default Home behavior
    # --- End Smart Home Key Handler ---

    def _on_close_window(self):
        """Handles window close event."""
        # Decrement the window count
        Notepad.open_window_count -= 1
        
        # If this was the last window, reset the first window initialization flag
        if Notepad.open_window_count == 0:
            Notepad.first_window_initialized = False
            Notepad.first_window_x = None
            Notepad.first_window_y = None
            
        self.root.destroy()

    def _add_to_recent_files(self, filepath):
        """Add a file to the recent files list"""
        # Convert to absolute path
        filepath = os.path.abspath(filepath)
        
        # If the file is already in the list, remove it (to move it to the top)
        if filepath in Notepad.recent_files:
            Notepad.recent_files.remove(filepath)
            
        # Add to the beginning of the list
        Notepad.recent_files.insert(0, filepath)
        
        # Limit the list to MAX_RECENT_FILES
        while len(Notepad.recent_files) > Notepad.MAX_RECENT_FILES:
            Notepad.recent_files.pop()
            
        # Update the menu
        self._update_recent_menu()
        
        # Save the list to a file
        self._save_recent_files()
        
    def _update_recent_menu(self):
        """Update the recent files menu"""
        # Clear the current menu
        self.recent_menu.delete(0, tk.END)
        
        if not Notepad.recent_files:
            # If no recent files, add a disabled item
            self.recent_menu.add_command(label="No recent files", state=tk.DISABLED)
        else:
            # Add each recent file to the menu
            for i, filepath in enumerate(Notepad.recent_files):
                # Get just the filename for display
                filename = os.path.basename(filepath)
                # Create a lambda that captures the current filepath
                self.recent_menu.add_command(
                    label=f"{i+1}. {filename}",
                    command=lambda path=filepath: self._load_file(path)
                )
                
            # Add a separator and a clear option
            self.recent_menu.add_separator()
            self.recent_menu.add_command(label="Clear Recent Files", command=self._clear_recent_files)
    
    def _clear_recent_files(self):
        """Clear the list of recent files"""
        Notepad.recent_files = []
        self._update_recent_menu()
        self._save_recent_files()
        
    def _save_recent_files(self):
        """Save the recent files list to a file"""
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".notething")
            os.makedirs(config_dir, exist_ok=True)
            
            recent_file_path = os.path.join(config_dir, "recent_files.txt")
            with open(recent_file_path, 'w', encoding='utf-8') as f:
                for filepath in Notepad.recent_files:
                    f.write(f"{filepath}\n")
        except Exception as e:
            print(f"Error saving recent files: {e}")
    
    def _load_recent_files(self):
        """Load the recent files list from a file"""
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".notething")
            recent_file_path = os.path.join(config_dir, "recent_files.txt")
            
            if os.path.exists(recent_file_path):
                with open(recent_file_path, 'r', encoding='utf-8') as f:
                    Notepad.recent_files = [line.strip() for line in f if line.strip()]
                    
                # Limit to MAX_RECENT_FILES
                while len(Notepad.recent_files) > Notepad.MAX_RECENT_FILES:
                    Notepad.recent_files.pop()
                    
                # Update the menu if it exists
                if hasattr(self, 'recent_menu'):
                    self._update_recent_menu()
        except Exception as e:
            print(f"Error loading recent files: {e}")

    def _setup_key_bindings(self):
        """Setup keyboard shortcuts/bindings."""
        # Existing bindings
        self.text_area.bind("<Control-h>", self._handle_ctrl_h)
        self.text_area.bind("<Control-Home>", self._handle_ctrl_home)
        self.text_area.bind("<Control-End>", self._handle_ctrl_end)
        self.text_area.bind("<Control-Shift-Home>", self._handle_ctrl_home)
        self.text_area.bind("<Control-Shift-End>", self._handle_ctrl_end)
        
        # Add F5 and F6 bindings
        self.text_area.bind("<F5>", lambda e: self.insert_sydney_time())
        self.text_area.bind("<F6>", lambda e: self.prompt_and_insert_date())
        
        # Add explicit Shift+Tab binding
        self.text_area.bind("<Shift-Tab>", self._handle_shift_tab_key)
        
        # Suppress default text widget behaviors
        self.text_area.bind("<Control-k>", lambda e: "break")  # Suppress delete to end of line
        self.text_area.bind("<Control-d>", lambda e: "break")  # Suppress delete character
        
        # Change Ctrl+O to open file dialog
        def handle_ctrl_o(event):
            self.open_file()
            return "break"  # Prevent default behavior
        
        # Bind to both root and text_area
        self.root.bind("<Control-o>", handle_ctrl_o)
        self.text_area.bind("<Control-o>", handle_ctrl_o)

    def _handle_ctrl_h(self, event):
        """Handle Ctrl+H key press."""
        self.open_replace_dialog()
        return "break"  # Prevent the default backspace behavior

    def _handle_ctrl_home(self, event=None):
        """Handle Ctrl+Home to move to the beginning of the document."""
        current_pos = self.text_area.index(tk.INSERT)
        
        # If Shift is pressed, extend/modify the selection
        if event.state & 0x1:  # 0x1 is the Shift modifier
            try:
                # Check if there's an existing selection
                sel_start = self.text_area.index(tk.SEL_FIRST)
                sel_end = self.text_area.index(tk.SEL_LAST)
                
                # If cursor is at selection start, keep selection end as anchor
                if self.text_area.compare(current_pos, "==", sel_start):
                    self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
                    self.text_area.tag_add(tk.SEL, "1.0", sel_end)
                else:
                    # If cursor is at selection end or no selection,
                    # extend selection from current position to start
                    self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
                    self.text_area.tag_add(tk.SEL, "1.0", current_pos)
            except tk.TclError:
                # No existing selection, create one from current pos to start
                self.text_area.tag_add(tk.SEL, "1.0", current_pos)
        else:
            # No Shift key - just move cursor and clear selection
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
        
        # Move cursor to the beginning of the document
        self.text_area.mark_set(tk.INSERT, "1.0")
        
        # Make sure the beginning is visible
        self.text_area.see("1.0")
        
        return "break"  # Prevent default behavior

    def _handle_ctrl_end(self, event=None):
        """Handle Ctrl+End to move to the end of the document."""
        current_pos = self.text_area.index(tk.INSERT)
        end_pos = self.text_area.index(tk.END)
        
        # If Shift is pressed, extend the selection
        if event.state & 0x1:  # 0x1 is the Shift modifier
            try:
                # If there's already a selection, maintain its start
                sel_start = self.text_area.index(tk.SEL_FIRST)
                self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
                self.text_area.tag_add(tk.SEL, sel_start, end_pos)
            except tk.TclError:
                # If no selection, create one from current pos to end
                self.text_area.tag_add(tk.SEL, current_pos, end_pos)
        
        # Move cursor to the end of the document
        self.text_area.mark_set(tk.INSERT, end_pos)
        
        # Make sure the end is visible
        self.text_area.see(end_pos)
        
        return "break"  # Prevent default behavior

    def _save_settings(self):
        """Save all application settings to file"""
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".notething")
            os.makedirs(config_dir, exist_ok=True)
            
            settings_path = os.path.join(config_dir, "settings.txt")
            with open(settings_path, 'w', encoding='utf-8') as f:
                # Save settings as key=value pairs
                f.write(f"reopen_last_file={int(Notepad.reopen_last_file)}\n")
                f.write(f"match_case={int(Notepad.last_match_case_setting)}\n")
                f.write(f"line_formatting={int(Notepad.line_formatting_enabled)}\n")
                f.write(f"auto_capitalize_headings={int(Notepad.auto_capitalize_headings)}\n")
                f.write(f"auto_capitalize_first_word={int(Notepad.auto_capitalize_first_word)}\n")
                f.write(f"auto_capitalize_indented={int(Notepad.auto_capitalize_indented)}\n")
                f.write(f"highlight_enabled={int(Notepad.highlight_enabled)}\n")
                f.write(f"auto_full_stop={int(Notepad.auto_full_stop)}\n")
                f.write(f"readonly_mode={int(Notepad.readonly_mode)}\n")
                f.write(f"default_find_text={Notepad.default_find_text}\n")
                f.write(f"default_replace_text={Notepad.default_replace_text}\n")
                
            # Also save recent files
            self._save_recent_files()
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _load_settings(self):
        """Load application settings from file"""
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".notething")
            settings_path = os.path.join(config_dir, "settings.txt")
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == "reopen_last_file":
                                Notepad.reopen_last_file = bool(int(value))
                            elif key == "match_case":
                                Notepad.last_match_case_setting = bool(int(value))
                            elif key == "line_formatting":
                                Notepad.line_formatting_enabled = bool(int(value))
                            elif key == "auto_capitalize_headings":
                                Notepad.auto_capitalize_headings = bool(int(value))
                            elif key == "auto_capitalize_first_word":
                                Notepad.auto_capitalize_first_word = bool(int(value))
                            elif key == "auto_capitalize_indented":
                                Notepad.auto_capitalize_indented = bool(int(value))
                            elif key == "highlight_enabled":
                                Notepad.highlight_enabled = bool(int(value))
                            elif key == "auto_full_stop":
                                Notepad.auto_full_stop = bool(int(value))
                            elif key == "readonly_mode":
                                Notepad.readonly_mode = bool(int(value))
                            elif key == "default_find_text":
                                Notepad.default_find_text = value
                            elif key == "default_replace_text":
                                Notepad.default_replace_text = value
            
            # Also load recent files
            self._load_recent_files()
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def _toggle_reopen_last_file(self):
        """Toggle the reopen last file setting"""
        Notepad.reopen_last_file = not Notepad.reopen_last_file
        self._save_settings()
        
        # Update the menu checkmark
        if Notepad.reopen_last_file:
            self.options_menu.entryconfig("Reopen Last File on Startup", selectcolor="black")
        else:
            self.options_menu.entryconfig("Reopen Last File on Startup", selectcolor="white")

    def open_settings_dialog(self):
        """Opens the settings dialog."""
        dialog = SettingsDialog(self.root, self)
        self.root.wait_window(dialog)
        
        # Update any UI elements that depend on settings
        if hasattr(self, 'options_menu'):
            if Notepad.reopen_last_file:
                self.options_menu.entryconfig("Reopen Last File on Startup", selectcolor="black")
            else:
                self.options_menu.entryconfig("Reopen Last File on Startup", selectcolor="white")

    # Add this method to Notepad class
    def _capitalize_first_word(self, line):
        """Capitalize the first word in a line, respecting special prefixes and indentation."""
        # Skip empty lines
        if not line.strip():
            return line
            
        # Check indentation
        leading_space = ''
        for char in line:
            if char.isspace():
                leading_space += char
            else:
                break
            
        # Skip indented lines if the setting is disabled
        if not Notepad.auto_capitalize_indented and leading_space:
            return line
            
        # Get the content after leading whitespace
        content = line[len(leading_space):]
        if not content:  # If line is only whitespace
            return line
    
        # Handle special prefixes
        prefixes = ['T ', 'N ', 'X ', 'C ', 'M ']
        for prefix in prefixes:
            if content.startswith(prefix):
                # Split remaining text into words
                remaining = content[2:].lstrip()
                if remaining:
                    # Capitalize first word after prefix
                    first_word = remaining.split()[0]
                    capitalized = first_word[0].upper() + first_word[1:] if len(first_word) > 1 else first_word.upper()
                    return leading_space + prefix + content[2:].replace(first_word, capitalized, 1)
                return line
        
        # Handle heading prefixes
        heading_prefixes = ['# ', '## ', '### ']
        for prefix in heading_prefixes:
            if content.startswith(prefix):
                remaining = content[len(prefix):].lstrip()
                if remaining:
                    # Capitalize first word after heading prefix
                    first_word = remaining.split()[0]
                    capitalized = first_word[0].upper() + first_word[1:] if len(first_word) > 1 else first_word.upper()
                    return leading_space + prefix + content[len(prefix):].replace(first_word, capitalized, 1)
                return line
        
        # Handle regular lines
        words = content.split()
        if words:
            # Capitalize first word
            first_word = words[0]
            capitalized = first_word[0].upper() + first_word[1:] if len(first_word) > 1 else first_word.upper()
            return leading_space + content.replace(first_word, capitalized, 1)
        
        return line

    def copy_file_path(self):
        """Copy the current file path to clipboard."""
        if self.current_file:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_file)
            status_text = f"Status: Copied path to clipboard: {self.current_file}"
            self.status_bar.config(text=status_text)
            self.tooltip.set_text(status_text)
        else:
            messagebox.showinfo("Copy Path", "No file is currently open.")

    def _detect_urls(self, event=None):
        """Detect URLs and file paths in the text and make them clickable."""
        self.text_area.tag_remove("hyperlink", "1.0", tk.END)
        text = self.text_area.get("1.0", tk.END)
        # Improved URL pattern: match until whitespace or newline
        url_pattern = r'(https?://[^\s\n]+|www\.[^\s\n]+|ftp://[^\s\n]+)'
        # Windows file path: C:\... (allow spaces in the filename part)
        win_path_pattern = r'([A-Za-z]:[\\/](?:[^\s<>:"|?*\r\n]+[\\/])*[^\s<>:"|?*\r\n]+(?: [^\s<>:"|?*\r\n]+)*)'
        # Unix path: /... (must have at least one slash after the initial slash)
        unix_path_pattern = r'(/[^-\s<>:"|?*]+/[^-\s<>:"|?*]+(?:/[^-\s<>:"|?*]+)*)'
        for pattern in [url_pattern, win_path_pattern, unix_path_pattern]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = f"1.0+{match.start()}c"
                end = f"1.0+{match.end()}c"
                self.text_area.tag_add("hyperlink", start, end)
        self.line_formatter._update_line_formatting()

        # Ensure tag_bind is set only once
        self.text_area.tag_bind("hyperlink", "<Enter>", lambda e: self.text_area.config(cursor="hand2"))
        self.text_area.tag_bind("hyperlink", "<Leave>", lambda e: self.text_area.config(cursor="arrow"))
        self.text_area.tag_bind("hyperlink", "<Button-1>", self._handle_click)

    def _handle_click(self, event):
        """Handle clicks on hyperlinks by extracting the text under the cursor and opening it."""
        index = self.text_area.index(f"@{event.x},{event.y}")
        ranges = self.text_area.tag_ranges("hyperlink")
        for start, end in zip(ranges[::2], ranges[1::2]):
            if self.text_area.compare(index, '>=', start) and self.text_area.compare(index, '<', end):
                url = self.text_area.get(start, end)
                self._open_url_or_file(url)
                return "break"
        return None

    def _open_url_or_file(self, path):
        """Open a URL in the default browser or a file in its default application."""
        try:
            # Check if it's a URL
            if path.startswith(('http://', 'https://', 'www.', 'ftp://')):
                # Add http:// if it starts with www
                if path.startswith('www.'):
                    path = 'http://' + path
                webbrowser.open(path)
            # Check if it's a file path
            elif os.path.exists(path):
                # Use the appropriate command based on the OS
                if os.name == 'nt':  # Windows
                    os.startfile(path)
                else:  # Unix-like
                    subprocess.run(['xdg-open', path])
            else:
                messagebox.showinfo("Error", f"Could not open: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open {path}: {str(e)}")

    def _set_file_permissions(self, filepath, readonly):
        """Set file permissions to readonly or writable."""
        try:
            if os.path.exists(filepath):
                if readonly:
                    # Set readonly permissions
                    os.chmod(filepath, 0o444)  # Read-only for all users
                else:
                    # Set writable permissions
                    os.chmod(filepath, 0o666)  # Read-write for all users
                return True
        except Exception as e:
            messagebox.showerror("Permission Error", f"Could not change file permissions:\n{e}")
        return False

    def open_new_window(self):
        """Open a new independent window."""
        # Create a new Tk root window instead of a Toplevel
        new_root = TkinterDnD.Tk()
        
        # Apply the same theme as the main window
        style = ttk.Style(new_root)
        try:
            if new_root.tk.call('tk', 'windowingsystem') == 'win32':
                style.theme_use('vista')
            elif new_root.tk.call('tk', 'windowingsystem') == 'aqua':
                style.theme_use('aqua')
            else:
                style.theme_use('clam')
        except tk.TclError:
            style.theme_use("default")
            
        # Cascade: offset the new window from the current one
        x = self.root.winfo_x() + 40
        y = self.root.winfo_y() + 40
        new_root.geometry(f"+{x}+{y}")
        
        # Create a new Notepad instance with the new root
        Notepad(new_root)
        
        # Start the new window's event loop
        new_root.mainloop()

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