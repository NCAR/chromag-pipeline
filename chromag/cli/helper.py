# -*- coding: utf-8 -*-

import datetime
import re


def increment_date(date):
    format = "%Y%m%d"
    d = datetime.datetime.strptime(date, format)
    d += datetime.timedelta(days=1)
    return(d.strftime(format))


def split_dates(date_expr, error):
    dates = []
    date_re = re.compile("^[12][0-9]{7}$")
    date_range_re = re.compile("^[12][0-9]{7}-[12][0-9]{7}$")
    for d in date_expr.split(","):
        if date_re.match(d):
            dates.append(d)
        elif date_range_re.match(d):
            start_date = d[0:8]
            end_date = d[9:17]
            if end_date <= start_date:
                error(f"end of range before start of range: {d}")
            date = start_date
            while date < end_date:
                dates.append(date)
                date = increment_date(date)
        else:
            error(f"invalid date expression: {d}")

    return(dates)


def add_run_arguments(parser):
    """Helper routine to add dates and flags arguments for a subcommand.
    """
    date_help = """dates to run on in the form YYYYMMDD including lists (using
           commas) and ranges (using hyphens where end date is not
           included)"""
    parser.add_argument("dates", type=str, nargs="*", help=date_help,
        metavar="date-expr")

    flags_help = """FLAGS section of config filename, i.e., file in config/
        directory matching chromag.FLAGS.cfg will be used"""
    parser.add_argument("-f", "--flags", type=str, help=flags_help,
        default=None)
