# -*- coding: utf-8 -*-

"""Create and handle ls sub-command.
"""

import glob
import os

try:
    from astropy.io import fits
    from astropy.utils.exceptions import AstropyUserWarning
    ls_requirements = True
except ModuleNotFoundError as e:
    ls_requirements = False


def file_lines(filename):
    n_lines = 0

    with open(filename, "r") as f:
        for line in f.readlines():
            n_lines += 1
    return(n_lines)


def list_fits_file_default(f):
    basename = os.path.basename(f)
    try:
        with fits.open(f) as fits_file:
            primary_header = fits_file[0].header
            s = "s" if len(fits_file) != 2 else ""
            n_exts = f"{len(fits_file) - 1} ext{s}"
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


def value2str(v, format=None):
    if format is not None:
        template = f"{{v{format}}}"
        return(template.format(v=v))
    if type(v) == str:
        return(f"{v:10s}")
    elif type(v) == float:
        return(f"{v:8.3f}")
    elif type(v) == int:
        return(f"{v:8d}")
    elif type(v) == bool:
        return(f"{v!s:5s}")
    elif v is None:
        return 5 * "-"
    return(f"{v}")
    
    
def list_fits_file(f, columns):
    basename = os.path.basename(f)
    line = f"{basename:30s}"
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


def list_files(files, columns=None):
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


def ls(args):
    if not ls_requirements:
        args.parser.error("missing Python packages required for listing FITS files")

    try:
        files = [f for f in args.files if os.path.isfile(f)]
        dirs = [d for d in args.files if os.path.isdir(d)]

        if len(files) == 0 and len(dirs) == 1:
            items = [f for f in glob.glob(os.path.join(dirs[0], "*"))]
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
    parser = subparsers.add_parser("ls",
        help="list files with extra ChroMag-specific info")
    parser.add_argument("files", nargs="*",
        default=".",
        help="ChroMag files(s)",
        metavar="file(s)")
    parser.add_argument("-k", "--keywords", type=str,
        help="FITS keyword names to display",
        default=None)
    parser.set_defaults(func=ls, parser=parser)