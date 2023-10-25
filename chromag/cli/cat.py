# -*- coding: utf-8 -*-

"""Create and handle cat sub-command.
"""

import warnings


try:
    from astropy.io import fits
    from astropy.utils.exceptions import AstropyUserWarning

    CAT_REQUIREMENTS = True
except ModuleNotFoundError as e:
    CAT_REQUIREMENTS = False


def cat_header(files, validate=False):
    """Display the contents of a header for a list of files."""
    with warnings.catch_warnings():
        if not validate:
            warnings.simplefilter("ignore", AstropyUserWarning)

        for i, file in enumerate(files):
            if len(files) > 1:
                if i != 0:
                    print()

                print(file)
                print("-" * len(file))

            try:
                with fits.open(file) as f:
                    header = f[0].header
                    print(repr(header))
            except FileNotFoundError:
                print(f"{file} not found")


def cat_subcommand(args):
    """Main routine to handle keyword arguments and dispatch the work."""
    if not CAT_REQUIREMENTS:
        args.parser.error(
            "missing Python packages required for listing contents of FITS files"
        )

    cat_header(args.files, args.validate)


def add_cat_subcommand(subparsers):
    """Add cat subcommand to the argparse subparsers."""
    cat_parser = subparsers.add_parser("cat", help="display file header")
    cat_parser.add_argument(
        "files", nargs="+", default=".", help="ChroMag files(s)", metavar="file(s)"
    )
    cat_parser.add_argument("--validate", help="validate header", action="store_true")
    cat_parser.set_defaults(func=cat_subcommand, parser=cat_parser)
