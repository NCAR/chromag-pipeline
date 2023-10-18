# -*- coding: utf-8 -*-

import glob
import os

import numpy as np

from ..config import get_option, get_basedir
from ..file import ChroMagFile
from ..pipeline import step


class Catalog:
    """Catalog representing the files in a run. You can create a new catalog for
    a subset of files from the catalog using any attributes of ChroMag file
    objects, such as:

       new_catalog = catalog[catalog.is_flat & (catalog.line == "1083")]
    """
    def __init__(self):
        self.n_files = 0
        self.catalog = []

    def add_file(self, file):
        self.catalog.append(file)
        self.n_files += 1

    def __str__(self):
        return("\n".join([str(f) for f in self.catalog]))

    def __len__(self):
        return(len(self.catalog))

    def __getattr__(self, name):
        return(np.array([f.__getattribute__(name) for f in self.catalog]))

    def __getitem__(self, key):
        new_catalog = Catalog()
        for f, k in zip(self.catalog, key):
            if k:
                new_catalog.add_file(f)
        return(new_catalog)

    def __iter__(self):
        return(self.catalog.__iter__())

    def __next__(self):
        return(self.catalog.__next__())

    def __str__(self):
        return(f"Catalog of {self.n_files} ChroMag files")


def write_inventory_file(catalog, filename):
    with open(filename, "w") as file:
        for f in catalog:
            file.write(f"{f.basename}   {f.datatype}   {f.wavelength:7.3f} nm   {f.scan_i:5d}   {f.scan_n:5d}\n")


@step()
def run_inventory(run):
    raw_basedir = get_basedir(run.date, "raw")
    raw_dir = os.path.join(raw_basedir, run.date)

    filenames = glob.glob(os.path.join(raw_dir, "*.fits*"))

    catalog = Catalog()

    for f in filenames:
        file = ChroMagFile(f)
        run.logger.info(str(file))
        catalog.add_file(file)

    run.logger.info(f"created catalog with {catalog.n_files} files")
    run.logger.info("writing inventory files...")

    process_dir = get_basedir(run.date, "process")
    if not os.path.isdir(process_dir):
        os.mkdir(process_dir)

    date_dir = os.path.join(process_dir, run.date)
    if not os.path.isdir(date_dir):
        os.mkdir(date_dir)

    inventory_filename = os.path.join(date_dir, f"{run.date}.chromag.inventory.txt")
    write_inventory_file(catalog, inventory_filename)

    return(catalog)
 
