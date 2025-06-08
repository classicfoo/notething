import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkcalendar import Calendar
from ui.mixins import CenterDialogMixin

# --- Calendar Dialog Class (using tkcalendar) ---
class CalendarDialog(tk.Toplevel, CenterDialogMixin):
    def __init__(self, master):
        super().__init__(master)
        
        self.transient(master)
        self.title("Select Date")
        self.result_date = None

        # Get current date for initial display
        now = datetime.now()

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Create the Calendar widget
        self.cal = Calendar(main_frame,
                            selectmode='day',
                            year=now.year,
                            month=now.month,
                            day=now.day,
                            date_pattern='dd/mm/yyyy')
        self.cal.pack(pady=10, padx=10, fill="both", expand=True)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(5,0), fill=tk.X)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ok_button = ttk.Button(button_frame, text="OK", command=self._on_ok, width=12)
        ok_button.pack(side=tk.LEFT, padx=(0,5), expand=True, fill=tk.X)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._on_cancel, width=12)
        cancel_button.pack(side=tk.RIGHT, padx=(5,0), expand=True, fill=tk.X)

        self.resizable(False, False)
        self.bind("<Escape>", lambda e: self._on_cancel())
        self.bind("<Return>", lambda e: self._on_ok())
        self.cal.bind("<Return>", lambda e: self._on_ok())
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Center the dialog
        self.center_dialog()
        
        self.grab_set()
        self.focus_set()
        self.cal.focus_set()

        # Arrow key navigation for calendar (robust date handling, no debug)
        def move_selection(days):
            cur = self.cal.selection_get()
            import datetime
            if cur:
                try:
                    # Ensure cur is a datetime.date
                    if isinstance(cur, datetime.datetime):
                        cur = cur.date()
                    elif not isinstance(cur, datetime.date):
                        cur = datetime.datetime.strptime(str(cur), "%Y-%m-%d").date()
                    new_date = cur + datetime.timedelta(days=days)
                    self.cal.selection_clear()
                    self.cal.selection_set(new_date)
                    self.cal.see(new_date)
                except Exception:
                    pass
        self.cal.bind('<Left>', lambda e: move_selection(-1))
        self.cal.bind('<Right>', lambda e: move_selection(1))
        self.cal.bind('<Up>', lambda e: move_selection(-7))
        self.cal.bind('<Down>', lambda e: move_selection(7))
        self.cal.focus_set()

        # Unbind on close
        def unbind_arrows():
            self.unbind_all('<Left>')
            self.unbind_all('<Right>')
            self.unbind_all('<Up>')
            self.unbind_all('<Down>')
        self.protocol("WM_DELETE_WINDOW", lambda: (unbind_arrows(), self._on_cancel()))
        self.bind("<Escape>", lambda e: (unbind_arrows(), self._on_cancel()))
        self.bind("<Return>", lambda e: (unbind_arrows(), self._on_ok()))
        # Also unbind in _on_ok and _on_cancel
        old_on_ok = self._on_ok
        def new_on_ok(*args, **kwargs):
            unbind_arrows()
            return old_on_ok(*args, **kwargs)
        self._on_ok = new_on_ok
        old_on_cancel = self._on_cancel
        def new_on_cancel(*args, **kwargs):
            unbind_arrows()
            return old_on_cancel(*args, **kwargs)
        self._on_cancel = new_on_cancel

    def _on_ok(self):
        self.result_date = self.cal.selection_get() # Returns a datetime.date object
        self.destroy()

    def _on_cancel(self):
        self.result_date = None
        self.destroy()
# --- End Calendar Dialog Class ---
