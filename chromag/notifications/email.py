# -*- coding: utf-8 -*-

"""Module containing helper functions for sending emails.
"""

from email.mime.text import MIMEText
import os
import smtplib
import socket

from .. import __version__, __revision__
from ..logging import logger


def send_email(to_email: str, subject: str, body_text: str):
    """Send an email."""
    userhome = os.path.expanduser("~")
    user = os.path.split(userhome)[-1]
    hostname = socket.gethostname()

    body_text += f"\n\nSent from ChroMag pipeline {__version__} [{__revision__}] by {user}@{hostname}"

    msg = MIMEText(body_text)
    msg["Subject"] = subject
    msg["From"] = f"{user}@ucar.edu"
    msg["To"] = to_email

    with smtplib.SMTP("localhost") as s:
        try:
            refused_recipients = s.send_message(msg)
            for r in refused_recipients:
                logger.warn(r)
        except smtplib.SMTPRecipientsRefused as e:
            logger.warn(e)
        except smtplib.SMTPHeloError as e:
            logger.warn(e)
        except smtplib.SMTPSenderRefused as e:
            logger.warn(e)
        except smtplib.SMTPDataError as e:
            logger.warn(e)
