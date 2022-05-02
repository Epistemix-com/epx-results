"""
"""

import os
import re
import datetime as dt
from warnings import warn
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from .utils import _path_to_job


__all__ = ["Snapshot"]
__author__ = ["Duncan Campbell"]


def _path_to_snapshot(date=None, **kwargs) -> Path:
    """
    Return the full path to FRED snapshot file.

    Parameters
    ----------
    date : dt.date, optional
            a simulation snapshot date
            If not passed, the last snapshot in a FRED job will be returned.

    **kwargs : dict
        One of the following keyword parameters must be provided:

        job_key : string
            A FRED job key
        job_id : int
            a FRED job ID
        PATH_TO_JOB : PathLike
            a path to a FRED job
        PATH_TO_SNAPSHOT : PathLike
            a path to a FRED snapshot. If passed, this path is returned
            regardless of `date` or any other keyword argument.

    Other Parameters
    ----------------
    **kwargs: dict
        additonal optional keyword arguments:

        FRED_RESULTS : PathLike
            the full path to a local FRED results directory
        FRED_HOME : PathLike
            the full path to a local FRED home directory.

    Returns
    -------
    PATH_TO_SNAPSHOT : Path
        a path to a FRED snapshot file

    Raises
    ------
    FileNotFoundError
        Raised if the indicated FRED snapshot cannot be found.
    ValueError
        Raised if the keyword parameters are not sufficient to uniquely
        identify a FRED snapshot file.

    Notes
    -----
    For details on how the path to a FRED job is resolved,
    see :py:func:`epxresults.utils._path_to_job`.

    :meta public:
    """

    if "PATH_TO_SNAPSHOT" in kwargs.keys():
        PATH_TO_SNAPSHOT = os.path.abspath(kwargs["PATH_TO_SNAPSHOT"])
        if not os.path.isfile(PATH_TO_SNAPSHOT):
            msg = f"`PATH_TO_SNAPSHOT`='{PATH_TO_SNAPSHOT}' does not exist."
            FileNotFoundError(msg)
        return PATH_TO_SNAPSHOT

    try:
        PATH_TO_JOB = _path_to_job(**kwargs)
    except ValueError:
        msg = (
            "Either `job_key`, `job_id`, `PATH_TO_JOB`, "
            "or `PATH_TO_SNAPSHOT` must be passed ",
            "as keyword arguments.",
        )
        raise ValueError(msg)

    if "date" in kwargs.keys():
        date = kwargs["date"]
        filename = f"snapshot.{date.strftime('%Y-%m-%d')}.tgz"
    else:
        try:
            # completed_snapshots.txt is produced in FRED 7.9 +
            with open(
                os.path.join(PATH_TO_JOB, "OUT", "completed-snapshots.txt"), "r"
            ) as f:
                last_snapshot = f.readlines()[-1].strip()
        except FileNotFoundError:
            last_snapshot = "snapshot.tgz"  # not available in FRED 7.9 +
        filename = last_snapshot

    PATH_TO_SNAPSHOT = os.path.join(PATH_TO_JOB, "OUT", filename)
    PATH_TO_SNAPSHOT = os.path.abspath(PATH_TO_SNAPSHOT)

    if not os.path.isfile(PATH_TO_SNAPSHOT):
        msg = (
            f"The requested snapshot, {filename}, does not exist in "
            f"{os.path.join(PATH_TO_JOB, 'OUT')}."
        )
        raise FileNotFoundError(msg)

    return PATH_TO_SNAPSHOT


class Snapshot(object):
    """
    A class that represents a FRED snapshot.

    Parameters
    ----------
    date : dt.date, optional
            a simulation snapshot date

    PATH_TO_SNAPSHOT : Pathlike, optional

    Attributes
    ----------
    path_to_snapshot : Path
        a path to a FRED snapshot file
    date : dt.date
        the snapshot simulation date
    """

    def __init__(self, date=None, **kwargs) -> None:
        """
        Initialize a FRED snapshot object
        """

        self.path_to_snapshot = _path_to_snapshot(date=date, **kwargs)
        self.filename = os.path.basename(self.path_to_snapshot)

    def delete(self, verbose=False):
        """ """
        # delete snapshot file
        try:
            if verbose:
                print(f"deleting {self.path_to_snapshot}.")
            os.remove(self.path_to_snapshot)
        except PermissionError:
            msg = (
                f"The snapshot could not be deleted."
                f"You may not have permission to modify {self.path_to_snapshot}."
            )
            raise PermissionError(msg)
        except FileNotFoundError:
            msg = (
                f"{self.path_to_snapshot} does not exist. It may have been "
                "previously deleted."
            )
            raise FileNotFoundError(msg)

    @property
    def date(self) -> Union[None, dt.date]:
        """
        the simulation snapshot date

        Notes
        -----
        In a version of FRED prior to 7.9, the latest snapshot produced in a
        FRED job was stored with a file name ``snapshot.tgz``. This is no
        longer the case as of FRED 7.9. In a future release, support for
        ``snapshot.tgz`` with an associate date of ``None`` will be
        deprecated.
        """

        if len(self.filename.split(".")) == 3:
            date_str = self.filename.split(".")[1]
            self._date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            self._date = None
            msg = (
                f"There is no simulation date associated with the "
                f"snapshot:{self.filename}."
            )
            warn(msg)
        return self._date
