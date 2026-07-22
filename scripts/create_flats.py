#!/usr/bin/env python

import argparse
import datetime


def create_flats(start_datetime: datetime.datetime):
    print(start_datetime)


def main():
    parser = argparse.ArgumentParser(description="Create synthetic ChroMag flats")

    datetime_help = "start datetime for flats in the format 'YYYY-MM-DDTHH:MM:SS'"
    parser.add_argument("datetime", type=str, help=datetime_help)

    args = parser.parse_args()

    start_datetime = datetime.datetime.strptime(args.datetime, "%Y-%m-%dT%H:%M:%S")

    create_flats(start_datetime)


if __name__ == "__main__":
    main()
