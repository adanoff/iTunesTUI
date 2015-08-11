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
        "STATUS": 3,
        "TITLE": 4,
        "CURSOR": 5
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
    curses.init_pair(COLOR_PAIRS["ERROR"], curses.COLOR_RED,
            curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIRS["PROMPT"], curses.COLOR_CYAN,
            curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIRS["STATUS"], curses.COLOR_GREEN,
            curses.COLOR_BLACK)
    curses.init_pair(COLOR_PAIRS["CURSOR"], curses.COLOR_WHITE,
            curses.COLOR_BLUE)
    curses.init_pair(COLOR_PAIRS["TITLE"], curses.COLOR_CYAN,
            curses.COLOR_GREEN)

    command_win = curses.newwin(1, curses.COLS, COMMAND_LINE, LEFT)

    command = None

    stdscr.addstr(0, 0, "Hello, world!")
    stdscr.refresh()

    status_message(command_win, "Fetching music...")
    display_list = itunes.get_playlist()
    status_message(command_win, "Got music.")

    cursor_line = 1

    display_pad = load_list(display_list, TOP_LINE, LEFT, cols=RIGHT - LEFT)
    display_pad.move(1, 0)
    display_pad.refresh(0, 0, TOP_LINE, LEFT, BOTTOM_LINE, RIGHT)

    pad_top = 0
    pad_rows = BOTTOM_LINE - TOP_LINE

    cursor_bottom = len(display_list)

    f = open("out.log", "w")


    # continue until quit command is given
    while command != STATUS_CODES.EXIT:

        key = display_pad.getkey()
        previous_line = cursor_line
        current = display_pad.inch(cursor_line + 2, 0)

        # convert arrow keys to their counterparts
        if key == "":
            next = display_pad.getkey() + display_pad.getkey()
            if next == "[B":
                key = "j"
            elif next == "[A":
                key = "k"

        # user wants to enter a command
        if key == ":":
            command = command_mode(command_win)

            # tell user they have entered an invalid command
            if command == STATUS_CODES.ERROR:
                status_message(command_win, "Invalid command entered",
                        color=COLOR_PAIRS["ERROR"])

            elif command == STATUS_CODES.SEARCH:
                search_term = prompt_mode(command_win, prompt="Enter a search term: ")

        elif key == "j": #move cursor down
            #f.write("Recognized: {}\n".format(key))
            if cursor_line < cursor_bottom:
                cursor_line += 1

        # FIXME for some reason going up (with k) moves the curses cursor down 1 then up 2
        elif key == "k": #move cursor up
            if cursor_line > 1:
                cursor_line -= 1

        # TODO jump to bottom/top of list

        else:
            #stdscr.addstr(0, 0, key)
            f.write("UNRECOGNIZED: {}\n".format(key))

        #current = display_pad.inch(cursor_line + 1, 0)
        f.write("PRESSED: {}\n".format(key))

        line_change = cursor_line - previous_line

        # only redraw if we moved the cursor
        if line_change:

            # if we're off the screen now, scroll
            if cursor_line > pad_top + pad_rows or cursor_line < pad_top:
                pad_top += line_change

            #f.write("BELOW CURSOR: {1} ({0}) ({0:b})\n".format(current, chr(current
                #& 0xFF)))
            #f.write("curses.A_REVERSE: {0} ({0:b})\n".format(curses.A_REVERSE))
            reversed = current & curses.A_REVERSE
            #f.write("REVERSED: {0} ({0:b})\n".format(reversed))
            line_str = inchstr(display_pad, cursor_line - line_change, 0)

            f.write("PREVIOUS LINE: {}\n".format(previous_line))
            f.write("LINE CHANGE: {:+}\n".format(line_change))
            f.write("CURSOR LINE: {}\n".format(cursor_line))

            # remove cursor and redraw on next line
            display_pad.addstr(previous_line, 0, line_str, reversed)
            display_pad.move(cursor_line, 0)
            display_pad.chgat(-1, curses.color_pair(COLOR_PAIRS["CURSOR"]))
            display_pad.refresh(pad_top, 0, TOP_LINE, LEFT, BOTTOM_LINE, RIGHT)

    f.close()

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

def load_list(track_list, pad=None, corner_y=0, corner_x=0, key="name", lines=0,
        cols=0):
    """
    Load a list of tracks into a pad and display some of that pad.

    All the tracks provided are loaded into the pad, however they will not all
    be visible at once (depending on provided dimensions).

    Parameters
    ----------
    track_list : list
        A list of dictionaries, each of which represents a track to display.
    pad : curses.WindowObject, optional
        The pad to draw the list in. Defaults to None, which means a new pad
        will be created to house the list.
    corner_y : int, optional
        The line on the screen at which to start the pad. Defaults to 0, which
        is the top of the screen.
    corner_x : int, optional
        The column of the screen at which to start the pad. Defaults to 0, which
        is the left of the screen.
    key : str, optional
        The name of a key in the track dictionaries to use for sorting. If the
        given argument is not a valid key, or if `None` is given, the current
        iTunes sorting order will be used.
    lines : int, optional
        The height of the pad in lines. Defaults to 0, which means the pad's
        height should be determined by the number of tracks in `track_list`.
    cols : int, optional
        The width of the pad in columns. Defaults to 0, which means the pad will
        be given the full width of the terminal (as given by `curses.COLS`).

    Returns
    -------
    curses.WindowObject
        The pad that has now been displayed on the screen.

    .. warning::Don't change the table formatting unless you REALLY know what
    you're doing; it's a fickle beast.
    """


    BUFFER = 2 #minimum spacing between cloumns

    # sort tracks first (if needed)
    if key in track_list[0]:
        key_func = lambda track: track.__getitem__(key) or ""
        track_list = sorted(track_list, key=key_func)

    # add one for the title
    if lines == 0:
        lines = len(track_list) + 1

    if cols == 0 or cols > curses.COLS:
        cols = curses.COLS

    pad = curses.newpad(lines, cols)

    fmts = []

    fmts.append("{i:5}: {name}")
    fmts.append("{album}")
    fmts.append("{artist}")
    fmts.append("[{time}]")

    line_fmt = (
        "{1[0]:<{0[0]}.{0[0]}}" # song name
        "{1[1]:<{0[1]}.{0[1]}}" # album
        "{1[2]:<{0[2]}.{0[2]}}" # artist
        "{1[3]:>{0[3]}.{0[3]}}" # duration
    )

    #f = open("out.log", "w")
    #f.write("COLS: {0}\n".format(cols))

    end_width = 7 # desired width of final column

    num_strings = len(fmts)

    space = [(cols - end_width) // (num_strings - 1)] * (num_strings - 1)
    space.append(cols - 1 - sum(space))

    title_line = line_fmt.format(space, ["    Name", "Album", "Artist", "Time"])
    pad.addstr(0, 0, title_line, curses.color_pair(COLOR_PAIRS["TITLE"]))

    # add the tracks to the pad
    for i, track in enumerate(track_list):
        reversed = (i % 2) * curses.A_REVERSE

        # place the cursor on the first line
        if i == 0:
            reversed = curses.color_pair(COLOR_PAIRS["CURSOR"])

        strings = []

        # create formatted strings
        for fmt in fmts:
            strings.append(fmt.format(i=i+1, **track))

        total_length = len(''.join(strings))

        # if we're off by 1 or a couple, add space to ending string
        while sum(space) < cols - 1:
            #f.write("adding space...\n")
            space[0] += 1

        # if we're over, subtract
        while sum(space) > cols - 1:
            space[-1] -= 1

        # truncate each field as necessary
        for j in range(num_strings - 1):

            # make it more clear that no album is given
            if strings[j] == "None":
                strings[j] = "-"
            strings[j] = truncate(strings[j], space[j] - BUFFER)

        #f.write("{0} : {1}\n".format(space, sum(space)))
        #f.write("{0}\n".format(' '.join(strings)))

        #f.write("space: {0}\n{1}\n{2}\n".format(space //3 -3 , left_str + mid_str + right_str, 40 * '-'))

        line_str = line_fmt.format(space, strings)
        line_str = line_str[:cols]

        pad.addstr(i + 1, 0, line_str, reversed)

    #f.close()

    return pad

@reset_cursor
def inchstr(window, y, x):
    """
    Read a string from curses display at y, x until EOL.

    Parameters
    ----------
    window : curses.WindowObject
        The window to read from.
    y : int
        The row to read from in `window`.
    x : int
        The column to start reading from in row `y`

    Returns
    -------
    str
        The string read from the interface.
    """

    window.move(y, x)
    result = []

    in_char = ""

    x_off = 0

    # weird EOL character...
    while in_char != "ÿ":
        in_char = window.inch(y, x + x_off)
        in_char = chr(in_char & 0xFF)

        x_off += 1

        result.append(in_char)

    return ''.join(result[:-1])

def truncate(text, max_len, fill="..."):
    """
    Truncate given text to a given maximum length.

    Parameters
    ----------
    text : str
        The text to truncate.
    max_len : int
        The maximum allowed length for `text`. If `text` is longer than
        `max_len` it will be shortened, otherwise it will remain unchanged.
    fill : str, optional
        The string that should be displayed at the end of the truncated text to
        indicate truncation. If `max_len` is too short, the fill may be omitted
        or changed. Defaults to `...`.

    Returns
    -------
    str
        The truncated (or unchanged) text, of length no greater than `max_len`
        (including any filling added at the end).
    """

    if max_len <= 0:
        return ""

    if max_len < len(fill):
        fill = "~"

    if len(text) > max_len:
        end_len = max(0, max_len - len(fill))
        text = text[:end_len] + fill

    try:
        assert len(text) <= max_len
    except AssertionError:
        raise AssertionError("{text} {max_len}".format(**locals()))
    return text

if __name__ == '__main__':
    curses.wrapper(main)
