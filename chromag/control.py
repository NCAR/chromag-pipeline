# -*- coding: utf-8 -*-

"""Module handling control of whether (re)processing of dates is stopped.
"""

import os

from .config import get_option


def _get_controlfile() -> str | None:
    controldir = get_option("process", "controldir")
    if controldir is not None:
        if not os.path.isdir(controldir):
            os.makedirs(controldir)
        controlfile = os.path.join(controldir, "command.txt")
        return controlfile
    else:
        return None


def is_running():
    controlfile = _get_controlfile()
    if controlfile is not None:
        with open(controlfile, "r") as f:
            value = f.read()
        return value == "RUNNING"
    else:
        return True


def _set_controlfile(value: str):
    controlfile = _get_controlfile()
    if controlfile is not None:
        with open(controlfile, "w") as f:
            f.write(value)
            return True
    else:
        return False


def set_running():
    if is_running():
        return False
    return _set_controlfile("RUNNING")


def set_stopped():
    if not is_running():
        return False
    return _set_controlfile("STOPPED")
