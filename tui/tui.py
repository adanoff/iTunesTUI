"""
tui.py

Copyright © 2015 Alex Danoff. All Rights Reserved.
2015-08-03

This file implements the TUI functionality of the program.
"""

import curses
from ..itunes import itunes

"""The top line of the usuable screen."""
TOP = 2

"""The bottom line of the usable screen."""
BOTTOM = curses.LINES - 2

"""The leftmost column of the usable screen."""
LEFT = 0

"""The rightmost column of the usable screen."""
RIGHT = curses.COLS - 1

"""The line allocated for entering commands."""
COMMAND = curses.LINES - 1

def main(stdscr):
    """
    Main controller function for the TUI.

    This function provides the standard run loop for the application.

    Parameters
    ----------
    stdscr : curses.WindowObject
        A `WindowObject` representing the main screen as passed by
        `curses.wrapper`.
    """
    pass

if __name__ == '__main__':
    curses.wrapper(main)
