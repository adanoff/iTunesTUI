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
STATUS_CODES = Enum("StatusCodes", "EXIT ERROR SEARCH")

"""Mapping of commands to actions."""
COMMAND_MAP = {
        "q": STATUS_CODES.EXIT,
        "quit": STATUS_CODES.EXIT,
        "s": STATUS_CODES.SEARCH,
        "search": STATUS_CODES.SEARCH
}

"""Color pair codes for various types of output."""
COLOR_PAIRS = {
        "NORMAL": 0,
        "ERROR": 1,
        "PROMPT": 2,
        "STATUS": 3
}

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

    # initialize color pairs
    curses.init_pair(COLOR_PAIRS["ERROR"], curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIRS["PROMPT"], curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIRS["STATUS"], curses.COLOR_GREEN, curses.COLOR_BLACK)

    command_win = curses.newwin(1, curses.COLS, COMMAND_LINE, LEFT)

    command = None

    stdscr.addstr(0, 0, "Hello, world!")
    stdscr.refresh()

    status_message(command_win, "Fetching music...")
    display_list = itunes.get_playlist()
    status_message(command_win, "Got music.")

    # continue until quit command is given
    while command != STATUS_CODES.EXIT:

        key = stdscr.getkey()

        # user wants to enter a command
        if key == ":":
            command = command_mode(command_win)

            # tell user they have entered an invalid command
            if command == STATUS_CODES.ERROR:
                status_message(command_win, "Invalid command entered",
                        color=COLOR_PAIRS["ERROR"])

            elif command == STATUS_CODES.SEARCH:
                search_term = prompt_mode(command_win, prompt="Enter a search term: ")

def reset_cursor(func):
    """
    Decorator for functions that should not move the cursor permanently.

    After any function with this decorator is called, the cursor will be placed
    in the same spot it was in before the call.

    Parameters
    ----------
    func : function
        The function to decorate.

    Returns
    -------
    function
        The decorated function.
    """

    # store cursor, call function, replace cursor
    def inner(*args, **kwargs):
        cursor_pos = curses.getsyx()
        result = func(*args, **kwargs)
        curses.setsyx(*cursor_pos)
        curses.doupdate()
        return result

    return inner

@reset_cursor
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

@reset_cursor
def prompt_mode(window, prompt=":", line=0, col=0):
    """
    Prompt the user for further information.

    This function is intended to be used to get more information from the user
    in order to complete some task. For example, after the search command is
    issued, a prompt would be used to allow the user to enter the search term.
    The prompt will be displayed in a different color.

    Parameters
    ----------
    window : curses.WindowObject
        The window in which the prompt should be displayed.
    prompt : str
        The string to prompt the user with (defaults to `:`).
    line : int
        The line in `window` in which to display the prompt (defaults to 0 (top)).
    col : int
        The column in `line` in which to start the prompt (defaults to 0 (left)).

    Returns
    -------
    str
        The user's response to the prompt, stripped of leading and trailing
        whitespace.
    """

    prompt = prompt.strip()

    curses.echo()
    window.clear()
    window.addstr(line, col, prompt, curses.color_pair(COLOR_PAIRS["PROMPT"]) |
            curses.A_BOLD)
    response = window.getstr(line, col + 1 + len(prompt))
    response = response.decode("utf-8").lower()
    curses.noecho()

    return response

@reset_cursor
def status_message(window, message, color=COLOR_PAIRS["STATUS"], line=0, col=0):
    """
    Display a status message to the user.

    This function shows the user a status message in the specified window and
    then returns the cursor to its position before the function was called.

    Parameters
    ----------
    window : curses.WindowObject
        The window in which the status message should be displayed.
    message : str
        The status message to display.
    color : int, optional
        The index number of the curses color pair to use for the message.
        Defaults to the `status` color pair.
    line : int, optional
        The line in `window` in which to display the message. Defaults to 0,
        which is the top of the window.
    col : int, optional
        The column in `line` to start display of the message. Defaults to 0,
        which is the beginning of the line.
    """

    message = message.strip()

    window.clear()
    window.addstr(line, col, message, curses.color_pair(color))
    window.refresh()

if __name__ == '__main__':
    curses.wrapper(main)
