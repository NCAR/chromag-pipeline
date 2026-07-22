#!/usr/bin/env python

import argparse
import datetime


def create_dark(dt: datetime.datetime):
    print(dt)


def main():
    parser = argparse.ArgumentParser(description="Create synthetic ChroMag dark")

    datetime_help = "datetime for dark in the format 'YYYY-MM-DDTHH:MM:SS'"
    parser.add_argument("datetime", type=str, help=datetime_help)

    args = parser.parse_args()

    dt = datetime.datetime.strptime(args.datetime, "%Y-%m-%dT%H:%M:%S")

    create_dark(dt)


if __name__ == "__main__":
    main()
