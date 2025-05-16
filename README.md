# Readme

## Features 
- F5 current time (Sydney)
- F6 Calendar
- Find Dialog (Ctrl + F)
- Find and Replace Dialog (Ctrl + H)
- Smart Home Key and Selection
N Pressing Shift + Home
	N First time - Selects until the end of first whitepsace characters
	N Second time - Selects until the beginning of the line

## Todo
X Find and Replace in selction checkbox
X Open Recent Files ... (Lists the last 5 files recently opened)
X Open dialog to be for all files by default (not just .txt files)
X Reopen last file on startup variable (for debugging purposes, bool value)
X After pressing F6, press enter to accept selected date on calendar picker

## Bugs
X tkcalendar doesn't open in centre of the screen straight away
X Find in seletion doesn't work
X Ctrl + Home is not working (should take user to beginning of file)
X After adding a date using F6 calendar, update line colour
X After making a selection, and pressing ctrl+home, it needs to cleanup custom tags to the text selection and just go to beginning of document
X Line colours don't update after find and replace: now updates after dialog is closed
X Find and replace in selection deletes existing newline
X Replace dialog looks broken: Increased dialog width to 400
X Replace all doesn't work
X When doing find and replace, it doesn't search from the beginning
X After replacing, it should automatically find the next instance (ready for replacing)
T Pressing enter a few time on line with heading doesn't work as expected
T Arrow keys doesn't move dates on calendar

T asdfasf 09:03 AM 17 May 2025 21 May 2025
T asdfasf
T asdfasf

# Study

## Preserving Visual Context with Custom Tags in Tkinter's Find/Replace Dialog

In Tkinter, when a dialog like Find/Replace is opened, it takes focus away from the main text widget. This triggers a default behaviour where the Text widget clears its selection highlighting, making it difficult for users to see what they had selected—a serious usability issue when performing actions like "Find in selection." To address this, we first disabled the automatic selection-clearing behaviour during widget initialisation. However, this alone wasn’t enough. We introduced custom tags to visually preserve and manage the user's selection while the dialog was open.

These custom tags served multiple purposes: they maintained visual feedback for users, clearly marked search boundaries, and supported layered visual states—such as showing both selected regions and search highlights simultaneously. Without proper cleanup, though, these tags could linger after the dialog closed, leading to confusing visual artifacts like leftover highlights or stacked tag effects. By carefully cleaning up tags when the dialog is dismissed, we preserved the clarity and usability of the editor. This solution highlights how working around Tkinter’s limitations with custom tags enables a cleaner, more intuitive user experience.

## Uncovering Hidden Behaviours: Debugging Ctrl+H in Tkinter's Text Widget

The bug report initially pointed to an issue where using "Find and Replace in selection" deleted existing newlines, but deeper investigation revealed a broader problem: pressing Ctrl+H deleted characters even before the replace dialog appeared. This behaviour was traced to a default binding in Tkinter’s Text widget, where Ctrl+H historically acts as a backspace. As a result, when Ctrl+H was pressed, the widget’s default backspace action occurred before the application's own binding opened the replace dialog, leading to unexpected deletions.

The fix involved binding Ctrl+H directly to the Text widget and returning "break" to prevent the default backspace behaviour from executing. This ensured that only the desired action—the dialog opening—occurred. The key takeaway is that bug reports may highlight a specific symptom of a more general issue, and effective debugging often requires understanding default widget behaviours and event-handling order within the GUI framework.
