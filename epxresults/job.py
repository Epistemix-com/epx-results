"""
This module contains tools for representing FRED jobs. FRED jobs are
collections of FRED simulation runs.
"""

from itertools import chain, repeat
import logging
import os
import re
import datetime as dt
from typing import Dict, List, Literal, Tuple
import pandas as pd
import shutil
from pathlib import Path
from .utils import (
    _path_to_job,
    _path_to_results,
    return_job_id,
    return_job_run_ids,
    _is_valid_results_directory,
    load_local_job_keys
)
from .insert import _write_local_keys
from .run import FREDRun
from .snapshot import Snapshot

__all__ = ['FREDJob']
__author__ = ['Duncan Campbell']

logger = logging.getLogger(__name__)


# job directory storing output for different intervals
_INTERVAL_DIRS = {'daily': 'OUT/PLOT/DAILY',
                  'weekly': 'OUT/PLOT/WEEKLY'}
OutputInterval = Literal['daily', 'weekly']

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
            a FRED job key
        job_id : int
            a FRED job ID
        PATH_TO_JOB : PathLike
            a path to a FRED job.

    Other Parameters
    ----------------
    **kwargs: dict
        additional optional keyword arguments:

        FRED_RESULTS : PathLike
            the full path to a local FRED results directory
        FRED_HOME : PathLike
            the full path to a local FRED home directory.

    Attributes
    ----------
    status : str:
        status of the job (e.g. 'FINISHED')
    runs : Dict[int, FREDRun]
        collection of runs belonging to the job. Keys are the FRED run
        ID numbers, values are `FREDRun` objects representing the runs.
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
    get_job_date_table :
        Mapping of simulation days to simulation dates.

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

    will return an object, ``job``, that provides access to the
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
        self._snapshot_map = self._set_snapshot_map()
        self._results_dir = self._fred_results(**kwargs)

    def _fred_results(self, **kwargs) -> Path:
        """
        The FRED results directory associated with the job

        Notes
        -----
        If no results directory is associated with the job, `None` will be
        returned.
        """

        if 'PATH_TO_JOB' in kwargs.keys():
            root = Path(self.path_to_job).parent.parent
            if _is_valid_results_directory(root):
                return root
            else:
                return None
        else:
            return Path(_path_to_results(**kwargs))

    def delete(self, verbose: bool = False) -> None:
        """
        Delete the FRED job results on your local file system. Deleting a job
        is irreversible.

        Parameters
        ----------
        verbose : bool
            print progress and status information

        Notes
        -----
        This method both removes the ``self.path_to_job`` directory on a file
        system and updates the local results ``KEY`` and ``ID`` file if the job
        is contained within a valid local FRED results directory.

        Raises
        ------
        PermissionError
            If the user has insufficient privileges to remove the FRED job from
            the local file system.
        FileNotFoundError
            If the job has already been removed from the local file system
            and/or the job is contained within in a non-standard local FRED
            results directory.
        """

        # update job keys in local results directory
        if self._results_dir is not None:
            if verbose:
                print(f"updating local results {self._results_dir}.")
            local_keys = load_local_job_keys(FRED_RESULTS=self._results_dir)
            try:
                del local_keys[self.job_key]
            except KeyError:
                if verbose:
                    msg = (f"no job key matching {self.job_key} found in "
                           f"the local FRED results {self._results_dir}.")
            try:
                _write_local_keys(local_keys, FRED_RESULTS=self._results_dir)
            except PermissionError:
                msg = (f"job {self.job_key} could not be deleted from the "
                       f"local FRED results directory {self._results_dir}. "
                       f"You may not have permission to modify the directory.")
                raise PermissionError(msg)

        # delete job results directory
        try:
            if verbose:
                print(f"deleting {self.path_to_job}.")
            shutil.rmtree(self.path_to_job)
        except PermissionError:
            msg = (f"job {self.job_key} could not be deleted."
                   f"You may not have permission to modify {self.path_to_job}")
            raise PermissionError(msg)
        except FileNotFoundError:
            msg = (f"{self.path_to_job} does not exist. It may have been "
                   "previously deleted.")
            raise FileNotFoundError(msg)

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
            a path to a FRED job

        Returns
        -------
        job_id : int
            a FRED job ID

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
            a list of FRED condition names

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
        count_type: str = "cumulative",
        interval: OutputInterval = "daily",
        format: str = "long",
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

        format : str, optional
            the default DataFrame format, either 'wide' or 'long'. By default,
            long format DataFrames are returned.

        Returns
        -------
        state_table : pandas.DataFrame
            a pandas DataFrame containing `state` counts for each run in a FRED
            job

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
        >>> df = job.get_job_state_table(condition='INF', state='E')
        """

        # check `count_type` keyword argument
        if count_type not in _count_types.keys():
            msg = f"`count_type` must be one of {_count_types.keys()}"
            raise ValueError(msg)

        prefix = _count_types[count_type]
        fname = f"{condition}.{prefix}{state}.csv"
        path_to_file = os.path.join(
            self.path_to_job, self._interval_path_component(interval), fname
        )

        # check if condition is available
        if condition not in self.conditions:
            msg = (
                f"{condition} is not available to load. "
                "See `self.conditions` for a list of available conditions."
            )
            raise ValueError(msg)

        if not os.path.isfile(path_to_file):
            msg = (
                f"'{path_to_file}' not found. `state`={state} may not be "
                f"a valid state in the FRED condition '{condition}'. "
                "Alternatively, the output for the requested interval "
                "may not be turned on."
            )
            raise ValueError(msg)

        df = self._read_plot_data_file(path_to_file, interval)
        self._validate_table_format(format)
        if format == "long":
            df = self._convert_wide_plot_table_to_long(df, count_type)

        return df

    def get_job_variable_table(
        self,
        variable: str,
        interval: OutputInterval = "daily",
        format: str = "long",
    ) -> pd.DataFrame:
        """
        Return a table of `variable` values for each run in a job.

        Parameters
        ----------
        variable : str
            a FRED global variable name

        interval : str
            the output interval

        format : str, optional
            the default DataFrame format, either 'wide' or 'long'. By default,
            long format DataFrames are returned.

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
        number of agents who are susceptible to the ``INF`` condition,
        infected, and recovered.

        The daily number of infected agents in each run on each day of the
        simulation can be loaded as:

        >>> from epxresults import FREDJob
        >>> job = FREDJob(job_key='simpleflu')
        >>> df = job.get_job_variable_table(variable='Infected')
        """

        # check if variable is available
        if variable not in self.global_variables:
            msg = (
                f"{variable} is not available to load. See "
                "`self.global_variables` for a list of "
                "available variables."
            )
            raise ValueError(msg)

        fname = f"FRED.{variable}.csv"
        path = os.path.join(
            self.path_to_job, self._interval_path_component(interval), fname
        )

        df = self._read_plot_data_file(path, interval)
        self._validate_table_format(format)
        if format == "long":
            df = self._convert_wide_plot_table_to_long(df, variable)

        return df

    def get_job_rt_table(
        self, condition: str, interval: OutputInterval = "daily", format: str = "long"
    ) -> pd.DataFrame:
        """Time series of the reproductive rate, R(t), of the given
        transmissible condition.

        See `FRED documentation`_ for further details of the definition of this
        quantity.

        .. _FRED documentation: https://docs.epistemix.com/projects/fred-sims/en/latest/sim-guide/chapter2.html#reproductive-rate-rt

        Examples
        --------
        >>> job = FREDJob(job_key='simpleflu')
        >>> df = job.get_job_rt_table('INF').head()
        >>> df  # doctest: +SKIP
           run  sim_day        Rt
        0    1        0  1.700000
        1    1        1  0.000000
        2    1        2  3.500000
        3    1        3  2.500000
        4    1        4  2.666667
        """
        self._validate_table_format(format)
        filename = f"{condition}.Rt.csv"

        try:
            df = self._read_plot_data_file(filename, interval)
        except FileNotFoundError:
            logger.error(
                f"Rt output data could not be found for condition {condition} "
                f"at {interval} frequency. Check expected outputs are on and "
                f"that condition is transmissible."
            )
        if format == "long":
            df = self._convert_wide_plot_table_to_long(df, "Rt")
        return df

    def get_job_gt_table(
        self, condition: str, interval: OutputInterval = "daily", format: str = "long"
    ) -> pd.DataFrame:
        """Time series of the generation time, G(t), of the given
        transmissible condition.

        See `FRED documentation`_ for further details of the definition of this
        quantity.

        .. _FRED documentation: https://docs.epistemix.com/projects/fred-sims/en/latest/sim-guide/chapter2.html#generation-time-gt

        Examples
        --------
        >>> job = FREDJob(job_key='simpleflu')
        >>> df = job.get_job_gt_table('INF').head()
        >>> df  # doctest: +SKIP
           run  sim_day        Gt
        0    1        0  5.676471
        1    1        1  0.000000
        2    1        2  5.404762
        3    1        3  5.291667
        4    1        4  3.130208
        """
        self._validate_table_format(format)
        filename = f"{condition}.Gt.csv"
        try:
            df = self._read_plot_data_file(filename, interval)
        except FileNotFoundError:
            logger.error(
                f"Gt output data could not be found for condition {condition} "
                f"at {interval} frequency. Check expected outputs are on and "
                f"that condition is transmissible."
            )
        if format == "long":
            df = self._convert_wide_plot_table_to_long(df, "Gt")
        return df

    def _read_plot_data_file(
        self, filename: str, interval: OutputInterval
    ) -> pd.DataFrame:
        """Read a file from the ``JOB/<n>/OUT/PLOT/<interval>`` directory for
        the job.

        FRED outputs summary tables for all state, global variable, and special
        variable (e.g Popsize, Rt) outputs in the
        ``JOB/<n>/OUT/PLOT/<interval>`` directory. These files have a row for
        each sim day, and include some summary statistics, as well as a column
        for each run.

        This utility function reads the given file for the given output
        interval, and returns a table with a column for each run, and the
        sim_day as index.

        Examples
        --------
        >>> job._read_plot_file('FRED.my_var.txt', 'daily').head()  # doctest: +SKIP
                 RUN1  RUN2  RUN3  RUN4  RUN5
        sim_day
        0         0.0   0.0   0.0   0.0   0.0
        1         0.0   0.0   0.0   0.0   0.0
        2         0.0   0.0   0.0   0.0   0.0
        3         0.0   0.0   0.0   0.0   0.0
        4         0.0   0.0   0.0   0.0   0.0
        """
        filepath = os.path.join(
            self.path_to_job, self._interval_path_component(interval), filename
        )
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"{filepath} does not exist.")
        pattern = re.compile("RUN[0-9]+")
        df = pd.read_csv(filepath, usecols=lambda x: pattern.match(x))
        df.index.name = "sim_day"
        return df

    @staticmethod
    def _convert_wide_plot_table_to_long(
        wide_plot_df: pd.DataFrame, varname: str
    ) -> pd.DataFrame:
        """Given FRED plot table in wide format, convert to tidy long format.

        FRED generates output files for variables in the
        ``JOB/<n>/OUT/PLOT/<interval>`` that are in a 'wide' format that has a
        row per sim day and a column per run. This utility function converts
        dataframes in the wide format to dataframes in 'long' format with
        a row for each (run, sim day) pair and columns:

        * run
        * sim_day
        * <name of variable>

        Examples
        --------
        >>> wide_df = job._read_plot_file('FRED.my_var', 'daily')  # doctest: +SKIP
        >>> job._convert_wide_plot_table_to_long(wide_df, 'my_var')  # doctest: +SKIP
           run  sim_day  my_var
        0    1        0     0.0
        1    1        1     0.0
        2    1        2     0.0
        3    1        3     0.0
        4    1        4     0.0
        """
        wide_plot_df["sim_day"] = wide_plot_df.index
        df = pd.wide_to_long(wide_plot_df, ["RUN"], i="sim_day", j="run")
        df = df.rename(columns={"RUN": varname})
        df = df.swaplevel().sort_index().reset_index()
        return df

    @staticmethod
    def _validate_table_format(format: str) -> None:
        valid_formats = ["wide", "long"]
        if format not in valid_formats:
            raise ValueError(
                f"{format} is not a valid table format. Use one "
                f"of: {', '.join(valid_formats)}"
            )

    def _interval_path_component(self, interval: str) -> str:
        """Get path component needed to find results for given reporting
        interval from within the FRED job directory, ``self.path_to_job``.
        """
        if interval not in _INTERVAL_DIRS.keys():
            raise ValueError(
                f"'{interval}' is not a valid interval. Provide one of "
                f"{', '.join(_INTERVAL_DIRS.keys())}"
            )
        if not os.path.isdir(
            os.path.join(self.path_to_job, _INTERVAL_DIRS[interval])
        ):
            raise ValueError(
                f"'{interval}' results were not generated for this job"
            )
        return _INTERVAL_DIRS[interval]

    def _parse_snapshots(self) -> List[str]:
        """
        collect snapshot filenames in the FRED job.
        """

        snapshots = [f for f in
                     os.listdir(os.path.join(self.path_to_job, 'OUT'))
                     if re.match(r'snapshot.*\.tgz$', f)]
        return snapshots

    def _set_snapshot_map(self) -> Dict[dt.date, Snapshot]:
        """
        build a dictionary which maps dates to snapshots
        """
        self._snapshot_map = {}
        for snapshot_file in self._parse_snapshots():
            snapshot = Snapshot(PATH_TO_SNAPSHOT=os.path.join(self.path_to_job,
                                                              'OUT',
                                                              snapshot_file))
            if snapshot.date is not None:
                self._snapshot_map[snapshot.date] = snapshot
            else:
                pass
        return self._snapshot_map

    @property
    def snapshots(self) -> List[Snapshot]:
        """
        a list of snapshots associated with this job
        """

        self._snapshots = {}
        self._snapshot_map = self._set_snapshot_map()
        return list(self._snapshot_map.values())

    def get_snapshot(self, date) -> Snapshot:
        """
        Return a snapshot for a given simulation date.

        Parameters
        ----------
        date : dt.date
            a datetime date object

        Returns
        -------
        snapshot : Snapshot
            a FRED snapshot object

        Raises
        ------
        KeyError
            raised if there is not snapshot for `date` in this FRED job

        Examples
        --------
        In the ``'simpleflu'`` model, a snapshot is generated on simulation
        date January 31, 2020. This snapshot can be retrieved by:

        >>> import datetime as dt
        >>> from epxresults import FREDJob
        >>> job = FREDJob(job_key='simpleflu')
        >>> snap = job.get_snapshot(date=dt.date(2020, 1, 22))
        """

        self._snapshot_map = self._set_snapshot_map()

        try:
            return self._snapshot_map[date]
        except KeyError:
            msg = (f"There is no snapshot available for simulation "
                   f"date: {date}.")
            raise KeyError(msg)

    def get_job_date_table(self) -> pd.DataFrame:
        """Table mapping sim days to sim dates for all runs in the job.

        Returns
        -------
        pd.DataFrame
            Table with columns ``run``, ``sim_day``, and ``sim_date``.
            ``sim_date`` is the date represented by ``sim_day`` in
            the simulation, and ``run`` is the FRED run number. Normally
            we expect all runs in a job to have the same ``sim_day`` and
            ``sim_date`` mappings but this is not enforced.

        Examples
        --------
        >>> from epxresults import FREDJob
        >>> job = FREDJob(job_key='simpleflu')
        >>> df = job.get_job_date_table()
        """
        return (
            pd.DataFrame.from_records(
                chain(*[
                    zip(repeat(i), self.runs[i].sim_days, self.runs[i].sim_dates)
                    for i in self.runs.keys()
                ]),
                columns=["run", "sim_day", "sim_date"]
            )
            .assign(sim_date=lambda df: pd.to_datetime(df["sim_date"]))
        )

    def __str__(self) -> str:
        return (
            f"FREDJob(job_key={self.job_key}, job_id={self.job_id}, "
            f"path_to_job={self.path_to_job})"
        )
