# -*- coding: utf-8 -*-

import glob
import os

import numpy as np

from ..config import get_option, get_basedir
from ..file import ChroMagFile
from ..pipeline import step


class Catalog:
    """Catalog representing the files in a run.

       new_catalog = catalog[catalog.is_flat and catalog.line == "1083"]
    """
    def __init__(self, n):
        self.n_files = 0
        self.catalog = np.empty((n,), dtype=np.object)

    def add_file(self, file):
        self.catalog[self.n_files] = file
        self.n_files += 1

    # TODO: allow attributes to be passed on to file objects
    # TODO: override indexing (mostly just pass along to NumPy)


@step()
def inventory(run):
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
 
