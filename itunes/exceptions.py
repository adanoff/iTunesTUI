"""
exceptions.py

Copyright © 2015 Alex Danoff. All Rights Reserved.
2015-08-02

This file defines custom exceptions for the iTunes funcitonality.
"""

class ITunesError(Exception):
    """
    Base exception class for iTunes interface.
    """
    pass

class AppleScriptError(ITunesError):
    """
    Represents an error received from AppleScript while running a script.

    Parameters
    ----------
    message : str
        The message that the exception will hold.
    script : str
        The AppleScript that was running when this exception was raised (default
        "").

    Attributes
    ----------
    script : str
        The AppleScript that was running when this exception was raised, if one
        was provided.
    """

    def __init__(self, message, script=""):

        super(AppleScriptError, self).__init__(message)
        self.script = script

class TrackError(ITunesError):
    """
    Represents an error in finding or playing a track.

    Parameters
    ----------
    message : str
        The message that the exception will hold.
    title : str
        The title of the track that caused the error (default "").

    Attributes
    ----------
    title : str
        The title of the track that caused the error.
    """

    def __init__(self, message, title=""):

        super(TrackError, self).__init__(message)
        self.title = title

class PlaylistError(ITunesError):
    """
    Represents an error in finding or playing a playlist.

    Parameters
    ----------
    message : str
        The message that the exception will hold.
    title : str
        The title of the playlist that caused the error (default "").

    Attributes
    ----------
    title : str
        The title of the playlist that caused the error.
    """

    def __init__(self, message, title=""):

        super(PlaylistError, self).__init__(message)
        self.title = title
