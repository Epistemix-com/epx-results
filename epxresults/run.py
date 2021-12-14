"""
"""

import os
import re
import datetime as dt
from typing import (Dict, List, Optional, Tuple, Union)
from .utils import (_path_to_run, _value_str_to_value, _read_fred_csv)
from .run_logs import _read_fred_run_log


__all__ = ['FREDRun']
__author__ = ['Duncan Campbell']


class FREDRun(object):
    """
    A class that provides access to results associated with a FRED run

    Parameters
    ----------
    run_id : int, optional
        a FRED run ID

    **kwargs: dict
        One of the following keyword parameters must be provided when
        intializing a FREDrun object:

        job_key : string
            A FRED job key.
        job_id : int
            A FRED job ID.
        PATH_TO_JOB : PathLike
            a path to a FRED job.
        PATH_TO_RUN : PathLike
            a path to a FRED run.

    Other Parameters
    ----------------
    **kwargs: dict
        additonal optional keyword arguments:

        FRED_RESULTS : PathLike
            the full path to a local FRED results directory
        FRED_HOME : PathLike
            the full path to a local FRED home directory.

    Attributes
    ----------
    parameters
    progress
    path_to_run : Path
    run_id : int
    sim_days : List[int]
        a list of simulation days, starting at 0.
    sim_dates : List[int]
        a list of simulaton date stamps in the format YYYYMMDD

    Methods
    -------
    get_log :
        get a FRED run log
    get_csv_output :
        get a CSV file output from a FRED run

    Notes
    -----
    For details on how the path to a FRED run is resolved,
    see :py:func:`epxresults.utils._path_to_run`.
    """

    def __init__(self, run_id, **kwargs) -> None:
        """
        Initialize a FRED run object.
        """

        self.path_to_run = _path_to_run(run_id=run_id, **kwargs)
        self.run_id = run_id
        self.sim_days, self.sim_dates = self._load_sim_dates()

    @property
    def parameters(self) -> Dict[str, Union[int, float, str]]:
        """
        a dictionary of run parameters
        """

        self._parameters = self._load_parameters()
        return self._parameters

    def _load_parameters(self) -> Dict[str, Union[int, float, str]]:
        """
        Process and return a dictionary of run parameters.

        Returns
        -------
        params : Dict
            a dictionary of FRED run parameters
        """
        fname = os.path.join(self.path_to_run, 'parameters.txt')
        param_file = open(fname, 'r')
        lines = param_file.readlines()

        d = {}
        for line in lines:
            line = line.strip()
            key, value = line.split(' = ')
            d[key] = _value_str_to_value(value)
        return d

    def _load_sim_dates(self) -> Tuple[List[int], List[dt.date]]:
        """
        Return a list of simulation days and dates.

        Returns
        -------
        sim_days : List
            a list of integers

        sim_dates : List
            a list of datetime date objects
        """

        fname = os.path.join(self.path_to_run, 'DAILY/Date.txt')

        sim_dates = []
        sim_days = []
        with open(fname, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                sim_day, date_str = line.split(' ')
                sim_days.append(int(sim_day))
                sim_dates.append(
                    dt.datetime.strptime(date_str, '%Y-%m-%d').date()
                    )
        return sim_days, sim_dates

    def get_log(self) -> List[str]:
        """
        Return a FRED run log

        Returns
        -------
        log : List
            a list of lines in the run log
        """
        log = _read_fred_run_log(self.run_id, PATH_TO_RUN=self.path_to_run)
        return log

    @property
    def progress(self) -> float:
        """
        percentage of total simulation days completed
        """
        self._progress = self._load_progress()
        return self._progress

    def _load_progress(self) -> float:
        """
        Load progress from `progress.txt`
        """

        fname = os.path.join(self.path_to_run, 'progress.txt')
        progress_pattern = re.compile(r"\((\d+%)\)")

        progress = []
        with open(fname, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                line = line.strip()
                p = progress_pattern.findall(line)[0]
                progress.append(float(p.strip('%')))
        return progress[-1]

    def get_csv_output(self, filename):
        """
        Load CSV output from a FRED run.

        Parameters
        ----------
        filename : str
            a csv filename

        Returns
        -------
        csv_table : pandas.DataFrame
            a pandas DataFrame containing the contents of `filename`.

        Examples
        --------
        In the ``'simpleflu'`` model, infection events are recorded in
        ``infections.csv``, which for each infection, records the infcted
        agent's ID, the date of exposure, the agent's age, and the agent's sex.

        The table of infection events can be loaded for run 1:

        >>> from epxresults import FREDJob
        >>> job = FREDJob(job_key='simpleflu')
        >>> run = job.runs[1]
        >>> run.get_csv_output('infections.csv')
                   id      date  age  sex
        0   ...
        ...
        """
        path_to_csv = os.path.join(self.path_to_run, 'CSV', filename)
        return _read_fred_csv(path_to_csv)
