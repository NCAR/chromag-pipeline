# -*- coding: utf-8 -*-

"""Top-level package for ChroMag parser."""

import importlib.metadata
import os
import subprocess

mission_start = "2025-01-01"

# find version and git revision:
#
# - add "-dev" to the version if there have been commits since the version was
#   tagged
# - add "*" to the revision if there are uncommitted changes

__version__ = importlib.metadata.version("chromag")

repo_dir = os.path.dirname(__file__)
try:
    __revision__ = (
        subprocess.check_output(["git", "-C", repo_dir, "rev-parse", "--short", "HEAD"])
        .decode("ascii")
        .strip()
    )
except CalledProcessError as e:
    __revision__ = "N/A"

# add a "*" to the revision if there are uncommitted changes
p = subprocess.run(["git", "-C", repo_dir, "diff-index", "--quiet", "HEAD", "--"])
if p.returncode != 0:
    __revision__ += "*"

try:
    description = (
        subprocess.check_output(["git", "-C", repo_dir, "describe"])
        .decode("ascii")
        .strip()
    )
except CalledProcessError as e:
    description = f"v{__version__}"

if description != f"v{__version__}":
    __version__ = f"{__version__}-dev"
