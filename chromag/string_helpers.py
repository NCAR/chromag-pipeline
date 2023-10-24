# -*- coding: utf-8 -*-

""" String helper routines.
"""

def truncate(s, max_length, continuation_chars="...", padding=False):
    """ Truncate a string to a length if necessary, but indicate truncated
        strings with the given characters. Also, pad with spaces to
        `max_length` if `padding` is set.
    """
    if len(s) > max_length:
        new_s = s[0:max_length - len(continuation_chars)] + continuation_chars
        return(new_s)

    return(s.ljust(max_length, " ") if padding else s)
