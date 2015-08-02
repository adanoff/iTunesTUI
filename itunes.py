"""
itunes.py

Copyright © 2015 Alex Danoff. All Rights Reserved.
2015-07-31

This file implements the iTunes "API" methods (in AppleScript)that will be
required by the program.
"""

from subprocess import Popen, PIPE
import json

def search(search_term):
    """
    Search the iTunes library.

    Search the iTunes library for a given string. The search will return matches
    of all types (albums, artists, songs, etc.).

    Parameters
    ----------
    search_term : str
        The string to search for in iTunes.

    Returns
    -------
    list
        A list containing the search results.
    """

    search_template = """tell application "iTunes"
    set music to playlist "Music"
    log (search music for "{term}")
    end tell"""

    #use {{}} so as not to break str.format
    search_template = """tell application "iTunes"
    set toRet to {{}}
    set searchResults to search playlist "Music" for "{term}"
    repeat with t in searchResults
        set props to get properties of t
        copy props to the end of toRet
    end repeat
    return toRet
    end tell"""

    #search_template = """tell application "iTunes"
    #activate
    #display dialog "test"
    #end tell"""

    print(search_template.format(term=search_term))
    #TODO figure out how the fuck to get applescript result into usable form
    #TODO remember that NONE of the keys are quoted - might make things a bit easier

    # -ss flag for JSON-like form
    command = ["osascript", "-ss"]

    # break script up into different lines
    for line in search_template.format(term=search_term).split('\n'):
        command.append('-e')
        command.append(line.strip())
    print("COMMAND: {0}".format(' '.join(command)))
    applescript_call = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    out, err = applescript_call.communicate()
    if (err):
        print("ERROR: ", err)

    out = out.decode("utf-8")
    out = parse_applescript(out)

def parse_applescript(raw):
    """
    Parse the result of an applescript call into a python dictionary.

    The raw response will be parsed as fully as possible, however the returned
    dictionary is not guaranteed to contain all of the information in `raw`.

    Parameters
    ----------
    raw : str
        A string containing the unprocessed applescript output.

    Returns
    -------
    dict
        A dictionary whose keys are a subset of those provided in `raw`.

    .. note:: This function currently uses a naive implementation that will not
    work properly if characters such as `,` or `:` are in the values of `raw`.
    """

    print(raw)
    pass

def main():
    search("just a friend")

if __name__ == '__main__':
    main()
