# -*- coding: utf-8 -*-

"""Module containing helper functions for notifications at the end of an eod
run.
"""

import os

from .email import send_email

from ..config import get_option
from ..datetime import decompose_date, short2hyphenated
from ..logging import logger, filter_log


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

    # [TODO]: add run statistics

    log_basedir = get_option("logging", "basedir")
    log_filename = os.path.join(
        log_basedir, f"{date_run.observing_day}.chromag.eod.log"
    )
    log_msgs = filter_log(log_filename, 2)  # logging.WARN = 2

    if log_msgs == "":
        body = "No log messages WARN or above"
    else:
        body = log_msgs

    attachments = []

    eng_basedir = get_option("engineering", "basedir")
    if eng_basedir is not None:
        eng_dir = os.path.join(eng_basedir, *decompose_date(date_run.observing_day))
        if eng_dir is not None:
            timeline_filename = os.path.join(
                eng_dir, f"{date_run.observing_day}.chromag.timeline.png"
            )
            attachments.append(timeline_filename)

    send_email(to, from_email, subject, body, attachments=attachments)
    logger.info(f"sent eod notification to {to}")

    return True
