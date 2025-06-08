import tkinter as tk

class HighlightingManager:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self._setup_highlight_tags()
        self._setup_bindings()

    def _setup_highlight_tags(self):
        """Configure the highlight-related tags."""
        self.text_widget.tag_configure("highlight", background="yellow")
        self.text_widget.tag_configure("highlight_selected", background="#E9E969")  # Grey-yellow for overlap
        self.text_widget.tag_configure(tk.SEL, background="lightgrey", foreground="black")

        # Set tag priorities (lower ones show through)
        self.text_widget.tag_lower("highlight")  # Bottom layer
        self.text_widget.tag_raise("highlight_selected", "highlight")  # Middle layer
        self.text_widget.tag_raise(tk.SEL, "highlight")  # Top layer

    def _setup_bindings(self):
        """Set up the highlight-related bindings."""
        self.text_widget.bind('<<Selection>>', self._update_highlight_selection)
        self.text_widget.bind('<ButtonRelease-1>', self._update_highlight_selection)

    def handle_highlight(self, event=None):
        """Handle Ctrl+Shift+H key press for highlighting."""
        try:
            # Check if there's a selection
            sel_start = self.text_widget.index(tk.SEL_FIRST)
            sel_end = self.text_widget.index(tk.SEL_LAST)
            
            # Get all ranges with highlight tag within selection
            ranges = self.text_widget.tag_ranges("highlight")
            has_highlight = False
            
            # Check if any part of the selection is already highlighted
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i + 1]
                if (self.text_widget.compare(start, ">=", sel_start) and 
                    self.text_widget.compare(end, "<=", sel_end)):
                    has_highlight = True
                    break
            
            if has_highlight:
                # Remove highlight from selection
                self.text_widget.tag_remove("highlight", sel_start, sel_end)
            else:
                # Add highlight to selection
                self.text_widget.tag_add("highlight", sel_start, sel_end)
                
        except tk.TclError:
            # No selection - handle single line
            cursor_pos = self.text_widget.index(tk.INSERT)
            line_start = self.text_widget.index(f"{cursor_pos} linestart")
            line_end = self.text_widget.index(f"{cursor_pos} lineend")
            
            # Check if line is already highlighted
            ranges = self.text_widget.tag_ranges("highlight")
            has_highlight = False
            
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i + 1]
                if (self.text_widget.compare(start, "==", line_start) and 
                    self.text_widget.compare(end, "==", line_end)):
                    has_highlight = True
                    break
            
            if has_highlight:
                # Remove highlight from line
                self.text_widget.tag_remove("highlight", line_start, line_end)
            else:
                # Add highlight to line
                self.text_widget.tag_add("highlight", line_start, line_end)
        
        return "break"

    def _update_highlight_selection(self, event=None):
        """Update the highlight_selected tag when selection changes"""
        try:
            sel_start = self.text_widget.index(tk.SEL_FIRST)
            sel_end = self.text_widget.index(tk.SEL_LAST)
            
            # Clear previous highlight_selected tags
            self.text_widget.tag_remove("highlight_selected", "1.0", tk.END)
            
            # Get all highlighted ranges
            ranges = self.text_widget.tag_ranges("highlight")
            
            # For each highlighted range, check overlap with selection
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i + 1]
                
                # If there's any overlap, apply highlight_selected tag
                if not (self.text_widget.compare(end, "<=", sel_start) or 
                       self.text_widget.compare(start, ">=", sel_end)):
                    # Calculate overlap region using text widget's compare method
                    if self.text_widget.compare(start, "<", sel_start):
                        overlap_start = sel_start
                    else:
                        overlap_start = start
                        
                    if self.text_widget.compare(end, ">", sel_end):
                        overlap_end = sel_end
                    else:
                        overlap_end = end
                        
                    self.text_widget.tag_add("highlight_selected", overlap_start, overlap_end)
        except tk.TclError:
            # No selection, remove all highlight_selected tags
            self.text_widget.tag_remove("highlight_selected", "1.0", tk.END)