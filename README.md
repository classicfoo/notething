# Readme

## Test Area

M Asdfasf 
	M Testing
	M This is a nested bullet 06 May 2025.
	M This is a nested bullet 08 Jun 2025.	
	
M This is a bullet
	X This is a nested bullet

T This is a bullet.
T This is a bullet. 
	T This is a nested bullet.
	

T This is a bullet. 
	M This is a migrated bullet
	N This is a note

### This Is A Heading

T Asdfasf

T Asdfasfa


## Features.
- F5 current time (Sydney)
- F6 Calendar
- Find Dialog (Ctrl + F)
- Find and Replace Dialog (Ctrl + H)
- Smart Home Key and Selection

## Todo
X Pressing Shift + Home
	X First time - Selects until the end of first whitepsace characters
	X Second time - Selects until the beginning of the line
X Find and Replace in selction checkbox
X Open Recent Files ... (Lists the last 5 files recently opened)
X Open dialog to be for all files by default (not just .txt files)
X Reopen last file on startup variable (for debugging purposes, bool value)
X After pressing F6, press enter to accept selected date on calendar picker
X Create a settings dialog
X Create a mixin that makes sure that all dialogs are opened in the centre of the screen
X Suppress default text widget behaviours
	X Ctrl + K  # Delete line from cursor to end
	X Ctrl + D  # Delete character after cursor
	X Ctrl + O  # Inserts newline
X Remember match case settings
X Auto suggest filenames by looking at the first markdown H1 in file and then using that ensuring that the filename is prepped so that it's valid. the end result should have a filename in lowercase and each word is separated by underscores. 
X Make markdown H1, H2 and H3 headings always be capitalised for each word on that line
T Dynamic Line Formatting
	X Rename TNX to Dynamic line formatting (DLF)
	X Add to settings
	X Make sure that setting applies to entire document when dialog is closed i.e. formatign is stripped for entire document when DLF is unchecked
	T Generalise the rules, so that the user can define them, put this in the settings dialog.
X File > New works differently depending on whether the app is being launched for the first time (first window) or if it's another window being opened
X Ensure all markdown h1, h2, h3 headings have the first letter of each word on that line captitalised
T Change the insert_time function to be more generic. The time should be whatever is set on the user's system. More generic naming makes the code more maintainable. this app is meant to be for general use. 
X Capitalise the first word in line (excluding "T ", "N ", "X ", "C ", "M "), whitespace characters and "# ", "## " and "### ". Add this to the settings.
T Find and replace dynamic line formatting to be updated right after replacement is done.
X Make replace all the default when pressing enter
	C Do we want to remove the alert after replacing all? No
		N Maybe make it so that left and right keys select the different buttons and pressing enter will depend on what button is selected.
	X Remember find and replace text across sessions
T Make F5 and F6 more generic
	T Make it so that user can define the date format and remember it
X Highlighter tool
X Add a full stop after pressing enter on a line. 
	N If there isn't already a full stop. 
	N Strip any whitespace from the end of the line before adding full stop.
	N User has to press enter for it auto add the full stop. 
	N Add a setting under text formatting to enable or disable this feature. 
X Make settings dialog scrollable.
T Move selected date by using arrow keys on calendar widget. 



## Bugs
X Tkcalendar doesn't open in centre of the screen straight away
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
X Find and replace not working on new window after going file > new
X Pressing enter a few time on line with heading doesn't work as expected
T Arrow keys doesn't move dates on calendar
X Checkboxes not showing properly for settings. 
X Open file dialog makes other window focused.
X Ctrl+Shift+Home not working 
X Shift+tab does not work on single lines
T Highlighter actions does not undo
T After accidently captialising every word on a line, can't undo.


# Study

## Preserving Visual Context With Custom Tags In Tkinter's Find/replace Dialog

In Tkinter, when a dialog like Find/Replace is opened, it takes focus away from the main text widget. This triggers a default behaviour where the Text widget clears its selection highlighting, making it difficult for users to see what they had selected—a serious usability issue when performing actions like "Find in selection." To address this, we first disabled the automatic selection-clearing behaviour during widget initialisation. However, this alone wasn’t enough. We introduced custom tags to visually preserve and manage the user's selection while the dialog was open.

These custom tags served multiple purposes: they maintained visual feedback for users, clearly marked search boundaries, and supported layered visual states—such as showing both selected regions and search highlights simultaneously. Without proper cleanup, though, these tags could linger after the dialog closed, leading to confusing visual artifacts like leftover highlights or stacked tag effects. By carefully cleaning up tags when the dialog is dismissed, we preserved the clarity and usability of the editor. This solution highlights how working around Tkinter’s limitations with custom tags enables a cleaner, more intuitive user experience.

## Uncovering Hidden Behaviours: Debugging Ctrl+h In Tkinter's Text Widget

The bug report initially pointed to an issue where using "Find and Replace in selection" deleted existing newlines, but deeper investigation revealed a broader problem: pressing Ctrl+H deleted characters even before the replace dialog appeared. This behaviour was traced to a default binding in Tkinter’s Text widget, where Ctrl+H historically acts as a backspace. As a result, when Ctrl+H was pressed, the widget’s default backspace action occurred before the application's own binding opened the replace dialog, leading to unexpected deletions.

The fix involved binding Ctrl+H directly to the Text widget and returning "break" to prevent the default backspace behaviour from executing. This ensured that only the desired action—the dialog opening—occurred. The key takeaway is that bug reports may highlight a specific symptom of a more general issue, and effective debugging often requires understanding default widget behaviours and event-handling order within the GUI framework.

# Taming Tkinter's Text Widget: Understanding And Overriding Emacs-style Default Keybindings

Tkinter's Text widget comes with numerous default keybindings inherited from Emacs, which can surprise developers expecting Windows-style behavior. These include unexpected actions like Ctrl+O inserting a newline, Ctrl+H acting as backspace, Ctrl+D deleting characters, and various Alt/Meta key combinations for word navigation and deletion. To create a modern text editor experience, it's important to explicitly override these default bindings using bind() with return "break" to prevent the default behavior, and then implement the expected Windows-style shortcuts that users are familiar with, such as Ctrl+O for file operations and Ctrl+H for find/replace functionality.

# Argument For The Name "tnx Bullets"

While "TNX Bullets" has the potential to be a catchy and memorable name, it may also lead to confusion due to its ambiguity and lack of clarity regarding the feature's functionality. A more descriptive name that directly conveys the purpose of the feature, such as "Dynamic Line Highlighting," might be more effective in ensuring users understand its value and functionality.

# Embracing Yagni: Designing Flexible And Future-proof Software Solutions

The concept of designing software with flexibility and generalization in mind is closely aligned with the principle of **YAGNI (You Aren't Gonna Need It)**, which emphasizes avoiding the implementation of unnecessary features until they are truly required. By adhering to YAGNI, developers can focus on delivering core functionalities that meet current user needs while leaving room for future enhancements. This approach not only simplifies the codebase, making it easier to maintain and understand, but also future-proofs the software by allowing it to adapt to changing requirements and unforeseen use cases without significant rework. Ultimately, prioritizing flexibility and generalization helps ensure that the application remains relevant and responsive to evolving user demands.

# Resolving Checkbox Display Issues In The Find/replace Dialog Through Proper Variable Initialization

The issue with dashes appearing in the checkboxes of the Find/Replace dialog is likely due to improperly initialized variables or mismatched variable types. To resolve this, the variable initialization should be moved before the UI creation, ensuring that the BooleanVar variables have explicit parent references (self) and initial values. By reordering the initialization process to guarantee that all variables exist before being used in the UI elements, this will eliminate the dashes, which typically indicate that the checkbutton's variable is in an undefined state. After implementing these changes, any related errors should be resolved.

# Leveraging Pseudocode And Problem Decomposition In Implementing Markdown Heading Capitalization

The successful implementation of the heading capitalization feature came after an initial failed attempt, highlighting the importance of proper planning and problem decomposition. During the second attempt, we took a more structured approach by first consulting ChatGPT to generate pseudocode and thoroughly describe the problem, which provided a fresh perspective on the solution. This new algorithm, which systematically handles word capitalization through _capitalize_heading_words and heading structure management via _format_heading_line, was then successfully integrated into the application. However, the implementation still had an oversight where the _update_line_formatting_event method didn't check the user's preference setting (auto_capitalize_headings), causing automatic formatting to occur even when disabled. This issue was ultimately resolved by adding a condition check, but the journey from failed attempt to successful implementation demonstrates how breaking down a problem and viewing it from a different angle, combined with proper planning and pseudocode, can lead to more effective solutions in software development.


# F7 Highlighter Tool: Quick Text Highlighting With Visual Feedback

The highlighter tool is a simple yet effective feature that allows users to highlight text in the editor using the F7 key. It works in two main ways: you can highlight an entire line when no text is selected, or highlight specific text when you have made a selection.

When you press F7 with no text selected, the tool automatically targets the entire line where your cursor is located. If that line isn't already highlighted, it adds a yellow highlight; if it's already highlighted, pressing F7 removes the highlight. This makes it easy to quickly highlight important lines in your notes.

When you have text selected and press F7, the tool works slightly differently. Instead of highlighting the whole line, it only highlights your selected text. If any part of your selection was already highlighted, pressing F7 removes all highlighting within the selection. This gives you precise control over which parts of your text are highlighted. The tool uses Tkinter's tag system to apply the highlighting, and can be enabled or disabled through the settings menu, with your preference being saved between sessions.

The tool provides clear visual feedback through its color system. Regular highlights appear in yellow, while selected text appears with a light grey background. When you select text that's already highlighted, you see a muddy yellow-grey color that naturally shows the overlap between the two states. This intuitive color mixing helps you easily identify text that is both selected and highlighted at the same time.
