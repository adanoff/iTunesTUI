"""
itunes.py

Copyright © 2015 Alex Danoff. All Rights Reserved.
2015-07-31

This file implements the iTunes "API" methods (in AppleScript)that will be
required by the program.
"""

from subprocess import Popen, PIPE
from datetime import datetime
import json
import re

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
    out = parse_response(out)

def parse_response(response):
    """
    Parse the result of an applescript call into a python dictionary.

    Parameters
    ----------
    response : str
        A string containing the unprocessed applescript output.

    Returns
    -------
    dict
        A dictionary whose keys are a subset of those provided in `response`.

    Raises
    ------
    ValueError
        If a record is malformed.
    """

    records = []

    response = response.strip()

    # more than one opening brace = list of records
    if response.startswith("{{") and response.endswith("}}"):
        response = "[" + response[1:]
        response = response[:-1] + "]"

    #print("RAW:", response)

    record_regex = re.compile(r'{(?P<record>.*?)}')

    # go through each record
    for match in record_regex.finditer(response):
        record = {}
        record_str = match.group("record")
        #print("RECORD_STR:",record_str, "\n")

        # matches commas not in quotes
        #
        # works because a comma in quotes can never be followed ONLY by
        # nonquotes or correctly quoted strings until the end of the line (since
        # one quote has by necessity already passed if it's in a quote)
        item_regex = re.compile(r',(?=(?:[^"]|"[^"]*")*$)')

        # go through each key value pair in the record
        for item in item_regex.split(record_str):

            item = item.strip()
            #print(repr(item))

            # never a `:` in key, so use that to split
            colon_pos = item.find(":")
            if colon_pos != -1:
                key = item[:colon_pos].strip()
                value = item[colon_pos + 1:].strip()
                #print(repr(value))

            else:
                raise ValueError("Unable to parse item: {0}".format(item))

            record["{0}".format(key)] = parse_value(value)

        records.append(record)

    #print(records)
    return records

def parse_value(str_value):
    """
    Parse a string (from AppleScript response) into an equivalent Python type.

    This function parses a string into whatever Python type it looks most like.
    The patters it checks are based on what AppleScript spits out when it
    returns responses. It currently supports int, float, bool, date, and None.

    Parameters
    ----------
    str_value : str
        A string containing the value to be parsed.

    Returns
    -------
    <t>
        A Python type (int, float, bool, etc) with the same value as
        `str_value`. If no suitable match is found, `str_value` is returned.
    """

    # check for None, int, float, bool, and date
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

    elif str_value.startswith("date"):
        open_quote = str_value.find('"')
        close_quote = str_value.rfind('"')

        # make sure there are quotes around the date
        if open_quote != -1 and close_quote != -1:
            date_str = str_value[open_quote + 1:close_quote]
            date_fmt = "%A, %B %d, %Y at %I:%M:%S %p" # wkday, m d, y at time
            result = datetime.strptime(date_str, date_fmt)

    else: # assumed to be a string, remove any quotes
        result = str_value.replace('"', "")

    return result

def main():
    search("just a friend")

if __name__ == '__main__':
    main()
