"""
tools for reading and processing FRED run logs
"""

import os
from os import PathLike
from typing import Dict, List, Optional, Tuple, Union
from collections import defaultdict
from .utils import _path_to_run

FRED_RUN_LOG_FNAME = "LOG"

__all__ = ["return_fred_run_log"]
__author__ = ["Duncan Campbell"]


def return_fred_run_log(run_id, **kwargs) -> List[str]:
    """
    Return a FRED run log.

    Parameters
    ----------
    run_id : int
        a FRED run ID

    PATH_TO_RUN : PathLike, optional
        a path to a FRED run directory

    job_key : string, optional
        A FRED job key

    job_id : int, optional
        A FRED job ID

    PATH_TO_JOB : PathLike, optional

    Returns
    -------
    logs : List
        a list of lines in the log

    Notes
    -----
    One of `PATH_TO_RUN`, `job_key`, `job_id`, or `PATH_TO_JOB`
    must be passed as a keyword argument.

    See .utils._path_to_run for more optional parameters
    """

    # enforce necessary parameters
    if not any(
        k in kwargs for k in ["PATH_TO_RUN", "job_key", "job_id", "PATH_TO_JOB"]
    ):
        msg = (
            "One of `PATH_TO_RUN`, `job_key`, `job_id`, or `PATH_TO_JOB` "
            "must be passed as a keyword argument."
        )
        raise TypeError(msg)

    PATH_TO_RUN = _path_to_run(run_id=run_id, **kwargs)

    logs = _read_fred_run_log(run_id, PATH_TO_RUN)
    return logs


def _read_fred_run_log(run_id: int, PATH_TO_RUN: PathLike) -> List:
    """
    Read in a FRED run log file.

    Returns
    -------
    log_lines : List
        a list of FRED run logs
    """

    log = os.path.join(PATH_TO_RUN, FRED_RUN_LOG_FNAME)
    with open(log) as f:
        lines = f.readlines()
    return lines
