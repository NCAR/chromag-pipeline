# -*- coding: utf-8 -*-

"""Module containing helper functions for notifications at the end of an eod
run.
"""

import os

from .email import send_email

from ..config import get_option
from ..datetime import short2hyphenated
from ..logging import logger, filter_log


def notify_eod(date_run):
    """Send notification at end of day. Returns whether it sent a
    notification."""
    send_notifications = get_option("notifications", "send")
    if not send_notifications:
        logger.info("skipping sending notification")
        return False

    to = get_option("notifications", "email")
    if to is None:
        logger.warn("no email to notify set")
        return False

    date = short2hyphenated(date_run.observing_day)
    # [TODO]: add status (success, failure, incomplete, etc.) to subject?
    subject = f"ChroMag end-of-day processing for {date}"

    # [TODO]: add run statistics

    log_basedir = get_option("logging", "basedir")
    log_filename = os.path.join(
        log_basedir, f"{date_run.observing_day}.chromag.eod.log"
    )
    body = filter_log(log_filename, 2)  # logging.WARN = 2

    # [TODO]: probably should make a timeline histogram like KCor/UCoMP have
    send_email(to, subject, body)
    logger.info(f"sent eod notification to {to}")

    return True
