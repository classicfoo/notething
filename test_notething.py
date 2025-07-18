import unittest
from unittest.mock import patch, MagicMock
import os
import tkinter as tk
from tkinterdnd2 import TkinterDnD
from notething import Notepad

class TestNotepad(unittest.TestCase):
    def setUp(self):
        self.root = TkinterDnD.Tk()
        self.root.withdraw() # Hide window during tests
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
        text = r'Here is the document: "C:\My Documents\report final.docx"'
        expected = [r'"C:\My Documents\report final.docx"']
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
        text = r'My site is www.mysite.com and my file is "C:\Users\My Stuff\doc.txt".'
        expected = ["www.mysite.com", r'"C:\Users\My Stuff\doc.txt"' ]
        self.run_test_on_text(text, expected)

    def test_url_and_path_together(self):
        text = r'Link: http://a.com/b.txt and path: C:\a\b.txt'
        expected = ["http://a.com/b.txt", r"C:\a\b.txt"]
        self.run_test_on_text(text, expected)

    def test_path_with_trailing_period(self):
        self.run_test_on_text(r"The file is C:\folder\file.txt.", [r"C:\folder\file.txt"])

    def test_do_not_detect_quoted_non_paths(self):
        self.run_test_on_text('He said "hello world" and left.', [])

if __name__ == '__main__':
    unittest.main()