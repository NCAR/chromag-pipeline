# -*- coding: utf-8 -*-

"""Module handling control of whether (re)processing of dates is stopped.

There is just a single file, `command.txt`, in `process.controldir` that
contains either "RUNNING" or "STOPPED" that indicates the processing state
of the pipeline. If the file contains, anything besides "RUNNING", the pipeline
is stopped and new runs of the pipeline will not start (existing runs will
finish).
"""

import os

from .config import get_option


def _get_controlfile() -> str | None:
    """Returns the fullpath to the "command.txt" file that stores the
    (re)processing state. If `process.controldir` is not set, returns `None`.
    This routine will create the `controldir` if `process.controldir` is set,
    but hasn't been created yet."""
    controldir = get_option("process", "controldir")
    if controldir is not None:
        if not os.path.isdir(controldir):
            os.makedirs(controldir)
        controlfile = os.path.join(controldir, "command.txt")
        return controlfile
    else:
        return None


def is_running():
    """Determine whether the (re)processing is running or stopped. If
    `process.controldir` is not set, returns `True`."""
    controlfile = _get_controlfile()
    if controlfile is not None:
        with open(controlfile, "r") as f:
            value = f.read()
        return value == "RUNNING"
    else:
        return True


def _set_controlfile(value: str) -> bool:
    """Helper routine to set the value of the (re)processing state of the
    pipeline. `value` must be either "RUNNING" or "STOPPED". If
    `process.controldir` is not set, returns `False`."""
    controlfile = _get_controlfile()
    if controlfile is not None:
        with open(controlfile, "r") as f:
            old_value = f.read()
        if (old_value == "RUNNING") == (value == "RUNNING"):
            return False
        with open(controlfile, "w") as f:
            f.write(value)
        return True
    else:
        return False


def set_running() -> bool:
    """Set the (re)processing state to be running, i.e., new runs are allowed.
    Returns a boolean indicating whether calling this routine changed anything.
    If `process.controldir` is not set, returns `False`."""
    return _set_controlfile("RUNNING")


def set_stopped() -> bool:
    """Set the (re)processing state to be stopped, i.e., new runs are not
    allowed. Returns a boolean indicating whether calling this routine changed
    anything. If `process.controldir` is not set, returns `False`."""
    return _set_controlfile("STOPPED")
