"""
This sub-package contains tools for interacting with local FRED results
"""

from __future__ import absolute_import
import os
from pathlib import Path
import pytest

from .utils import *
from .job import *
from .run import *
from .insert import *
from .snapshot import *


# version
pkg_root_dir = Path(__file__).parent
with open(os.path.join(pkg_root_dir, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()


# testing suite
def test():
    """
    run pytest tests
    """
    retcode = pytest.main()
