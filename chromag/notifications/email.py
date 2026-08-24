# -*- coding: utf-8 -*-

"""Module containing helper functions for sending emails.
"""

import os

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from ..logging import logger


def send_email(
    to_email: str,
    from_email: str | None = None,
    subject: str = "",
    plain_text: str = "",
    /,
    *,
    attachments: list[str] | None = None,
    html_text: str = "",
):
    """Send an email. Attachments will be attached with the file basename as
    "Content-ID" and "Content-Disposition" filename.
    """

    userhome = os.path.expanduser("~")
    user = os.path.split(userhome)[-1]

    msg = MIMEMultipart("alternative" if len(html_text) > 0 else "mixed")
    msg["Subject"] = subject
    msg["From"] = f"{user}@ucar.edu" if from_email is None else from_email
    msg["To"] = to_email

    msg.attach(MIMEText(plain_text, "plain"))
    if len(html_text) > 0:
        msg.attach(MIMEText(html_text, "html"))

    for f, name in attachments or []:
        with open(f, "rb") as file:
            part = MIMEApplication(file.read(), Name=name)

        # after the file is closed
        part["Content-ID"] = f"<{name}>"
        part["Content-Disposition"] = f'attachment; filename="{name}"'
        msg.attach(part)

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
