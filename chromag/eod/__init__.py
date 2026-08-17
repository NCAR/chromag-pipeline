# -*- coding: utf-8 -*-

"""Sub-package for end-of-day processing
"""

import os

from .clearday import clearday
from .run import run


# set umask for process: rwxrwxr-x for directories, rw-rw-r--- for files
os.umask(0o002)
