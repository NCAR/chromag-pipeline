# -*- coding: utf-8 -*-

"""Top-level package for ChroMag parser."""

import importlib.metadata
import os
import subprocess

# find version and git revision

__version__ = importlib.metadata.version("chromag")

repo_dir = os.path.dirname(__file__)
__revision__ = (
    subprocess.check_output(["git", "-C", repo_dir, "rev-parse", "--short", "HEAD"])
    .decode("ascii")
    .strip()
)
# add a "*" to the revision if there are uncommitted changes
p = subprocess.run(["git", "-C", repo_dir, "diff-index", "--quiet", "HEAD", "--"])
if p.returncode != 0:
    __revision__ += "*"

description = (
    subprocess.check_output(["git", "-C", repo_dir, "describe"]).decode("ascii").strip()
)

if description != f"v{__version__}":
    __version__ = f"{__version__}-dev"
