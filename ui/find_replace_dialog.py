import tkinter as tk
from tkinter import ttk, messagebox
import time
from ui.mixins import CenterDialogMixin
from ui.tooltip import Tooltip

# --- Find/Replace Dialog Class ---
class FindReplaceDialog(tk.Toplevel, CenterDialogMixin):
    def __init__(self, master, text_widget, replace_mode=False):
        # Store references before creating the dialog
        self.text_widget = text_widget
        self.master = master
        
        # Create the dialog
        super().__init__(master)
        
        # Configure dialog
        self.title("Find" if not replace_mode else "Find and Replace")
        self.transient(master)
        self.resizable(False, False)

        # Initialize variables with explicit parent
        self.find_what_var = tk.StringVar(self)
        self.replace_with_var = tk.StringVar(self)
        self.match_case_var = tk.BooleanVar(self, value=False)  # Initialize with False
        self.find_in_selection_var = tk.BooleanVar(self, value=False)  # Initialize with False

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
        
        # Apply the preserved selection tag
        if has_selection:
            self.text_widget.tag_configure(self.preserved_sel_tag, 
                                          background="lightgrey", 
                                          foreground="black")
            self.text_widget.tag_add(self.preserved_sel_tag, 
                                    self.initial_sel_start, 
                                    self.initial_sel_end)

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
            
            # Add Swap button
            self.swap_btn = ttk.Button(entry_frame, text="⇅", width=3, command=self._swap_fields)
            self.swap_btn.grid(row=0, column=2, rowspan=2, padx=(5,0), pady=2, sticky='ns')
            # Add Return key binding for swap button
            self.swap_btn.bind("<Return>", lambda e: self._swap_fields())
            
            # Configure tooltip for swap button
            self.swap_tooltip = Tooltip(self.swap_btn)
            self.swap_tooltip.set_text("Swap Find/Replace text")

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
            # Add binding for Return key when Replace All button has focus
            self.replace_all_btn.bind("<Return>", lambda e: self.replace_all())

        # --- Initial Focus and Bindings ---
        self.find_entry.focus_set() # Start cursor in "Find what"
        self.protocol("WM_DELETE_WINDOW", self._cleanup_custom_tags_and_destroy) # Handle closing via 'X' button

        # Bind Enter key in find entry to Find Next
        self.find_entry.bind("<Return>", lambda event: self.find_next())
        if replace_mode:
            self.replace_entry.bind("<Return>", lambda event: self.replace_all())
            # Set focus to Replace All button after a brief delay
            self.after(100, lambda: self.replace_all_btn.focus_set())

        # --- Bind Escape key to close the dialog ---
        self.bind("<Escape>", lambda event: self._cleanup_custom_tags_and_destroy())
        # --- End Escape Binding ---

        # Store last search position
        self.last_pos = "1.0"

        # Set "Find in selection" checkbox if there's a preserved selection
        if has_selection:
            self.find_in_selection_var.set(True)
        
        # Center the dialog
        self.center_dialog()
        
        # Set focus and make modal
        self.grab_set()
        self.focus_set()
        self.find_entry.focus_set()

    def _cleanup_custom_tags_and_destroy(self, event=None):
        """Clean up tags and then destroy the dialog"""
        self._cleanup_custom_tags()
        self.destroy()

    def _cleanup_custom_tags(self, event=None):
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
        """Replace all occurrences of the find term with the replace term."""
        find_term = self.find_what_var.get()
        replace_term = self.replace_with_var.get()
        
        if not find_term:
            messagebox.showwarning("Replace All", "Please enter text to find.", parent=self)
            return
        
        # Determine search boundaries
        if self.find_in_selection_var.get():
            if self.initial_sel_start and self.initial_sel_end:
                start_pos = self.initial_sel_start
                stop_pos = self.initial_sel_end
            else:
                messagebox.showwarning("Replace All", "No text selected.", parent=self)
                return
        else:
            start_pos = "1.0"
            stop_pos = tk.END
        
        # Remove any existing highlight
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        
        # Turn off auto separators to make it a single undo operation
        original_autoseparators = self.text_widget.cget("autoseparators")
        self.text_widget.config(autoseparators=False)
        
        count = 0
        current_pos = start_pos
        nocase = not self.match_case_var.get()
        
        try:
            # Loop through and replace all occurrences
            while True:
                found_pos = self.text_widget.search(find_term, current_pos, stopindex=stop_pos, nocase=nocase)
                if not found_pos:
                    break
                
                # Calculate the end position of the found text
                end_pos = f"{found_pos}+{len(find_term)}c"
                
                # Replace this occurrence
                self.text_widget.delete(found_pos, end_pos)
                self.text_widget.insert(found_pos, replace_term)
                
                # Update current position for next search
                # Important: account for the different lengths of find and replace terms
                current_pos = f"{found_pos}+{len(replace_term)}c"
                
                # Update stop position if we're searching in selection
                # This is needed because the replacement might change text positions
                if self.find_in_selection_var.get():
                    # Adjust the end boundary by the difference in length between find and replace terms
                    length_diff = len(replace_term) - len(find_term)
                    if length_diff != 0:
                        # Get current line and char position of stop_pos
                        line, char = map(int, self.text_widget.index(stop_pos).split('.'))
                        # Adjust the character position
                        char += length_diff
                        # Update stop_pos
                        stop_pos = f"{line}.{char}"
                
                count += 1
            
            # Create a single undo entry for all replacements
            if count > 0:
                self.text_widget.edit_separator()
                
            # Show result message
            if count > 0:
                messagebox.showinfo("Replace All", f"Replaced {count} occurrence(s).", parent=self)
                # Update line colors if needed
                if hasattr(self.master, '_update_line_colors'):
                    self.master._update_line_colors()
            else:
                messagebox.showinfo("Replace All", f"Cannot find '{find_term}'", parent=self)
                
        finally:
            # Restore auto separators
            self.text_widget.config(autoseparators=original_autoseparators)

    def _swap_fields(self):
        """Swap the contents of find and replace fields."""
        find_text = self.find_what_var.get()
        replace_text = self.replace_with_var.get()
        
        self.find_what_var.set(replace_text)
        self.replace_with_var.set(find_text)
        
        # Set focus to find field after swap
        self.find_entry.focus_set()

# --- End Find/Replace Dialog Class ---
