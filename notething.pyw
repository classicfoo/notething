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


# --- Calendar Dialog Class (using tkcalendar) ---
class CalendarDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        
        # Hide the window initially until we position it correctly
        self.withdraw()
        
        self.transient(master)
        self.title("Select Date")
        self.result_date = None # Will store the selected datetime.date object

        # Get current date for initial display
        now = datetime.now()

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Create the Calendar widget
        self.cal = Calendar(main_frame,
                            selectmode='day', # Allow selecting a single day
                            year=now.year,
                            month=now.month,
                            day=now.day,
                            date_pattern='dd/mm/yyyy') # Display pattern on calendar
        self.cal.pack(pady=10, padx=10, fill="both", expand=True)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(5,0), fill=tk.X)
        button_frame.columnconfigure(0, weight=1) # Make buttons expand if needed
        button_frame.columnconfigure(1, weight=1)

        ok_button = ttk.Button(button_frame, text="OK", command=self._on_ok, width=12)
        ok_button.pack(side=tk.LEFT, padx=(0,5), expand=True, fill=tk.X)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._on_cancel, width=12)
        cancel_button.pack(side=tk.RIGHT, padx=(5,0), expand=True, fill=tk.X)

        # --- Centering and Modality ---
        self.update_idletasks()
        
        # Calculate positioning before showing the window
        padding_x = 40 
        padding_y = 60
        dialog_width = self.cal.winfo_reqwidth() + padding_x
        dialog_height = self.cal.winfo_reqheight() + self.cal.winfo_reqheight()//2 + padding_y

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        self.resizable(False, False)
        self.bind("<Escape>", lambda e: self._on_cancel())
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        self.grab_set() # Make modal
        
        # Now show the window after everything is set up
        self.deiconify()
        
        self.focus_set()
        self.cal.focus_set() # Set focus to the calendar

    def _on_ok(self):
        self.result_date = self.cal.selection_get() # Returns a datetime.date object
        self.destroy()

    def _on_cancel(self):
        self.result_date = None
        self.destroy()
# --- End Calendar Dialog Class ---

# --- Find/Replace Dialog Class ---
class FindReplaceDialog(tk.Toplevel):
    def __init__(self, master, text_widget, replace_mode=False):
        # Store references before creating the dialog
        self.text_widget = text_widget
        self.master = master
        
        # Store the current selection before creating the Toplevel
        try:
            self.initial_sel_start = self.text_widget.index(tk.SEL_FIRST)
            self.initial_sel_end = self.text_widget.index(tk.SEL_LAST)
            has_selection = True
        except tk.TclError:
            self.initial_sel_start = None
            self.initial_sel_end = None
            has_selection = False
        
        # Create a super unique tag name for preserving selection
        self.preserved_sel_tag = f"preserved_selection_{id(self)}_{time.time()}"
        
        # Apply the preserved selection tag (using the same colors as normal selection)
        if has_selection:
            self.text_widget.tag_configure(self.preserved_sel_tag, 
                                          background="lightgrey", 
                                          foreground="black")
            self.text_widget.tag_add(self.preserved_sel_tag, 
                                    self.initial_sel_start, 
                                    self.initial_sel_end)
            
        # Now create the dialog
        super().__init__(master)
        
        # Configure dialog and setup UI
        self.title("Find" if not replace_mode else "Find and Replace")
        
        # Configure dialog
        dialog_width = 350
        dialog_height = 150
        self.resizable(False, False)
        self.transient(master)

        # Center the dialog relative to the main window
        window_x = master.winfo_rootx()
        window_y = master.winfo_rooty()
        window_width = master.winfo_width()
        window_height = master.winfo_height()
        
        x = window_x + (window_width // 2) - (dialog_width // 2)
        y = window_y + (window_height // 2) - (dialog_height // 2)
        
        # Set size and position in one call
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Variables for entries and checkbox
        self.find_what_var = tk.StringVar()
        self.replace_with_var = tk.StringVar()
        self.match_case_var = tk.BooleanVar()
        self.find_in_selection_var = tk.BooleanVar()

        # --- UI Elements ---
        # Frame for entries
        entry_frame = ttk.Frame(self, padding="10")
        entry_frame.pack(fill=tk.X)

        ttk.Label(entry_frame, text="Find what:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.find_entry = ttk.Entry(entry_frame, textvariable=self.find_what_var, width=30)
        self.find_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        if replace_mode:
            ttk.Label(entry_frame, text="Replace with:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
            self.replace_entry = ttk.Entry(entry_frame, textvariable=self.replace_with_var, width=30)
            self.replace_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        entry_frame.columnconfigure(1, weight=1) # Make entry expand

        # Frame for options and buttons
        bottom_frame = ttk.Frame(self, padding="5 10")
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        # Options (Checkboxes) - using a sub-frame for alignment
        options_frame = ttk.Frame(bottom_frame)
        options_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.match_case_check = ttk.Checkbutton(options_frame, text="Match case", variable=self.match_case_var)
        self.match_case_check.pack(anchor='w')
        self.find_in_selection_check = ttk.Checkbutton(options_frame, text="Find in selection", variable=self.find_in_selection_var)
        self.find_in_selection_check.pack(anchor='w')
        # Add "Wrap around" later if needed

        # Buttons - using a sub-frame for alignment
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.find_next_btn = ttk.Button(button_frame, text="Find Next", command=self.find_next)
        self.find_next_btn.pack(side=tk.LEFT, padx=2, pady=2)

        if replace_mode:
            self.replace_btn = ttk.Button(button_frame, text="Replace", command=self.replace)
            self.replace_btn.pack(side=tk.LEFT, padx=2, pady=2)
            self.replace_all_btn = ttk.Button(button_frame, text="Replace All", command=self.replace_all)
            self.replace_all_btn.pack(side=tk.LEFT, padx=2, pady=2)

        # --- Initial Focus and Bindings ---
        self.find_entry.focus_set() # Start cursor in "Find what"
        self.protocol("WM_DELETE_WINDOW", self._cleanup_tags_and_destroy) # Handle closing via 'X' button

        # Bind Enter key in find entry to Find Next
        self.find_entry.bind("<Return>", lambda event: self.find_next())
        if replace_mode:
             self.replace_entry.bind("<Return>", lambda event: self.replace())

        # --- Bind Escape key to close the dialog ---
        self.bind("<Escape>", lambda event: self._cleanup_tags_and_destroy())
        # --- End Escape Binding ---

        # Store last search position
        self.last_pos = "1.0"

        # Set "Find in selection" checkbox if there's a preserved selection
        if has_selection:
            self.find_in_selection_var.set(True)
        
        # Make dialog modal
        self.grab_set()
        self.focus_set()
        
        # Bind dialog destruction to cleanup the preserved selection tag
        self.bind("<Destroy>", self._cleanup_tags)

    def _cleanup_tags_and_destroy(self, event=None):
        """Clean up tags and then destroy the dialog"""
        self._cleanup_tags()
        self.destroy()

    def _cleanup_tags(self, event=None):
        """Remove custom tags when the dialog is destroyed"""
        try:
            # Clear ALL selections and custom tags
            self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_widget.tag_remove(self.preserved_sel_tag, "1.0", tk.END)
            self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
            
            # Delete the custom tag completely
            self.text_widget.tag_delete(self.preserved_sel_tag)
            
        except tk.TclError:
            pass  # Widget might already be gone

    def find_next(self):
        find_term = self.find_what_var.get()
        if not find_term:
            messagebox.showwarning("Find", "Please enter text to find.", parent=self)
            return

        # Remove previous highlight
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)

        # Get search boundaries
        if self.find_in_selection_var.get():
            if self.initial_sel_start and self.initial_sel_end:
                # When searching in selection, use the boundaries from our preserved selection
                start_pos = self.text_widget.index(tk.INSERT)
                stop_index = self.initial_sel_end

                # If cursor is outside selection, move it to the beginning of the selection
                if (self.text_widget.compare(start_pos, "<", self.initial_sel_start) or
                    self.text_widget.compare(start_pos, ">", self.initial_sel_end)):
                    start_pos = self.initial_sel_start
            else:
                messagebox.showwarning("Find", "No text selected.", parent=self)
                return
        else:
            start_pos = self.text_widget.index(tk.INSERT)
            stop_index = tk.END

        # Perform the search
        nocase = not self.match_case_var.get()
        found_pos = self.text_widget.search(find_term, start_pos, stopindex=stop_index, nocase=nocase)

        if found_pos:
            # Found a match in the current direction
            end_pos = f"{found_pos}+{len(find_term)}c"
            
            # Apply search highlight
            self.text_widget.tag_add("search_highlight", found_pos, end_pos)
            
            # Ensure search highlight is on top ONLY if we have a preserved selection
            if self.initial_sel_start and self.initial_sel_end:
                try:
                    self.text_widget.tag_raise("search_highlight", self.preserved_sel_tag)
                except tk.TclError:
                    # In case the tag was removed or isn't defined
                    pass
            
            # Make sure the found text is visible
            self.text_widget.see(found_pos)
            
            # Move cursor to end of found text for next search
            self.text_widget.mark_set(tk.INSERT, end_pos)
            
            # Bring dialog back to front
            self.lift()
        else:
            # No match found in the current direction, offer to wrap around
            if self.find_in_selection_var.get():
                # For search in selection, wrap from selection start
                wrap_start = self.initial_sel_start
                wrap_message = "Reached the end of the selection. Continue from the beginning of the selection?"
            else:
                # For normal search, wrap from document start
                wrap_start = "1.0"
                wrap_message = "Reached the end of the document. Continue from the beginning?"
            
            if messagebox.askyesno("Find", wrap_message, parent=self):
                # Try searching from the beginning
                found_pos = self.text_widget.search(find_term, wrap_start, stopindex=start_pos, nocase=nocase)
                if found_pos:
                    end_pos = f"{found_pos}+{len(find_term)}c"
                    self.text_widget.tag_add("search_highlight", found_pos, end_pos)
                    
                    # Only try to raise tag if we have a preserved selection
                    if self.initial_sel_start and self.initial_sel_end:
                        try:
                            self.text_widget.tag_raise("search_highlight", self.preserved_sel_tag)
                        except tk.TclError:
                            pass
                        
                    self.text_widget.see(found_pos)
                    self.text_widget.mark_set(tk.INSERT, end_pos)
                    self.lift()
                else:
                    messagebox.showinfo("Find", f"Cannot find '{find_term}'", parent=self)
            else:
                # User chose not to wrap around, so do nothing
                pass

    def replace(self):
        # --- Refined Replace logic ---
        find_term = self.find_what_var.get()
        replace_term = self.replace_with_var.get()
        nocase = not self.match_case_var.get()

        # Check if the currently highlighted search result matches the find term
        highlight_range = self.text_widget.tag_ranges("search_highlight")
        if highlight_range:
            hl_start, hl_end = highlight_range
            highlighted_text = self.text_widget.get(hl_start, hl_end)

            # Compare highlighted text with find_term (respecting case option)
            text_to_compare = highlighted_text if not nocase else highlighted_text.lower()
            find_to_compare = find_term if not nocase else find_term.lower()

            if text_to_compare == find_to_compare:
                # Remove highlight *before* deleting
                self.text_widget.tag_remove("search_highlight", hl_start, hl_end)
                self.text_widget.delete(hl_start, hl_end)
                self.text_widget.insert(hl_start, replace_term)
                # Move cursor to end of replaced text - this becomes the start for the *next* find
                self.text_widget.mark_set(tk.INSERT, f"{hl_start}+{len(replace_term)}c")
                # DO NOT automatically find next here. Let the user click Find Next again.
                return # Stop after successful replace

        # If no highlight matches the find term,
        # just find the next occurrence (as if Find Next was clicked).
        self.find_next()
        # --- End Refined Replace logic ---

    def replace_all(self):
        # --- Replace All logic with single undo step ---
        find_term = self.find_what_var.get()
        replace_term = self.replace_with_var.get()
        nocase = not self.match_case_var.get()

        if not find_term:
            messagebox.showwarning("Replace All", "Please enter text to find.", parent=self)
            return

        # --- Remove any existing highlight before starting ---
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)

        count = 0
        start_pos = "1.0"

        # --- Temporarily disable auto separators for single undo ---
        try:
            original_autoseparators = self.text_widget.cget("autoseparators")
            self.text_widget.config(autoseparators=False)

            while True:
                found_pos = self.text_widget.search(find_term, start_pos, stopindex=tk.END, nocase=nocase, count=tk.IntVar())
                if not found_pos:
                    break # No more occurrences

                # Check if found_pos is valid before proceeding
                if not found_pos: continue

                end_pos = f"{found_pos}+{len(find_term)}c"
                self.text_area.delete(found_pos, end_pos)
                self.text_area.insert(found_pos, replace_term)
                count += 1
                # Start next search *after* the inserted text
                start_pos = f"{found_pos}+{len(replace_term)}c"

            # --- Manually add undo separator *if* changes were made ---
            if count > 0:
                self.text_widget.edit_separator()

        finally:
            # --- Always restore original autoseparator setting ---
            self.text_widget.config(autoseparators=original_autoseparators)
        # --- End single undo step logic ---

        if count > 0:
             messagebox.showinfo("Replace All", f"Replaced {count} occurrence(s).", parent=self)
             # Update line colors only if changes were made
             self._update_line_colors() # Call helper method
        else:
             messagebox.showinfo("Replace All", f"Cannot find '{find_term}'", parent=self)
        # --- End Replace All logic ---

    # Need access to the main app's color update method
    def _update_line_colors(self):
         if hasattr(self.master, '_update_line_colors'):
              self.master._update_line_colors()


# --- End Find/Replace Dialog Class ---

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

    def __init__(self, root, initial_file=None):
        self.root = root
        self.root.title("Notething")
        
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

        # Create the scrollbar (ttk)
        self.scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create the text area (tk)
        self.font = tkFont.Font(root=self.root, family="Consolas", size=11)
        self.bold_font = tkFont.Font(root=self.root, family="Consolas", size=11, weight="bold") # New bold font
        self.text_area = tk.Text(
            text_frame, # Place text area in the frame
            wrap=tk.WORD,
            font=self.font,
            padx=10,
            pady=10,
            undo=True,  # <-- Enable undo/redo stack
            maxundo=-1,  # <-- -1 means unlimited undo levels
            autoseparators=True,  # <-- Automatically separate undo operations
            exportselection=False,  # <-- This is the key change that keeps selection visible when focus is lost
            yscrollcommand=self.scrollbar.set, # Link text area scroll to scrollbar
            selectbackground="lightgrey", # <-- Change selection background back to lightgrey
            selectforeground="black",      # Keep selection text black
        )
        self.text_area.pack(expand=True, fill='both', side=tk.LEFT) # Pack text area after scrollbar

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

        # --- Find/Replace State ---
        self.find_dialog = None
        self.last_find_text = ""
        self.last_replace_text = ""
        self.last_match_case = False
        # --- End Find/Replace State ---

        self.create_menu()
        self.bind_hotkeys()

        # Bind Ctrl + Backspace to delete the previous word
        self.text_area.bind("<Control-BackSpace>", self.delete_previous_word)

        # --- Bind KeyRelease for Line Coloring ---
        self.text_area.bind("<KeyRelease>", self._update_line_colors_event) # Use _event suffix for direct bindings
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

        # Load initial file if provided, or last file if setting enabled
        if initial_file:
            self._load_file(initial_file)
        elif Notepad.reopen_last_file and Notepad.recent_files:
            # Reopen the most recently used file
            self._load_file(Notepad.recent_files[0])
        else:
            # Ensure initial coloring is applied even for an empty new file
            self._update_line_colors()
            self.root.title("Notething - Untitled") # Set title for new blank window

        # Bind the window close button (X)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_window)

    def create_menu(self):
        # tk.Menu is standard, ttk doesn't replace it
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator='Ctrl+N')
        file_menu.add_command(label="Open", command=self.open_file, accelerator='Ctrl+O')
        
        # Add submenu for recent files
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Open Recent", menu=self.recent_menu)
        self._update_recent_menu()
        
        file_menu.add_command(label="Save", command=self.save_file, accelerator='Ctrl+S')
        file_menu.add_command(label="Rename", command=self.rename_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        menu_bar.add_cascade(label="File", menu=file_menu)

        # --- Add Edit Menu ---
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        # Add Undo/Redo if needed later using text_area.edit_undo(), text_area.edit_redo()
        edit_menu.add_command(label="Find...", command=self.open_find_dialog, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self.open_replace_dialog, accelerator="Ctrl+H")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        # --- End Edit Menu ---

        self.root.config(menu=menu_bar)

    def bind_hotkeys(self):
        self.root.bind('<Control-n>', lambda event: self.new_file())
        self.root.bind('<Control-o>', lambda event: self.open_file())
        self.root.bind('<Control-s>', lambda event: self.save_file())
        self.root.bind('<F5>', lambda event: self.insert_sydney_time())
        self.root.bind('<F6>', lambda event: self.prompt_and_insert_date())
        # --- Add Find/Replace Hotkeys ---
        self.root.bind('<Control-f>', lambda event: self.open_find_dialog())
        self.root.bind('<Control-h>', lambda event: self.open_replace_dialog())
        # --- End Find/Replace Hotkeys ---

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
        """Opens a new, blank Notepad window."""
        new_notepad_root = TkinterDnD.Tk() # Create a new Tk root

        # Apply the same theme setup as the main window
        # This ensures new windows also get the theme.
        style = ttk.Style(new_notepad_root)
        try:
            # Try a theme that might look better on the specific OS
            if new_notepad_root.tk.call('tk', 'windowingsystem') == 'win32':
                style.theme_use('vista') # Or 'xpnative'
            elif new_notepad_root.tk.call('tk', 'windowingsystem') == 'aqua':
                style.theme_use('aqua') # macOS
            else:
                style.theme_use('clam') # A reasonable default for Linux/others
        except tk.TclError:
            style.theme_use("default") # Fallback

        # Create a new Notepad instance associated with the new root.
        # No initial_file is passed, so it will be a blank editor.
        Notepad(new_notepad_root)
        # The main application's root.mainloop() will handle this new window's events.
        # Do not call new_notepad_root.mainloop() here.

    def _load_file(self, file_path):
        """Loads the content of the specified file into the text area."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
                self.current_file = file_path
                # Update title to include filename only
                filename = os.path.basename(file_path)
                self.root.title(f"Notething - {filename}")
                status_text = f"Status: Opened {file_path}"
                self.status_bar.config(text=status_text)
                self.tooltip.set_text(status_text)
                self._update_line_colors()
                
                # Add to recent files list
                self._add_to_recent_files(file_path)
        except FileNotFoundError:
             messagebox.showerror("Error Opening File", f"File not found:\n{file_path}")
             self.new_file()
             self.root.title("Notething")
        except Exception as e:
            messagebox.showerror("Error Opening File", f"Could not open file:\n{e}")
            self.new_file()
            self.root.title("Notething")

    def open_file(self):
        """Open a file for editing"""
        # Show the file dialog with "All Files" as the default option
        filepath = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All Files", "*.*"),  # This is now first, so it's the default
                ("Text Files", "*.txt"),
                ("Python Files", "*.py;*.pyw"),
                ("Markdown Files", "*.md"),
                ("HTML Files", "*.html;*.htm")
            ]
        )
        
        if filepath:  # If a file was selected (not canceled)
            self._load_file(filepath)

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
        self.text_area.tag_remove("maroon_line", "1.0", tk.END)
        self.text_area.tag_remove("bold_line", "1.0", tk.END)
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
            elif stripped_line.startswith("M "): # Check for M fourth
                self.text_area.tag_add("maroon_line", line_start, line_end) #Apply MAROON tag
            elif stripped_line.startswith("# ") or stripped_line.startswith("## ") or stripped_line.startswith("### "): # Check for headings
                self.text_area.tag_add("bold_line", line_start, line_end) # Apply HEADING tag
            else:
                # Apply normal color tag if none of the conditions are met
                self.text_area.tag_add("normal_line", line_start, line_end)

    def _update_line_colors_event(self, event=None):
        """Callback for KeyRelease event to update line colors."""
        # Optional: Add checks here if needed (e.g., ignore certain keys)
        self._update_line_colors()
    # --- End new method ---

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
            
            self._update_line_colors()
    # --- End method to prompt for date ---

    # --- Methods to Open Find/Replace Dialog ---
    def _launch_find_replace_dialog(self, replace_mode=False):
        if self.find_dialog is not None:
            try:
                # If window exists but was closed/destroyed, this will raise TclError
                self.find_dialog.lift()
                # If it's already a replace dialog but user wants find, or vice-versa,
                # maybe recreate it? For now, just lift existing.
                # A better approach might be a single dialog that shows/hides replace widgets.
                return # Already open
            except tk.TclError:
                self.find_dialog = None # It was destroyed, clear reference

        self.find_dialog = FindReplaceDialog(self.root, self.text_area, replace_mode=replace_mode)

        # Pre-fill with last search values
        self.find_dialog.find_what_var.set(self.last_find_text)
        if replace_mode:
            self.find_dialog.replace_with_var.set(self.last_replace_text)
        self.find_dialog.match_case_var.set(self.last_match_case)

        # Set focus correctly
        if replace_mode and self.last_find_text:
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
             # --- Remove search highlight when dialog closes ---
             try:
                 self.text_area.tag_remove("search_highlight", "1.0", tk.END)
             except tk.TclError:
                 pass # Ignore error if text_area is already gone
             # ---

             # Save last values before clearing the reference
             try:
                  self.last_find_text = self.find_dialog.find_what_var.get()
                  if hasattr(self.find_dialog, 'replace_with_var'):
                       self.last_replace_text = self.find_dialog.replace_with_var.get()
                  self.last_match_case = self.find_dialog.match_case_var.get()
             except tk.TclError:
                  pass
             finally:
                  self.find_dialog = None # Clear the reference
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
            self._update_line_colors() # Update colors if a line prefix changes
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
            # self._update_line_colors()
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
                self._update_line_colors()
        finally:
            self.text_area.config(autoseparators=original_autoseparators)

        return "break"

    def _handle_shift_tab_key(self, event=None):
        """Handles Shift+Tab key press for outdenting."""
        try:
            sel_first_idx = self.text_area.index(tk.SEL_FIRST)
            sel_last_idx = self.text_area.index(tk.SEL_LAST)
        except tk.TclError: # No selection
            # No standard behavior for Shift-Tab without selection in simple editors
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
                if self.text_area.get(f"{i}.0", f"{i}.1") == "\t":
                    self.text_area.delete(f"{i}.0", f"{i}.1")
                    current_shift = -1
                    modified_count +=1
                # Add elif for spaces if needed:
                # elif self.text_area.get(f"{i}.0", f"{i}.4") == "    ":
                #     self.text_area.delete(f"{i}.0", f"{i}.4")
                #     current_shift = -4
                #     modified_count += 1
                
                if i == first_line_num:
                    sel_first_line_char_shift = current_shift
                if i == last_line_num_sel: # If the line where selection ends was outdented
                    sel_last_line_char_shift = current_shift
            
            if modified_count > 0:
                self.text_area.edit_separator()
                self.text_area.tag_remove(tk.SEL, "1.0", tk.END)

                adj_sel_first_char_idx = max(0, int(sel_first_idx.split('.')[1]) + sel_first_line_char_shift)
                adj_sel_first = f"{first_line_num}.{adj_sel_first_char_idx}"
                
                adj_sel_last_char_idx = max(0, last_char_num_sel + sel_last_line_char_shift)
                adj_sel_last = f"{last_line_num_sel}.{adj_sel_last_char_idx}"
                
                # Ensure selection direction is maintained (start <= end)
                if self.text_area.compare(adj_sel_first, ">", adj_sel_last):
                    adj_sel_last = adj_sel_first # Collapse selection if it inverted

                self.text_area.tag_add(tk.SEL, adj_sel_first, adj_sel_last)
                self.text_area.mark_set(tk.INSERT, adj_sel_last)
                self._update_line_colors()
        finally:
            self.text_area.config(autoseparators=original_autoseparators)
        
        return "break"
    # --- End Tab/Shift-Tab Handlers ---

    # --- Add Enter Key Handler for Auto-Indentation ---
    def _handle_enter_key(self, event=None):
        """Handles Enter key press for auto-indentation."""
        current_cursor_pos = self.text_area.index(tk.INSERT)
        current_line_start_idx = self.text_area.index(f"{current_cursor_pos} linestart")
        current_line_end_idx = self.text_area.index(f"{current_cursor_pos} lineend")
        current_line_content = self.text_area.get(current_line_start_idx, current_line_end_idx)

        leading_whitespace = ""
        for char in current_line_content:
            if char.isspace(): # Catches spaces, tabs, etc.
                leading_whitespace += char
            else:
                break

        text_before_cursor_on_line = self.text_area.get(current_line_start_idx, current_cursor_pos)

        original_autoseparators = self.text_area.cget("autoseparators")
        self.text_area.config(autoseparators=False)
        
        try:
            # Scenario 1: Pressing Enter on a line that *only* contains whitespace,
            # and the cursor is at the end of this whitespace.
            if current_line_content.strip() == "" and text_before_cursor_on_line == current_line_content:
                self.text_area.delete(current_line_start_idx, current_line_end_idx)
                self.text_area.insert(current_line_start_idx, "\n") # Cursor moves to next line, col 0
                self.text_area.edit_separator()
            else:
                # Scenario 2: Auto-indent new line, potentially splitting the current line.
                # Text after the cursor on the current line.
                suffix = self.text_area.get(current_cursor_pos, current_line_end_idx)
                
                # Delete the suffix from the current line.
                self.text_area.delete(current_cursor_pos, current_line_end_idx)
                
                # Insert newline, the indent, and then the suffix.
                self.text_area.insert(current_cursor_pos, "\n" + leading_whitespace + suffix)
                self.text_area.edit_separator()
        finally:
            self.text_area.config(autoseparators=original_autoseparators)

        self._update_line_colors()
        return "break" # Prevent default Tkinter Enter behavior
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
        # Here you could add logic to check for unsaved changes before closing.
        # For now, just destroy the window.
        # Notepad.open_window_count -= 1 # Decrementing can be complex if windows close out of order
                                        # and we want to reuse cascade slots.
                                        # If open_window_count reaches 0, reset first_window_x/y
                                        # so the next new window (if app is kept running) re-centers.
        # A simpler approach for now: The mainloop exits when the last Tk root is destroyed.
        # The cascading will just continue from the initial point.
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
        # Existing key bindings...
        
        # Add bindings for Ctrl+Home and Ctrl+End navigation
        self.text_area.bind("<Control-Home>", self._handle_ctrl_home)
        self.text_area.bind("<Control-End>", self._handle_ctrl_end)
        
        # Also handle the shift variants for selection
        self.text_area.bind("<Control-Shift-Home>", self._handle_ctrl_home)
        self.text_area.bind("<Control-Shift-End>", self._handle_ctrl_end)
        
        # ...other bindings

    def _handle_ctrl_home(self, event=None):
        """Handle Ctrl+Home to move to the beginning of the document."""
        current_pos = self.text_area.index(tk.INSERT)
        
        # If Shift is pressed, extend the selection
        if event.state & 0x1:  # 0x1 is the Shift modifier
            try:
                # If there's already a selection, maintain its end
                sel_end = self.text_area.index(tk.SEL_LAST)
                self.text_area.tag_add(tk.SEL, "1.0", sel_end)
            except tk.TclError:
                # If no selection, create one from current pos to start
                self.text_area.tag_add(tk.SEL, "1.0", current_pos)
        
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