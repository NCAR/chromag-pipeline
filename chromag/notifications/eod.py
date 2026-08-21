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
    """Send notification at end of day."""
    to = "mgalloy@ucar.edu"
    date = short2hyphenated(date_run.observing_day)
    # [TODO]: add status (success, failure, incomplete, etc.) to subject?
    subject = f"ChroMag end-of-day processing for {date}"

    log_basedir = get_option("logging", "basedir")
    log_filename = os.path.join(
        log_basedir, f"{date_run.observing_day}.chromag.eod.log"
    )
    body = filter_log(log_filename, 2)  # logging.WARN = 2

    # [TODO]: add run statistics, error messages in log
    # [TODO]: probably should make a timeline histogram like KCor/UCoMP have
    send_email(to, subject, body)
    logger.info(f"sent eod notification to {to}")
