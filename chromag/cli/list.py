# -*- coding: utf-8 -*-

"""Create and handle list sub-command, which lists running ChroMag processes.
"""

import datetime
import os
import time

import psutil
from rich.console import Console

from ..datetime import human_timedelta
from ..file import human_bytes


def list_subcommand(args):
    """List all the running ChroMag processes."""
    n_processes = 0
    now = datetime.datetime.now()
    console = Console(highlight=False)
    for p in psutil.process_iter():
        if p.name() == "chromag":
            with p.oneshot():
                cmdline = p.cmdline()
                if cmdline[2] == "list":
                    continue

                n_processes += 1
                pdatetime = datetime.datetime.fromtimestamp(p.create_time())
                age = human_timedelta(now - pdatetime)

                # [TODO]: not sure how to get this to not return 0.0 from a
                # script; it will return values when I do it interactively
                # cpu_percent = p.cpu_percent(interval=1)
                cpu_percent = "--"

                memory_info = p.memory_info()
                rss = human_bytes(memory_info.rss)
                vms = human_bytes(memory_info.vms)

                console.print(
                    f"[magenta][{p.pid}][/] running for {age}, cpu: {cpu_percent}%, memory physical: {rss}, virtual: {vms} ({p.status()})"
                )

                if args.verbose:
                    print(" ".join(cmdline))
                else:
                    common_prefix = os.path.commonprefix(cmdline[0:2])
                    for i in range(2):
                        cmdline[i] = cmdline[i].removeprefix(common_prefix)
                    cmdline = " ".join(cmdline)
                    print(cmdline)
    if n_processes == 0:
        print("no ChroMag processes currently running")


def add_list_subcommand(subparsers):
    """Add list subcommand to the argparse subparsers."""
    list_parser = subparsers.add_parser("list", help="list running ChroMag processes")
    list_parser.add_argument(
        "-v", "--verbose", help="set to show full output", action="store_true"
    )
    list_parser.set_defaults(func=list_subcommand, parser=list_parser)
