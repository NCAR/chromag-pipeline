# -*- coding: utf-8 -*-

"""Module containing helper functions for notifications at the end of an eod
run.
"""

import os
import socket

from .email import send_email

from .. import __version__, __revision__
from ..config import get_option
from ..datetime import decompose_date, short2hyphenated
from ..logging import logger, filter_log


with open(os.path.join(os.path.dirname(__file__), "eod-template.html"), "r") as f:
    eod_template = f.read()


def notify_eod(date_run):
    """Send notification at end of day. Returns whether it sent a
    notification."""
    send_notifications = get_option("notifications", "send")
    if not send_notifications:
        logger.info("skipped sending notification")
        return False

    to = get_option("notifications", "to")
    if to is None:
        logger.warning("no email to notify set")
        return False
    from_email = get_option("notifications", "from")

    date = short2hyphenated(date_run.observing_day)
    # [TODO]: add status (success, failure, incomplete, etc.) to subject?
    subject = f"ChroMag end-of-day processing for {date}"

    plain_text = ""

    # [TODO]: add run statistics

    log_basedir = get_option("logging", "basedir")
    log_filename = os.path.join(
        log_basedir, f"{date_run.observing_day}.chromag.eod.log"
    )
    log_msgs = filter_log(log_filename, 2)  # logging.WARN = 2

    if log_msgs == "":
        log_msgs = "No log messages WARN or above"

    plain_text += log_msgs

    attachments = []

    eng_basedir = get_option("engineering", "basedir")
    if eng_basedir is not None:
        eng_dir = os.path.join(eng_basedir, *decompose_date(date_run.observing_day))
        if eng_dir is not None:
            timeline_basename = f"{date_run.observing_day}.chromag.timeline.png"
            timeline_filename = os.path.join(eng_dir, timeline_basename)
            attachments.append(timeline_filename)
            timeline_plot_html = (
                f'<img src="cid:{timeline_basename}" alt="Timeline plot"/>'
            )
        else:
            timeline_plot_html = "<p>No timeline plot</p>"
    else:
        timeline_plot_html = "<p>No timeline plot</p>"

    userhome = os.path.expanduser("~")
    user = os.path.split(userhome)[-1]
    hostname = socket.gethostname()

    plain_text += f"\n\nSent from ChroMag pipeline {__version__} [{__revision__}] by {user}@{hostname}"

    html_text = eod_template.format(
        log_msgs=log_msgs,
        timeline_plot_html=timeline_plot_html,
        __version__=__version__,
        __revision__=__revision__,
        user=user,
        hostname=hostname,
    )

    send_email(
        to,
        from_email,
        subject,
        plain_text,
        attachments=attachments,
        html_text=html_text,
    )
    logger.info(f"sent eod notification to {to}")

    return True
