"""
tui.py

Copyright © 2015 Alex Danoff. All Rights Reserved.
2015-08-03

This file implements the TUI functionality of the program.
"""

import curses

from enum import Enum

from itunes import itunes

"""Status codes returned by `command_mode` to indicate an action."""
STATUS_CODES = Enum("StatusCodes", 'EXIT ERROR SEARCH')

"""Mapping of commands to actions."""
COMMAND_MAP = {
        "q": STATUS_CODES.EXIT,
        "quit": STATUS_CODES.EXIT
}

"""Constant for error color pair."""
ERROR_PAIR = 1

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

    # positioning variables
    TOP_LINE = 2
    BOTTOM_LINE = curses.LINES - 2
    LEFT = 0
    RIGHT = curses.COLS - 1
    COMMAND_LINE = curses.LINES - 1

    curses.init_pair(ERROR_PAIR, curses.COLOR_RED, curses.COLOR_BLACK)

    stdscr.addstr(0, 0, "Hello, world!")
    stdscr.refresh()

    command_win = curses.newwin(1, curses.COLS, COMMAND_LINE, LEFT)

    command = None

    # continue until quit command is given
    while command != STATUS_CODES.EXIT:

        key = stdscr.getkey()

        # user wants to enter a command
        if key == ":":
            command = command_mode(command_win)
            cursor_pos = stdscr.getyx()

            # tell user they have entered an invalid command
            if command == STATUS_CODES.ERROR:
                stdscr.addstr(COMMAND_LINE, 0, "Invalid command entered", curses.color_pair(ERROR_PAIR))
                stdscr.move(*cursor_pos)
            elif command == STATUS_CODES.SEARCH:
                pass

def command_mode(window, line=0, col=0):
    """
    Receive commands from the user on a vim-like command line.

    Parameters
    ----------
    window : curses.WindowObject
        The window in which the command line should be placed.
    line : int
        The line in `window` on which to display the command line (default 0).
    col : int
        The column in `line` to display the command line (default 0). Note that
        this is the column where the `:` character will be redisplayed, not
        where the actual command will start.

    Returns
    -------
    <Enum 'STATUS_CODES'>
        The status code of the command entered by the user.
    """

    curses.echo()
    window.clear()
    window.addstr(line, col, ":")
    command = window.getstr(line, col + 1)
    command = command.decode("utf-8").lower()
    curses.noecho()

    return COMMAND_MAP.get(command, STATUS_CODES.ERROR)

if __name__ == '__main__':
    curses.wrapper(main)
