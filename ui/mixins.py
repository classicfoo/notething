# Add this class before the other dialog classes
class CenterDialogMixin:
    """Mixin class to center dialogs on screen."""
    def center_dialog(self):
        """Centers the dialog on screen."""
        # Hide the window initially until we position it correctly
        self.withdraw()
        
        # Update window size calculations
        self.update_idletasks()
        
        # Get window and screen dimensions
        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set position and show window
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.deiconify()