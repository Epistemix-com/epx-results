"""
"""

import os
import re
from typing import (Dict, List, Optional, Tuple, Union)
import pandas as pd
from .utils import (_path_to_job, _path_to_results,
                    return_job_id, return_job_run_ids)
from .run import FREDRun

__all__ = ['FREDJob']
__author__ = ['Duncan Campbell']


# job directory storing output for different intervals
_interval_dirs = {'daily': 'OUT/PLOT/DAILY',
                  'Weekly': 'OUT/PLOT/WEEKLY'}
# prefix associated with different state counts
_count_types = {'count': '',
                'new': 'new',
                'cumulative': 'tot'}


class FREDJob(object):
    """
    A class that provides access to results associated with a FRED job

    Parameters
    ----------
    **kwargs: dict
        One of the following keyword parameters must be provided when
        intializing a FREDjob object:

        job_key : string
            A FRED job key.
        job_id : int
            A FRED job ID.
        PATH_TO_JOB : PathLike
            a path to a FRED job.

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
    status
    runs
    path_to_job : Path
        a path to a FRED job results directory
    job_key : str
        a FRED job key
    job_id : int
        a FRED job ID
    conditions : List[str]
        a list of conditions with available output
    global_variables : List[str]
        a list of global variables with available output

    Methods
    -------
    get_job_variable_table :
        Get a table of global variable values for each run in a job.
    get_job_state_table :
        Get a table of state counts in a condition for each run in a job.

    Notes
    -----
    For details on how the path to a FRED job is resolved,
    see :py:func:`epxresults.utils._path_to_job`.

    Examples
    --------
    A ``FREDJob`` object may be instantiated using a FRED Job key. For example,
    if there is a FRED job with a key ``'simpleflu'``, then,

    >>> from epxresults import FREDJob
    >>> job = FREDJob(job_key='simpleflu')

    will provide an object, ``job``, that provides access to the
    results associated with ``'simpleflu'``.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize a FRED job object
        """

        self.path_to_job = _path_to_job(**kwargs)
        self.job_key = self._return_job_key()
        self.job_id = self._return_job_id(**kwargs)
        self.conditions, self.global_variables = self._parse_vars()

    @property
    def status(self) -> str:
        """
        the status of a FRED job
        """

        fname = os.path.join(self.path_to_job, 'META/STATUS')
        with open(fname) as f:
            status = f.readline().strip()
        self._status = status
        return status

    @property
    def runs(self) -> Dict[int, FREDRun]:
        """
        a dictionary of FRED run objects associated with this job
        """

        if self.status != 'FINISHED':
            self._runs = {}
            return self._runs
        else:
            self._runs = {}
            run_ids = return_job_run_ids(job_id=self.job_id,
                                         PATH_TO_JOB=self.path_to_job)
            for run_id in run_ids:
                self._runs[run_id] = FREDRun(run_id=run_id, job_id=self.job_id,
                                             PATH_TO_JOB=self.path_to_job)
            return self._runs

    def _return_job_key(self) -> str:
        """
        Return a FRED job key

        Returns
        -------
        job_key : str
            A FRED job key associated with a FRED job.
        """

        fname = os.path.join(self.path_to_job, 'META/KEY')
        with open(fname) as f:
            key = f.readline().strip()
        return key

    def _return_job_id(self, **kwargs) -> int:
        """
        Return the FRED job ID associated with a FRED job.

        Parameters
        ----------
        PATH_TO_JOB : PathLike
            a path to a FRED job.

        Returns
        -------
        job_id : int
            A FRED job ID.

        Notes
        -----
        If a ``FREDJob`` is instantiated with a path to a FRED job directory,
        then we do not assume that there is a job ID associated with the
        FRED Job since the job ID is only used when naming the FRED job
        directory.
        """
        if 'PATH_TO_JOB' in kwargs.keys():
            job_id = None
        else:
            FRED_RESULTS = _path_to_results(**kwargs)
            job_id = return_job_id(job_key=self.job_key,
                                   FRED_RESULTS=FRED_RESULTS)
        return job_id

    def _parse_vars(self) -> Tuple[List, List]:
        """
        Parse the ``VARS`` file in the ``OUT/PLOT/VARS`` directory within the
        FRED job directory to infer the list of available conditions and global
        variables.

        Returns
        -------
        conditions : List
            a list of FRED conditon names

        global_variables : List
            a list of global variable names
        """
        fname = os.path.join(self.path_to_job, 'OUT/PLOT/VARS')

        conditions = set()
        global_variables = set()
        with open(fname, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                try:
                    condition, state = line.split('.')
                    if condition == 'FRED':
                        variable = state
                        global_variables.add(variable)
                    else:
                        conditions.add(condition)
                except (ValueError, NameError):
                    pass

        return conditions, global_variables

    def get_job_state_table(
            self,
            condition: str,
            state: str,
            count_type: str = 'cumulative',
            interval: str = 'daily'
            ) -> pd.DataFrame:
        """
        Return a table of state counts in `condition` for each run in a job.

        Parameters
        ----------
        condition : str
            a FRED condition name

        state : str
            a state name in `condition`

        count_type : str, optional
            the type of count returned, one of 'count', 'new', or 'cumulative'.
            'count' returns the number of agents in a state at midnight
            on the simulation day. 'new' returns the number of times any agent
            entered that state on the simulation day. 'cumulative' returns
            the cumulative number of times any agent has entered the state
            by the simulation day.

        interval : str, optional
            the interval over which state counts are performed.
            one of 'daily' or 'weekly'.

        Returns
        -------
        state_table : pandas.DataFrame
            a pandas DataFrame containing `state` counts
            for each run in a FRED job.

        Notes
        -----
        Only conditions with the property ``output=1`` will be available
        with this method.

        Examples
        --------
        In the ``'simpleflu'`` model, the ``INF`` condition represents a
        contagious influenza. The cumulative number of agents exposed to this
        condition in each run on each day of the simulation can be loaded as:

        >>> from epxresults import FREDJob
        >>> job = FREDJob(job_key='simpleflu')
        >>> job.get_job_state_table(condition='INF', state='E')
           RUN1  RUN2  RUN3
        0 ...
        1 ...
        ...
        """

        prefix = _count_types[count_type]
        fname = f"{condition}.{prefix}{state}.csv"
        path_to_file = os.path.join(self.path_to_job,
                                    f"{_interval_dirs[interval]}",
                                    f"{fname}")

        # check if condition is available
        if condition not in self.conditions:
            msg = (f"{condition} is not availabe to load. "
                   "See `self.conditions` for a list of available conditions.")
            raise ValueError(msg)

        if not os.path.isfile(path_to_file):
            msg = (f"'{path_to_file}' not found. `state`={state} may not be "
                   f"a valid state in the FRED condition '{condition}'.")
            raise ValueError(msg)

        pattern = re.compile("RUN[0-9]+")
        return pd.read_csv(path_to_file, usecols=lambda x: pattern.match(x))

    def get_job_variable_table(
            self,
            variable: str,
            interval: str = 'daily'
            ) -> pd.DataFrame:
        """
        Return a table of `variable` values for each run in a job.

        Parameters
        ----------
        variable : str
            FRED global variable name

        interval : str
            the output inteval

        Returns
        -------
        var_table : pandas.DataFrame
            a pandas DataFrame containing `variable` values
            for each run in the job.

        Notes
        -----
        Only global variables with output turned on, ``<variable>.output=1``,
        will be available with this method.

        Examples
        --------
        In the ``'simpleflu'`` model, there are a set of global variables,
        ``Susceptible``, ``Infected``, and ``Recovered`` that track the daily
        number of agents who are susecptible to the ``INF`` condition,
        infected, and recoered.

        The daily number of infected agents in each run on each day of the
        simualtion can be loaded as:

        >>> from epxresults import FREDJob
        >>> job = FREDJob(job_key='simpleflu')
        >>> job.get_job_variable_table(variable='Infected')
           RUN1  RUN2  RUN3
        0   ...
        1   ...
        ...
        """

        # check if variable is available
        if variable not in self.global_variables:
            msg = (f"{variable} is not available to load. See "
                   "`self.global_variables` for a list of "
                   "available variables.")
            raise ValueError(msg)

        fname = f"FRED.{variable}.csv"
        path = os.path.join(self.path_to_job,
                            f"{_interval_dirs[interval]}",
                            f"{fname}")

        pattern = re.compile("RUN[0-9]+")
        return pd.read_csv(path, usecols=lambda x: pattern.match(x))
