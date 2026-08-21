# -*- coding: utf-8 -*-

"""Module containing helper functions for sending emails.
"""

from email.mime.text import MIMEText
import os
import smtplib
import socket

from .. import __version__, __revision__
from ..logging import logger


def send_email(
    to_email: str, from_email: str | None = None, subject: str = "", body_text: str = ""
):
    """Send an email."""
    userhome = os.path.expanduser("~")
    user = os.path.split(userhome)[-1]
    hostname = socket.gethostname()

    body_text += f"\n\nSent from ChroMag pipeline {__version__} [{__revision__}] by {user}@{hostname}"

    msg = MIMEText(body_text)
    msg["Subject"] = subject
    msg["From"] = f"{user}@ucar.edu" if from_email is None else from_email
    msg["To"] = to_email

    with smtplib.SMTP("localhost") as s:
        try:
            refused_recipients = s.send_message(msg)
            for r in refused_recipients:
                logger.warning(r)
        except smtplib.SMTPRecipientsRefused as e:
            logger.warning(e)
        except smtplib.SMTPHeloError as e:
            logger.warning(e)
        except smtplib.SMTPSenderRefused as e:
            logger.warning(e)
        except smtplib.SMTPDataError as e:
            logger.warning(e)
