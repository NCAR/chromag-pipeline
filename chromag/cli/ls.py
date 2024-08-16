# -*- coding: utf-8 -*-

"""Create and handle ls sub-command.
"""

import glob
import os
import warnings

try:
    from astropy.io import fits
    from astropy.utils.exceptions import AstropyUserWarning

    LS_REQUIREMENTS = True
except ModuleNotFoundError as e:
    LS_REQUIREMENTS = False


def file_lines(filename):
    """Returns the number of lines in a text file."""
    n_lines = 0

    with open(filename, "r", encoding="utf-8") as f:
        for line in f.readlines():
            n_lines += 1
    return n_lines


def value2str(v, format=None):
    """Convert a given value to a string with the given format, if present."""
    if format is not None:
        return f"{v:{format}}"

    if isinstance(v, str):
        return f"{v:10s}"
    elif isinstance(v, float):
        return f"{v:8.3f}"
    elif isinstance(v, int):
        return f"{v:8d}"
    elif isinstance(v, bool):
        return f"{v!s:5s}"
    elif v is None:
        return 5 * "-"

    return f"{v}"


def list_fits_file_default(f):
    """Display a listing for a file with the default columns."""
    basename = os.path.basename(f)
    with warnings.catch_warnings():
        try:
            with fits.open(f) as fits_file:
                primary_header = fits_file[0].header
                s = "s" if len(fits_file) != 2 else ""

                if "DATATYPE" in primary_header:
                    datatype = primary_header["DATATYPE"]
                else:
                    datatype = 10 * "-"

                if "WAVELNTH" in primary_header:
                    wavelength = primary_header["WAVELNTH"]
                    if type(wavelength) == float:
                        wavelength = f"{wavelength:7.3f} nm"
                    elif len(wavelength) > 0:
                        wavelength = f"{wavelength:>7s} nm"
                else:
                    wavelength = 7 * "-"

                if "EXPTIME" in primary_header:
                    exptime = primary_header["EXPTIME"]
                    if type(exptime) == float:
                        exptime = f"{exptime:7.5f} ms"
                    elif len(exptime) > 0:
                        exptime = f"{exptime:>7s} ms"
                else:
                    exptime = 7 * "-"
            print(f"{basename:30s}  {datatype:10s}  {wavelength:10s}  {exptime:10s}")
        except FileNotFoundError:
            print(f"{basename} not found")
        except OSError as e:
            print(f"{basename:30s}  empty FITS file")


def list_fits_file(f, columns):
    """Display a listing for a file with the given FITS keywords as columns."""
    basename = os.path.basename(f)
    line = f"{basename:30s}"

    with warnings.catch_warnings():
        try:
            with fits.open(f) as fits_file:
                primary_header = fits_file[0].header
                for c in columns:
                    v = primary_header[c] if c in primary_header else None
                    v = value2str(v)
                    line += f"  {v}"
            print(line)
        except FileNotFoundError:
            print(f"{basename} not found")
        except OSError as e:
            print(f"{basename:30s}  empty FITS file")


def list_files(files, columns=None):
    """Display listing for a list of files. Use `columns` list as FITS
    keywords to display, if present.
    """
    for f in files:
        basename = os.path.basename(f)
        if os.path.isdir(f):
            n_subfiles = len(glob.glob(os.path.join(f, "*")))
            name = f"{basename}/"
            print(f"{name:30s}  {n_subfiles} files")
        elif os.path.isfile(f):
            filename, file_extension = os.path.splitext(f)
            if file_extension == ".tgz":
                size = os.stat(f).st_size
                print(f"{basename:30s}  {size} bytes")
                continue

            try:
                if columns is None:
                    list_fits_file_default(f)
                else:
                    list_fits_file(f, columns)
            except OSError:
                if file_extension in [".log", ".olog", ".txt", ".cfg", ".tarlist"]:
                    n_lines = file_lines(f)
                    s = "s" if n_lines != 1 else ""
                    print(f"{basename:30s}  {n_lines} line{s}")
                else:
                    size = os.stat(f).st_size
                    print(f"{basename:30s}  {size} bytes")
        else:
            print(f"{f} - unknown item")


def ls_subcommand(args):
    """Main routine to handle keyword arguments and dispatch the work."""
    if not LS_REQUIREMENTS:
        args.parser.error("missing Python packages required for listing FITS files")

    with warnings.catch_warnings():
        if args.quiet:
            warnings.simplefilter("ignore", AstropyUserWarning)

        try:
            files = [f for f in args.files if os.path.isfile(f)]
            dirs = [d for d in args.files if os.path.isdir(d)]

            if len(files) == 0 and len(dirs) == 1:
                items = list(glob.glob(os.path.join(dirs[0], "*")))
                files = [f for f in items if os.path.isfile(f)]
                dirs = [d for d in items if os.path.isdir(d)]

            if args.keywords is None:
                columns = None
            else:
                columns = args.keywords.split(",")

            list_files(sorted(dirs))
            list_files(sorted(files), columns=columns)
        except KeyboardInterrupt:
            pass


def add_ls_subcommand(subparsers):
    """Add ls subcommand to the argparse subparsers."""
    ls_parser = subparsers.add_parser(
        "ls", help="list files with extra ChroMag-specific info"
    )
    ls_parser.add_argument(
        "files", nargs="*", default=".", help="ChroMag files(s)", metavar="file(s)"
    )
    ls_parser.add_argument(
        "-k", "--keywords", type=str, help="FITS keyword names to display", default=None
    )
    ls_parser.add_argument("--quiet", help="suppress warnings", action="store_true")
    ls_parser.set_defaults(func=ls_subcommand, parser=ls_parser)
