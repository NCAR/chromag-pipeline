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
    def __init__(self, n):
        self.n_files = 0
        self.catalog = np.empty((n,), dtype=np.object)

    def add_file(self, file):
        self.catalog[self.n_files] = file
        self.n_files += 1

    def __str__(self):
        return("\n".join([str(f) for f in self.catalog]))

    def __len__(self):
        return(len(self.catalog))

    def __getattr__(self, name):
        return(np.array([f.__getattribute__(name) for f in self.catalog]))

    def __getitem__(self, key):
        new_catalog_files = self.catalog[key]
        new_catalog = Catalog(len(new_catalog_files))
        for f in new_catalog_files:
            new_catalog.add_file(f)
        return(new_catalog)


@step()
def run_inventory(run):
    raw_basedir = get_basedir(run.date, "raw")
    raw_dir = os.path.join(raw_basedir, run.date)

    filenames = glob.glob(os.path.join(raw_dir, "*.fts*"))

    catalog = Catalog(len(filenames))

    for f in filenames:
        file = ChroMagFile(f)
        run.logger.info(str(file))
        catalog.add_file(file)

    run.logger.info(f"created catalog with {catalog.n_files} files")
    return(catalog)
 
