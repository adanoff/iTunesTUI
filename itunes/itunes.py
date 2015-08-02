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
    if err:
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

    Raises
    ------
    ValueError
        If a record is malformed.

    .. note:: This function currently uses a naive implementation that will not
    work properly if characters such as `,` or `:` are in the values of `raw`.
    """

    records = []

    raw = raw.strip()

    # more than one opening brace = list of records
    if raw.startswith("{{") and raw.endswith("}}"):
        raw = "[" + raw[1:]
        raw = raw[:-2] + "]"

    #print("RAW:", raw)

    open_brace_pos = raw.find("{")
    close_brace_pos = raw.find("}")

    # we found a pair of braces, start a record
    if open_brace_pos != -1 and close_brace_pos != -1:
        record = {}
        record_str = raw[open_brace_pos + 1:close_brace_pos]
        print("RECORD_STR:",record_str)

        # go through each key value pair in the record
        for item in record_str.split(", "):

            # never a `:` in key, so use that to split
            colon_pos = item.find(":")
            if colon_pos != -1:
                key = item[:colon_pos].strip()
                value = item[colon_pos + 1:].strip()
            else:
                raise ValueError("Unable to parse item: {0}".format(item))

# private method to (attempt to) parse values into their proper type
def parse_value(str_value):

    # check for None, int, float, and bool
    if not str_value or str_value == "missing value" or str_value == '""':
        result = None

    elif str_value.isdigit():
        result = int(str_value)

    elif "." in str_value: # might be a float
        dot_pos = str_value.find(".")

        if (str_value[:dot_pos].isdigit() and str_value[dot_pos +
                1:].isdigit()):
            result = float(str_value)

    elif str_value == "true" or str_value == "false":
        result = True if str_value == "true" else False

    else:
        result = str_value

    return result

def main():
    search("just a friend")

if __name__ == '__main__':
    main()
