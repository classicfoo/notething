import unittest
from unittest.mock import patch, MagicMock
import os
import tkinter as tk
from tkinterdnd2 import TkinterDnD
from notething import Notepad


class TestNotepad(unittest.TestCase):
    def setUp(self):
        self.root = TkinterDnD.Tk()
        self.root.withdraw()  # Hide window during tests
        self.app = Notepad(self.root)

    def tearDown(self):
        self.root.destroy()

    @patch('webbrowser.open')
    def test_open_url(self, mock_open):
        self.app._open_url_or_file('http://example.com')
        mock_open.assert_called_with('http://example.com')

    @patch('os.path.exists')
    @patch('os.startfile')
    def test_open_file_with_spaces(self, mock_startfile, mock_exists):
        mock_exists.return_value = True
        file_path = r'C:\Users\MichaelHuynh\Documents\_my_documents\work\ongoing\todo\collections\FW_ New online training for clients_ Australian Consumer Law.msg'
        self.app._open_url_or_file(file_path)
        mock_startfile.assert_called_with(file_path)

    @patch('os.path.exists')
    @patch('os.startfile')
    def test_open_file_with_quotes(self, mock_startfile, mock_exists):
        mock_exists.return_value = True
        file_path = r'"C:\Users\MichaelHuynh\Documents\_my_documents\work\ongoing\todo\collections\FW_ New online training for clients_ Australian Consumer Law.msg"'
        expected_path = file_path.strip('"')
        self.app._open_url_or_file(file_path)
        mock_startfile.assert_called_with(expected_path)

    @patch('os.path.exists')
    @patch('tkinter.messagebox.showinfo')
    def test_open_invalid_path(self, mock_showinfo, mock_exists):
        mock_exists.return_value = False
        self.app._open_url_or_file('invalid/path')
        mock_showinfo.assert_called_with('Error', 'Could not open: invalid/path')

    @patch('os.path.exists')
    @patch('notething.Notepad._open_in_notething')
    def test_open_text_file_in_notething(self, mock_open_in_notething, mock_exists):
        mock_exists.return_value = True
        file_path = 'test.txt'
        self.app._open_url_or_file(file_path)
        mock_open_in_notething.assert_called_with(file_path)


class TestFindDialogBehavior(unittest.TestCase):
    def setUp(self):
        self.root = TkinterDnD.Tk()
        self.root.withdraw()
        self.app = Notepad(self.root)

    def tearDown(self):
        if self.app.find_dialog is not None:
            try:
                self.app.find_dialog.destroy()
            except tk.TclError:
                pass
        self.root.destroy()

    def test_find_dialog_highlights_text(self):
        self.app.last_find_text = "sample"
        self.app.open_find_dialog()
        self.root.update()
        dialog = self.app.find_dialog
        self.root.update()
        selected = dialog.find_entry.selection_get()
        self.assertEqual(selected, "sample")

    def test_find_dialog_closes_on_focus_out(self):
        self.app.open_find_dialog()
        self.root.update()
        dialog = self.app.find_dialog
        self.app.text_area.focus_set()
        self.root.update()
        self.assertFalse(dialog.winfo_exists())


class TestDetectUrls(unittest.TestCase):
    def setUp(self):
        self.root = TkinterDnD.Tk()
        self.root.withdraw()  # Hide window during tests
        self.app = Notepad(self.root)
        self.text_area = self.app.text_area

    def tearDown(self):
        self.root.destroy()

    def get_hyperlinked_text(self):
        """Helper function to get all text segments tagged as 'hyperlink'."""
        ranges = self.text_area.tag_ranges("hyperlink")
        return sorted([self.text_area.get(start, end) for start, end in zip(ranges[::2], ranges[1::2])])

    def run_test_on_text(self, text, expected_links):
        """Helper to run detection and assert results."""
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", text)
        self.app._detect_urls()
        self.assertEqual(self.get_hyperlinked_text(), sorted(expected_links))

    def test_standard_url(self):
        self.run_test_on_text("Visit http://example.com for more.", ["http://example.com"])

    def test_www_url(self):
        self.run_test_on_text("Go to www.google.com.", ["www.google.com"])

    def test_windows_path_unquoted(self):
        self.run_test_on_text(r"File is at C:\Users\test.txt.", [r"C:\Users\test.txt"])

    def test_windows_path_with_spaces_quoted(self):
        text = r'Here is the document: "C:\\My Documents\\report final.docx"'
        expected = [r'"C:\\My Documents\\report final.docx"']
        self.run_test_on_text(text, expected)

    def test_unix_path_unquoted(self):
        self.run_test_on_text("Config at /etc/nginx/nginx.conf.", ["/etc/nginx/nginx.conf"])

    def test_unix_path_with_spaces_quoted(self):
        text = 'My project is in "/home/user/my project/main.py"'
        expected = ['"/home/user/my project/main.py"']
        self.run_test_on_text(text, expected)

    def test_no_links(self):
        self.run_test_on_text("This is just plain text.", [])

    def test_mixed_links(self):
        text = r'My site is www.mysite.com and my file is "C:\\Users\\My Stuff\\doc.txt".'
        expected = ["www.mysite.com", r'"C:\\Users\\My Stuff\\doc.txt"']
        self.run_test_on_text(text, expected)

    def test_url_and_path_together(self):
        text = r'Link: http://a.com/b.txt and path: C:\\a\\b.txt'
        expected = ["http://a.com/b.txt", r"C:\\a\\b.txt"]
        self.run_test_on_text(text, expected)

    def test_path_with_trailing_period(self):
        self.run_test_on_text(r"The file is C:\\folder\\file.txt.", [r"C:\\folder\\file.txt"])

    def test_do_not_detect_quoted_non_paths(self):
        self.run_test_on_text('He said "hello world" and left.', [])


class TestHyperlinkBinding(unittest.TestCase):
    def setUp(self):
        self.root = TkinterDnD.Tk()
        self.root.withdraw()
        self.app = Notepad(self.root)

    def tearDown(self):
        if self.app.find_dialog is not None:
            try:
                self.app.find_dialog.destroy()
            except tk.TclError:
                pass
        self.root.destroy()

    def test_hyperlink_binding_restored(self):
        self.app.text_area.insert("1.0", "http://example.com")
        self.app._detect_urls()
        before = self.app.text_area.tag_bind("hyperlink", "<Button-1>")
        self.assertTrue(before)

        self.app.open_find_dialog()
        self.root.update()
        during = self.app.text_area.tag_bind("hyperlink", "<Button-1>")
        self.assertFalse(during)

        self.app.find_dialog._cleanup_custom_tags_and_destroy()
        self.root.update()
        after = self.app.text_area.tag_bind("hyperlink", "<Button-1>")
        self.assertEqual(after, before)

    @patch('tkinter.messagebox.showwarning')
    def test_find_next_warning_does_not_close_dialog(self, mock_warn):
        self.app.text_area.insert("1.0", "http://example.com")
        self.app._detect_urls()
        self.app.open_find_dialog()
        self.root.update()
        dialog = self.app.find_dialog

        # Trigger find_next with empty search term to invoke showwarning
        dialog.find_what_var.set("")
        dialog.find_next()
        self.root.update()

        # Dialog should still exist and hyperlink binding remains disabled
        self.assertTrue(dialog.winfo_exists())
        self.assertFalse(self.app.text_area.tag_bind("hyperlink", "<Button-1>"))

        dialog._cleanup_custom_tags_and_destroy()
        self.root.update()

        self.assertTrue(self.app.text_area.tag_bind("hyperlink", "<Button-1>"))


if __name__ == '__main__':
    unittest.main()

