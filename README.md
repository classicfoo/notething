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
T After pressing F6, press enter to accept selected date on calendar picker

## Bugs
X tkcalendar doesn't open in centre of the screen straight away
X Find in seletion doesn't work
X Ctrl + Home is not working (should take user to beginning of file)
X After adding a date using F6 calendar, update line colour
T After making a selection, and pressing ctrl+home, it needs to cleanup custom tags to the text selection and just go to beginning of document
T When updating TNX bullets the line colours don't update after each replace
T Find and replace in selection deletes existing newline
T Replace dialog looks broken
T Replace all doesn't work
T When doing find and replace, it doesn't search from the beginning
T After replacing, it should automatically find the next instance (ready for replacing)
T Pressing enter a few time on line with heading doesn't work as expected

# Study
Custom tag cleanup is essential in the FindReplaceDialog 
N It prevents Visual Artifacts
N Without cleanup, you'd experience these issues:
	N Search highlights would remain visible after closing the dialog
	N Multiple layers of preserved selection highlighting could accumulate
	N These visual artifacts would make the editor look messy and confusing
