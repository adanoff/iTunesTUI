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

from .exceptions import AppleScriptError, TrackError

def search(search_term, keys=["name"]):
    """
    Search the iTunes library.

    Search the iTunes library for a given string. The search will return matches
    of all types (albums, artists, songs, etc.).

    Parameters
    ----------
    search_term : str
        The string to search for in iTunes.
    keys : list, optional
        The item(s) in the track dictionary to be used for sorting the tracks.
        Defaults to `name` (the track's title). If none of the items in `keys`
        is a valid key in the track dictionaries, or if `None` is passed, the
        current iTunes sorting order will be used.

    Returns
    -------
    list
        A list containing the search results.
    """

    # use {{}} so as not to break str.format
    search_template = """tell application "iTunes"
    set toRet to {{}}
    set searchResults to search playlist "Music" for "{term}"
    repeat with t in searchResults
        set props to get properties of t
        copy props to the end of toRet
    end repeat
    return toRet
    end tell"""

    #print(search_template.format(term=search_term) + "\n")

    out = run_applescript(search_template.format(term=search_term))

    track_list = parse_response(out)

    # sort results
    if track_list:
        for key in keys:
            if key in track_list[0]:
                key_func = lambda track: track.__getitem__(key) or ""
                track_list = sorted(track_list, key=key_func)

    return track_list

def get_playlist(name="Music", key="name"):
    """
    Get all the songs in the playlist specified.

    Parameters
    ----------
    name : str, optional
        The name of the playlist (defaults to "Music", which contains all
        music).
    key : str, optional
        The item in the track dictionary to be used for sorting the tracks.
        Defaults to `name` (the track's title). If `key` is not a valid key in
        the track dictionaries, or if `None` is passed, the current iTunes
        sorting order will be used.

    Returns
    -------
    list
        A list containing dictionaries, each of which represents a track in
        `playlist`.

    Raises
    ------
    PlaylistError
        If the playlist cannot be loaded.
    """

    playlist_template = """tell application "iTunes"
    return properties of tracks in playlist named "{name}"
    end tell"""

    try:
        out = run_applescript(playlist_template.format(name=name))
    except AppleScriptError as ae:
        raise PlaylistError("No playlist named: {0}".format(name), name)

    track_list = parse_response(out)

    # sort results
    if track_list:
        if key in track_list[0]:
            key_func = lambda track: track.__getitem__(key) or ""
            track_list = sorted(track_list, key=key_func)

    return track_list

def play():
    """
    Play the current track.

    This function does not change what track is playing.
    """

    play_script = """tell application "iTunes"
    play
    end tell
    """

    run_applescript(play_script)

def pause():
    """
    Pause the current track.

    This function does not change what track is playing.
    """

    pause_script = """tell application "iTunes"
    pause
    end tell
    """

    run_applescript(pause_script)

def playpause():
    """
    Toggle play state of iTunes.
    """

    playpause_script = """tell application "iTunes"
    playpause
    end tell
    """

    run_applescript(playpause_script)

def play_track(title):
    """
    Play the track indicated by `title`.

    Parameter
    ---------
    title : str
        The title of the track to play.

    Raises
    ------
    TrackError
        If `track` cannot be played.
    """

    script = """tell application "iTunes"
    play track "{0}"
    end tell
    """

    try:
        run_applescript(script.format(title))
    except AppleScriptError as ae:
        raise TrackError("No track named: {0}".format(title), title)

def run_applescript(script):
    """
    Run the given piece of AppleScript in a separate process.

    Parameters
    ----------
    script : str
        A string representing the script to run. The script should be written
        (using a triple-quoted string) with each statement on its own line.
        Indentation does not matter.

    Returns
    -------
    str
        The raw response from running `script`. No processessing is
        done before this value is returned.

    Raises
    ------
    AppleScriptException
        If `script` causes any AppleScript errors.
    """

    # -ss flag for JSON-like form
    command = ["osascript", "-ss"]

    # break script up into different lines
    for line in script.split('\n'):
        command.append('-e')
        command.append(line.strip())
    #print("COMMAND: {0}".format(' '.join(command)))
    applescript_call = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    out, err = applescript_call.communicate()

    out = out.decode("utf-8")
    err = err.decode("utf-8")

    if err:
        raise AppleScriptError("Error parsing script: {0}".format(err), script)

    return out

def parse_response(response):
    """
    Parse the result of an applescript call into a python dictionary.

    Parameters
    ----------
    response : str
        A string containing the unprocessed applescript output.

    Returns
    -------
    list
        A list of dictionaries which contain the information in `response`.

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

    #log_file = open("out.log", "w")

    # go through each record
    for match in record_regex.finditer(response):
        record = {}
        record_str = match.group("record")
        #print("RECORD_STR:",record_str, "\n")

        # remove escaped quotes from records
        if '\\"' in record_str:
            record_str = record_str.replace('\\"', "&quot;")

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

            else:
                raise ValueError("Unable to parse item: {0}".format(item))

            parsed = parse_value(value)
            record["{0}".format(key)] = parsed
            #log_file.write(("{!r} -> {!r}\n".format(value, parsed)))

        records.append(record)

    #log_file.close()
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
    if (not str_value or str_value == "missing value" or str_value == '""' or
            str_value == "none"):
        result = None

    elif str_value.isdigit():
        result = int(str_value)

    elif ("." in str_value and str_value.strip().count(" ") == 0 and
            str_value.count(".") == 1 and '"' not in str_value): # might be a float
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

    else: # assumed to be a string, remove any quotes (and add back escaped)
        result = str_value.replace('"', "")
        result = result.replace("&quot;", '"')

    return result

def main():
    search("just a friend")
    play()
    pause()
    playpause()
    play_track("Just a Friend")
if __name__ == '__main__':
    main()
