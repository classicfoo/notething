import tkinter as tk
from tkinter import ttk

class LineFormatter:
    def __init__(self, text_area, notepad):
        self.text_area = text_area
        self.notepad = notepad
        self._configure_tags()
        # Create the combined formatting handler
        self._update_all_formatting = self._create_combined_handler()
    
    def _configure_tags(self):
        self.text_area.tag_configure("green_line", foreground="green")
        self.text_area.tag_configure("blue_line", foreground="blue")
        self.text_area.tag_configure("grey_line", foreground="grey")
        self.text_area.tag_configure("normal_line", foreground="black")
        self.text_area.tag_configure("maroon_line", foreground="maroon")
        # Make sure self.notepad.bold_font exists, or use a default font
        self.text_area.tag_configure("bold_line", font=getattr(self.notepad, "bold_font", None))

    def _capitalize_first_word(self, line):
        """Capitalize the first word in a line, respecting indentation."""
        # Find the first non-whitespace character
        first_non_space = 0
        for i, char in enumerate(line):
            if not char.isspace():
                first_non_space = i
                break
        
        # If line is empty or only whitespace, return as is
        if first_non_space == len(line):
            return line
            
        # Split into indentation and content
        indentation = line[:first_non_space]
        content = line[first_non_space:]
        
        # Capitalize first word
        words = content.split(' ', 1)
        if len(words) > 0:
            first_word = words[0].capitalize()
            if len(words) > 1:
                return indentation + first_word + ' ' + words[1]
            return indentation + first_word
        return line

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

    def _create_combined_handler(self):
        """Create a combined handler for line formatting and URL detection."""
        def _update_all_formatting(event=None):
            self._update_line_formatting()
            # Instead of calling notepad._detect_urls directly, we'll use a callback
            if hasattr(self.notepad, '_detect_urls'):
                self.notepad._detect_urls()
        return _update_all_formatting

    def _update_line_formatting(self, event=None):
        """Update the formatting of all lines in the text area."""
        if not self.notepad.line_formatting_enabled:
            # Remove all formatting when disabled
            self.text_area.tag_remove("green_line", "1.0", tk.END)
            self.text_area.tag_remove("blue_line", "1.0", tk.END)
            self.text_area.tag_remove("grey_line", "1.0", tk.END)
            self.text_area.tag_remove("maroon_line", "1.0", tk.END)
            self.text_area.tag_remove("bold_line", "1.0", tk.END)
            self.text_area.tag_remove("normal_line", "1.0", tk.END)
            return

        # Store current cursor position and selection
        current_cursor = self.text_area.index(tk.INSERT)
        try:
            selection_start = self.text_area.index(tk.SEL_FIRST)
            selection_end = self.text_area.index(tk.SEL_LAST)
            has_selection = True
        except tk.TclError:
            has_selection = False

        # Remove existing tags first to reset colors
        self.text_area.tag_remove("green_line", "1.0", tk.END)
        self.text_area.tag_remove("blue_line", "1.0", tk.END)
        self.text_area.tag_remove("grey_line", "1.0", tk.END)
        self.text_area.tag_remove("maroon_line", "1.0", tk.END)
        self.text_area.tag_remove("bold_line", "1.0", tk.END)
        self.text_area.tag_remove("normal_line", "1.0", tk.END)

        # Process all lines
        content = self.text_area.get("1.0", tk.END)
        lines = content.split('\n')
        modified = False
        
        for i, line in enumerate(lines):
            # Get line number (1-based)
            line_num = i + 1
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            
            # Get stripped line for prefix checking
            stripped_line = line.lstrip()
            
            # Format the line
            formatted_line = line
            
            # Auto-capitalize first word if enabled
            if self.notepad.auto_capitalize_first_word:
                formatted_line = self._capitalize_first_word(formatted_line)
                
            # Format headings if enabled
            if stripped_line.startswith('#') and self.notepad.auto_capitalize_headings:
                formatted_line = self._format_heading_line(formatted_line)
                
            # Apply formatting if line changed
            if formatted_line != line:
                modified = True
                self.text_area.delete(line_start, line_end)
                self.text_area.insert(line_start, formatted_line)
                
            # Apply bold tag for headings
            if stripped_line.startswith('#'):
                self.text_area.tag_add("bold_line", line_start, line_end)
                
            # Apply color formatting based on line prefix
            if stripped_line.startswith('T '):
                self.text_area.tag_add("blue_line", line_start, line_end)
            elif stripped_line.startswith('N '):
                self.text_area.tag_add("green_line", line_start, line_end)
            elif stripped_line.startswith('X ') or stripped_line.startswith('C '):
                self.text_area.tag_add("grey_line", line_start, line_end)
            elif stripped_line.startswith('M '):
                self.text_area.tag_add("maroon_line", line_start, line_end)
            else:
                self.text_area.tag_add("normal_line", line_start, line_end)

        # Restore cursor position and selection if they existed
        self.text_area.mark_set(tk.INSERT, current_cursor)
        if has_selection:
            self.text_area.tag_add(tk.SEL, selection_start, selection_end)

    def _update_line_formatting_event(self, event=None):
        """Handle line formatting after key events."""
        # Get the current line
        current_line = self.text_area.get("insert linestart", "insert lineend")
        
        # Only process if the line starts with a heading marker AND auto-capitalize is enabled
        if current_line.startswith('#') and self.notepad.auto_capitalize_headings:
            # Store cursor position
            cursor_pos = self.text_area.index(tk.INSERT)
            
            # Format the line
            formatted_line = self._format_heading_line(current_line)
            if formatted_line != current_line:
                # Replace the line content
                self.text_area.delete("insert linestart", "insert lineend")
                self.text_area.insert("insert linestart", formatted_line)
                
                # Restore cursor position
                self.text_area.mark_set(tk.INSERT, cursor_pos)
        
        # Continue with regular line formatting
        self._update_line_formatting()