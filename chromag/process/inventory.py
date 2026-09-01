# -*- coding: utf-8 -*-

"""Module for making inventory/catalog of ChroMag data."""

import glob
import os

import numpy as np

from ..config import get_option, get_basedir
from ..datetime import decompose_date, filename2datetime
from ..epochs import get_epochvalue
from ..file import ChroMagRawFile
from ..logging import logger
from ..pipeline import step
from ..plot import write_timeline
from ..strings import truncate as truncate_string


class MissingRawData(Exception):
    """Exception subclass to indicate a missing raw data directory."""


class Catalog:
    """Catalog representing the files in a run. You can create a new catalog for
    a subset of files from the catalog using any attributes of ChroMag file
    objects, such as:

       new_catalog = catalog[catalog.is_flat & (catalog.wave_region == "1083")]
    """

    def __init__(self):
        self.n_files = 0
        self.catalog = []

    def add_file(self, file: ChroMagRawFile):
        """Add a ChroMagRawFile to the catalog."""
        self.catalog.append(file)
        self.n_files += 1

    def __len__(self):
        return len(self.catalog)

    def __getattr__(self, name: str):
        return np.array([f.__getattribute__(name) for f in self.catalog])

    def __getitem__(self, key: str):
        new_catalog = Catalog()
        for f, k in zip(self.catalog, key):  # pylint: disable=invalid-name
            if k:
                new_catalog.add_file(f)
        return new_catalog

    def __iter__(self):
        return self.catalog.__iter__()

    def __repr__(self):
        return "\n".join([str(f) for f in self.catalog])

    def __str__(self):
        return f"Catalog of {self.n_files} ChroMag files"


def write_inventory_file(catalog: Catalog, filename: str):
    """Write a single inventory file from the given catalog."""
    with open(filename, "w", encoding="utf-8") as file:
        for f in catalog:  # pylint: disable=invalid-name
            components = [
                f"{f.basename}",
                f"{f.datatype[0:3].lower()}",
                f"{f.object:4s}",
                f"{f.wavelength:7.3f} nm",
                f"{f.scan_i:5d}",
                f"{f.scan_n:5d}",
                f"{truncate_string(f.obs_description, 25, padding=True)}",
            ]
            file.write("   ".join(components) + "\n")


@step()
def run_inventory(run):
    """Generate inventory files."""
    raw_basedir = get_basedir(run.observing_day, "raw")
    raw_dir = os.path.join(raw_basedir, run.observing_day)

    if not os.path.isdir(raw_dir):
        raise MissingRawData(f"raw directory does not exist: {raw_dir}")

    filenames = glob.glob(os.path.join(raw_dir, "*.fits*"))
    # glob doesn't sort the filenames
    filenames = sorted(filenames, key=os.path.basename)

    catalog = Catalog()

    for f in filenames:  # pylint: disable=invalid-name
        process = get_epochvalue("process", filename2datetime(f))
        if process:
            file = ChroMagRawFile(f, run.observing_day)
            logger.debug(str(file))
            catalog.add_file(file)
        else:
            logger.warn(f"skipping {os.path.basename(f)}")

    logger.info(f"created catalog with {catalog.n_files} files")
    logger.info("writing inventory files...")

    process_dir = get_basedir(run.observing_day, "process")
    if not os.path.isdir(process_dir):
        os.mkdir(process_dir)

    date_dir = os.path.join(process_dir, run.observing_day)
    if not os.path.isdir(date_dir):
        os.mkdir(date_dir)

    inventory_filename = os.path.join(
        date_dir, f"{run.observing_day}.chromag.inventory.txt"
    )
    write_inventory_file(catalog, inventory_filename)

    eng_basedir = get_option("engineering", "basedir")
    if eng_basedir is not None:
        eng_dir = os.path.join(eng_basedir, *decompose_date(run.observing_day))
        if not os.path.isdir(eng_dir):
            os.makedirs(eng_dir)
        timeline_filename = os.path.join(
            eng_dir, f"{run.observing_day}.chromag.timeline.png"
        )
        write_timeline(timeline_filename, catalog)

    return catalog
