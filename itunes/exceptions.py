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
