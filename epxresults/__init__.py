"""
This sub-package contains tools for interacting with local FRED results
"""

from __future__ import absolute_import

from .utils import *
from .job import *
from .run import *
from .insert import *


import os
from pathlib import Path
import pytest

# version
mypackage_root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
with open(os.path.join(mypackage_root_dir, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()


def test():
    """
    run pytest tests
    """
    retcode = pytest.main()
