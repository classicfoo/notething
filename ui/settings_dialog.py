import tkinter as tk
from tkinter import ttk
from ui.mixins import CenterDialogMixin


# Add this after the other dialog classes
class SettingsDialog(tk.Toplevel, CenterDialogMixin):
    def __init__(self, master, notepad):
        super().__init__(master)
        self.notepad = notepad
        self.title("Settings")
        self.transient(master)
        self.resizable(False, False)

        # --- Initialize all variables at the top ---
        self.reopen_last_var = tk.BooleanVar(self, value=bool(notepad.reopen_last_file))
        self.match_case_var = tk.BooleanVar(self, value=bool(notepad.last_match_case_setting))
        self.line_format_var = tk.BooleanVar(self, value=bool(notepad.line_formatting_enabled))
        self.auto_capitalize_var = tk.BooleanVar(self, value=bool(notepad.auto_capitalize_headings))
        self.auto_capitalize_first_word_var = tk.BooleanVar(self, value=bool(notepad.auto_capitalize_first_word))
        self.auto_capitalize_indented_var = tk.BooleanVar(self, value=bool(notepad.auto_capitalize_indented))
        self.highlight_enabled_var = tk.BooleanVar(self, value=bool(notepad.highlight_enabled))
        self.auto_full_stop_var = tk.BooleanVar(self, value=bool(notepad.auto_full_stop))
        self.readonly_mode_var = tk.BooleanVar(self, value=bool(notepad.readonly_mode))
        self.default_find_text_var = tk.StringVar(self, value=notepad.default_find_text)
        self.default_replace_text_var = tk.StringVar(self, value=notepad.default_replace_text)

        # --- Make dialog scrollable ---
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(content_frame, borderwidth=0, highlightthickness=0, width=420)
        vscroll = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        main_frame = ttk.Frame(canvas, padding="16 16 16 8")
        main_frame_id = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        main_frame.bind("<Configure>", _on_frame_configure)

        def _on_canvas_configure(event):
            canvas.itemconfig(main_frame_id, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mousewheel scrolling (bind_all for dialog lifetime)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.bind_all("<MouseWheel>", _on_mousewheel)
        # Unbind on close
        def unbind_mousewheel():
            self.unbind_all("<MouseWheel>")
        self.protocol("WM_DELETE_WINDOW", lambda: (unbind_mousewheel(), self._on_cancel()))
        self.bind("<Escape>", lambda e: (unbind_mousewheel(), self._on_cancel()))
        self.bind("<Return>", lambda e: (unbind_mousewheel(), self._on_ok()))
        # Also unbind in _on_ok and _on_cancel
        old_on_ok = self._on_ok
        def new_on_ok(*args, **kwargs):
            unbind_mousewheel()
            return old_on_ok(*args, **kwargs)
        self._on_ok = new_on_ok
        old_on_cancel = self._on_cancel
        def new_on_cancel(*args, **kwargs):
            unbind_mousewheel()
            return old_on_cancel(*args, **kwargs)
        self._on_cancel = new_on_cancel

        # Section style
        section_font = ("TkDefaultFont", 10, "bold")

        # Startup Settings
        startup_frame = ttk.LabelFrame(main_frame, text="Startup", padding="8")
        startup_frame.pack(fill=tk.X, pady=(0, 12))
        startup_frame.configure(labelwidget=ttk.Label(startup_frame, text="Startup", font=section_font))
        reopen_check = ttk.Checkbutton(
            startup_frame, 
            text="Reopen last file on startup",
            variable=self.reopen_last_var,
            command=lambda: self._update_checkbox_state(self.reopen_last_var)
        )
        reopen_check.pack(anchor='w', pady=(0, 2))

        # Search Settings
        search_frame = ttk.LabelFrame(main_frame, text="Search", padding="8")
        search_frame.pack(fill=tk.X, pady=(0, 12))
        search_frame.configure(labelwidget=ttk.Label(search_frame, text="Search", font=section_font))
        match_case_check = ttk.Checkbutton(
            search_frame,
            text="Match case by default",
            variable=self.match_case_var,
            command=lambda: self._update_checkbox_state(self.match_case_var)
        )
        match_case_check.pack(anchor='w', pady=(0, 2))
        ttk.Label(search_frame, text="Default Find text:").pack(anchor='w', padx=2, pady=(6,0))
        self.default_find_text_var = tk.StringVar(self, value=notepad.default_find_text)
        default_find_entry = ttk.Entry(search_frame, textvariable=self.default_find_text_var, width=20)
        default_find_entry.pack(anchor='w', padx=2, pady=(0,4))
        ttk.Label(search_frame, text="Default Replace text:").pack(anchor='w', padx=2, pady=(6,0))
        self.default_replace_text_var = tk.StringVar(self, value=notepad.default_replace_text)
        default_replace_entry = ttk.Entry(search_frame, textvariable=self.default_replace_text_var, width=20)
        default_replace_entry.pack(anchor='w', padx=2, pady=(0,2))

        # Dynamic Line Formatting
        format_frame = ttk.LabelFrame(main_frame, text="Dynamic Line Formatting", padding="8")
        format_frame.pack(fill=tk.X, pady=(0, 12))
        format_frame.configure(labelwidget=ttk.Label(format_frame, text="Dynamic Line Formatting", font=section_font))
        format_check = ttk.Checkbutton(
            format_frame,
            text="Enable dynamic line formatting",
            variable=self.line_format_var,
            command=lambda: self._update_checkbox_state(self.line_format_var)
        )
        format_check.pack(anchor='w', pady=(0, 2))

        # Heading Settings
        heading_frame = ttk.LabelFrame(main_frame, text="Heading Settings", padding="8")
        heading_frame.pack(fill=tk.X, pady=(0, 12))
        heading_frame.configure(labelwidget=ttk.Label(heading_frame, text="Heading Settings", font=section_font))
        capitalize_check = ttk.Checkbutton(
            heading_frame,
            text="Auto-capitalize heading words",
            variable=self.auto_capitalize_var,
            command=lambda: self._update_checkbox_state(self.auto_capitalize_var)
        )
        capitalize_check.pack(anchor='w', pady=(0, 2))

        # Text Formatting
        text_format_frame = ttk.LabelFrame(main_frame, text="Text Formatting", padding="8")
        text_format_frame.pack(fill=tk.X, pady=(0, 12))
        text_format_frame.configure(labelwidget=ttk.Label(text_format_frame, text="Text Formatting", font=section_font))
        capitalize_first_word_check = ttk.Checkbutton(
            text_format_frame,
            text="Auto-capitalize first word in lines",
            variable=self.auto_capitalize_first_word_var,
            command=lambda: self._update_checkbox_state(self.auto_capitalize_first_word_var)
        )
        capitalize_first_word_check.pack(anchor='w', pady=(0, 2))
        capitalize_indented_check = ttk.Checkbutton(
            text_format_frame,
            text="Include indented lines in auto-capitalization",
            variable=self.auto_capitalize_indented_var,
            command=lambda: self._update_checkbox_state(self.auto_capitalize_indented_var)
        )
        capitalize_indented_check.pack(anchor='w', pady=(0, 2))
        auto_full_stop_check = ttk.Checkbutton(
            text_format_frame,
            text="Auto-add full stop at end of line on Enter",
            variable=self.auto_full_stop_var,
            command=lambda: self._update_checkbox_state(self.auto_full_stop_var)
        )
        auto_full_stop_check.pack(anchor='w', pady=(0, 2))
        readonly_mode_check = ttk.Checkbutton(
            text_format_frame,
            text="Read-only mode (requires Save As for readonly files)",
            variable=self.readonly_mode_var,
            command=lambda: self._update_checkbox_state(self.readonly_mode_var)
        )
        readonly_mode_check.pack(anchor='w', pady=(0, 2))

        # Highlighting Settings
        highlight_frame = ttk.LabelFrame(main_frame, text="Highlighting", padding="8")
        highlight_frame.pack(fill=tk.X, pady=(0, 12))
        highlight_frame.configure(labelwidget=ttk.Label(highlight_frame, text="Highlighting", font=section_font))
        highlight_check = ttk.Checkbutton(
            highlight_frame,
            text="Enable highlighting (Ctrl+Shift+H)",
            variable=self.highlight_enabled_var,
            command=lambda: self._update_checkbox_state(self.highlight_enabled_var)
        )
        highlight_check.pack(anchor='w', pady=(0, 2))

        # --- OK/Cancel Buttons at bottom right ---
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, anchor="e", pady=(0, 8), padx=16)
        ok_button = ttk.Button(button_frame, text="OK", command=self._on_ok, width=10)
        ok_button.pack(side=tk.RIGHT, padx=(5, 0))
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._on_cancel, width=10)
        cancel_button.pack(side=tk.RIGHT)

        # Bindings
        self.bind("<Escape>", lambda e: self._on_cancel())
        self.bind("<Return>", lambda e: self._on_ok())
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Center and make modal
        self.center_dialog()
        self.grab_set()
        self.focus_set()

    def _update_checkbox_state(self, var):
        """Ensure checkbox state is properly updated"""
        # Force the variable to be a proper boolean
        var.set(bool(var.get()))

    def _on_ok(self):
        # Save settings using boolean values
        self.notepad.reopen_last_file = bool(self.reopen_last_var.get())
        self.notepad.last_match_case_setting = bool(self.match_case_var.get())
        self.notepad.line_formatting_enabled = bool(self.line_format_var.get())
        self.notepad.auto_capitalize_headings = bool(self.auto_capitalize_var.get())
        self.notepad.auto_capitalize_first_word = bool(self.auto_capitalize_first_word_var.get())
        self.notepad.auto_capitalize_indented = bool(self.auto_capitalize_indented_var.get())
        self.notepad.highlight_enabled = bool(self.highlight_enabled_var.get())
        self.notepad.auto_full_stop = bool(self.auto_full_stop_var.get())
        self.notepad.readonly_mode = bool(self.readonly_mode_var.get())
        self.notepad.default_find_text = self.default_find_text_var.get()
        self.notepad.default_replace_text = self.default_replace_text_var.get()
        self.notepad._save_settings()
        # Apply formatting changes immediately
        self.notepad._update_line_formatting()
        self.destroy()

    def _on_cancel(self):
        self.destroy()
