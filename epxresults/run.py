"""
This module provides tools for representing FRED simulation "runs".
"""

import os
import re
import pandas as pd
import datetime as dt
import networkx as nx
from typing import Dict, List, Tuple, Union
from .utils import _path_to_run, _value_str_to_value, _read_fred_csv
from .run_logs import _read_fred_run_log


__all__ = ["FREDRun"]
__author__ = ["Duncan Campbell"]


_interval_dirs = {"daily": "DAILY", "Weekly": "WEEKLY"}
# prefix associated with different state counts
_count_types = {"count": "", "new": "new", "cumulative": "tot"}


class FREDRun(object):
    """
    A class that provides access to results associated with a FRED run

    Parameters
    ----------
    run_id : int, optional
        a FRED run ID

    **kwargs: dict
        One of the following keyword parameters must be provided when
        intializing a `FREDrun` object:

        job_key : string
            a FRED job key
        job_id : int
            a FRED job ID
        PATH_TO_JOB : PathLike
            a path to a FRED job
        PATH_TO_RUN : PathLike
            a path to a FRED run

    Other Parameters
    ----------------
    **kwargs: dict
        additional optional keyword arguments:

        FRED_RESULTS : PathLike
            the full path to a local FRED results directory
        FRED_HOME : PathLike
            the full path to a local FRED home directory

    Attributes
    ----------
    parameters
    progress
    path_to_run : Path
        a full path to a FRED run directory
    run_id : int
        a FRED run ID
    sim_days : List[int]
        a list of simulation days, starting at 0
    sim_dates : List[int]
        a list of simulation date stamps in the format YYYYMMDD

    Methods
    -------
    get_log :
        get a FRED run log
    get_state :
        get state counts in a condition
    get_variable :
        get the value of a global variable
    get_list_variable :
        get the value of a global list variable
    get_table_variable :
        get the value of a table variable
    get_list_table_variable :
        get the value of a list_table variable
    get_csv_output :
        get a CSV file output from a FRED run
    get_network :
        import a FRED network as a NetworkX Graph

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
        fname = os.path.join(self.path_to_run, "parameters.txt")
        param_file = open(fname, "r")
        lines = param_file.readlines()

        d = {}
        for line in lines:
            line = line.strip()
            key, value = line.split(" = ")
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

        fname = os.path.join(self.path_to_run, "DAILY/Date.txt")

        sim_dates = []
        sim_days = []
        with open(fname, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                sim_day, date_str = line.split(" ")
                sim_days.append(int(sim_day))
                sim_dates.append(dt.datetime.strptime(date_str, "%Y-%m-%d").date())
        return sim_days, sim_dates

    def get_log(self) -> List[str]:
        """
        Return a FRED run log.

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
        Load progress from `progress.txt`.
        """

        fname = os.path.join(self.path_to_run, "progress.txt")
        progress_pattern = re.compile(r"\((\d+%)\)")

        progress = []
        with open(fname, "r") as f:
            lines = f.readlines()
            for line in lines[1:]:
                line = line.strip()
                p = progress_pattern.findall(line)[0]
                progress.append(float(p.strip("%")))
        return progress[-1]

    def get_state(
        self,
        condition: str,
        state: str,
        count_type: str = "cumulative",
        interval: str = "daily",
    ) -> pd.Series:
        """
        Return an series of state counts in `condition`.

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

        interval : str
            the output interval

        Returns
        -------
        ser : pd.Series
            a series of integers containing `state` counts

        Examples
        --------
        In the ``'simpleflu'`` model, the ``INF`` condition represents a
        contagious influenza. The cumulative number of agents exposed to this
        condition on each day of the simulation can be loaded as:

        >>> from epxresults import FREDRun
        >>> run = FREDRun(job_key='simpleflu', run_id=1)
        >>> ser = run.get_state(condition='INF', state='E')
        """

        # check `count_type` keyword argument
        if count_type not in _count_types.keys():
            msg = f"`count_type` must be one of {_count_types.keys()}"
            raise ValueError(msg)

        # check `interval` keyword argument
        if interval not in _interval_dirs.keys():
            msg = f"`interval` must be one of {_interval_dirs.keys()}"
            raise ValueError(msg)

        prefix = _count_types[count_type]

        fname = f"{condition}.{prefix}{state}.txt"
        fname = os.path.join(self.path_to_run, _interval_dirs[interval], fname)

        if not os.path.isfile(fname):
            msg = (
                f"No output found for {condition}.{prefix}{state} in "
                f"{os.path.join(self.path_to_run, _interval_dirs[interval])}."
            )
            raise FileNotFoundError(msg)

        # read in data from file
        arr = []
        with open(fname, "r") as f:
            lines = f.readlines()
            count = 0
            for line in lines:
                sim_time_unit, value = line.split(" ")
                arr.append(_value_str_to_value(value))
                count += 1
        return pd.Series(arr, dtype="int")

    def get_variable(self, variable: str, interval: str = "daily") -> pd.Series:
        """
        Return an series of values for a global variable.

        Parameters
        ----------
        variable : str
            a FRED global variable name

        interval : str
            the output interval

        Returns
        -------
        ser : pd.Series
            a series of floats containing `variable` values

        Examples
        --------
        In the ``'simpleflu'`` model, there are a set of global variables,
        ``Susceptible``, ``Infected``, and ``Recovered`` that track the daily
        number of agents who are susceptible to the ``INF`` condition,
        infected, and recovered.

        The daily number of infected agents in run on each day of the
        simulation can be loaded as:

        >>> from epxresults import FREDRun
        >>> run = FREDRun(job_key='simpleflu', run_id=1)
        >>> ser = run.get_variable(variable='Infected')
        """

        # check `interval` keyword argument
        if interval not in _interval_dirs.keys():
            msg = f"`interval` must be one of {_interval_dirs.keys()}"
            raise ValueError(msg)

        fname = f"FRED.{variable}.txt"
        fname = os.path.join(self.path_to_run, _interval_dirs[interval], fname)

        if not os.path.isfile(fname):
            msg = (
                f"No output found for {variable} in "
                f"{os.path.join(self.path_to_run, _interval_dirs[interval])}"
            )
            raise FileNotFoundError(msg)

        # read in data from file
        arr = []
        with open(fname, "r") as f:
            lines = f.readlines()
            count = 0
            for line in lines:
                sim_time_unit, value = line.split(" ")
                arr.append(_value_str_to_value(value))
                count += 1
        return pd.Series(arr, dtype="float")

    def get_list_variable(
        self,
        variable: str,
        sim_day: int = None,
    ) -> pd.Series:
        """
        Return an series of values for a global list variable.

        Parameters
        ----------
        variable : str
            a FRED global list variable name

        sim_day : int
            the simulation day. By default, the last output will be returned.

        Returns
        -------
        arr : pd.Series
            a series of floats containing `variable` values

        Examples
        --------
        In the ``'simpleflu'`` model, there are a set of global list variables,
        ``g_list_of_case_count_by_age`` and ``g_list_of_symp_count_by_age``
        that count the number agents who are infected and symptomatic in age
        bins.

        The number of cases in age bins can then be loaded as

        >>> from epxresults import FREDRun
        >>> run = FREDRun(job_key='simpleflu', run_id=1)
        >>> ser = run.get_list_variable(variable='g_list_of_case_count_by_age')
        """

        if sim_day is not None:
            fname = f"{variable}-{sim_day}.txt"
        else:
            fname = f"{variable}.txt"
        fname = os.path.join(self.path_to_run, "LIST", fname)

        if not os.path.isfile(fname):
            msg = (
                f"The requested output for `{variable}` was not found in "
                f"{os.path.join(self.path_to_run, 'LIST')}"
            )
            raise FileNotFoundError(msg)

        # read in data from file
        arr = []
        with open(fname, "r") as f:
            lines = f.readlines()
            count = 0
            for line in lines[1:]:
                value = line.strip()
                arr.append(value)
                count += 1
        return pd.Series(arr, dtype="float")

    def get_table_variable(
        self,
        variable: str,
        sim_day: int = None,
    ) -> pd.Series:
        """
        Return a table variable as a series.

        Parameters
        ----------
        variable : str
            a FRED table variable name

        sim_day : int
            the simulation day. By default, the last output will be returned.

        Returns
        -------
        arr : pd.Series
            a series of floats containing `variable` values indexed by keys
        """

        if sim_day is not None:
            fname = f"{variable}-{sim_day}.txt"
        else:
            fname = f"{variable}.txt"
        fname = os.path.join(self.path_to_run, "LIST", fname)

        if not os.path.isfile(fname):
            msg = (
                f"The requested output for `{variable}` was not found in "
                f"{os.path.join(self.path_to_run, 'LIST')}"
            )
            raise FileNotFoundError(msg)

        # read in data from file
        d = {}
        with open(fname, "r") as f:
            lines = f.readlines()
            count = 0
            for line in lines[1:]:
                key, value = line.strip().split(",")
                d[key] = value
                count += 1

        return pd.Series(d, name=variable)

    def get_list_table_variable(
        self,
        variable: str,
        sim_day: int = None,
        format: str = "long",
    ) -> pd.Series:
        """
        Return a list_table variable as a series.

        Parameters
        ----------
        variable : str
            a FRED table variable name

        sim_day : int
            the simulation day. By default, the last output will be returned.

        format : str, optional
            the Series format to be returned, either 'wide' (lists of float values indexed by keys which appear exactly once) or 'long' (float values indexed by keys which may appear more than once).
            By default, long format Series are returned.

        Returns
        -------
        arr : pd.Series
            a series of floats or lists of floats that record the list values from the list_table `variable` indexed by the corresponding keys
        """

        if sim_day is not None:
            fname = f"{variable}-{sim_day}.txt"
        else:
            fname = f"{variable}.txt"
        fname = os.path.join(self.path_to_run, "LIST", fname)

        if not os.path.isfile(fname):
            msg = (
                f"The requested output for `{variable}` was not found in "
                f"{os.path.join(self.path_to_run, 'LIST')}"
            )
            raise FileNotFoundError(msg)

        # read in data from file
        d = []
        i = []
        with open(fname, "r") as f:
            lines = f.readlines()

        for line in lines[1:]:
            line_list = line.strip().split(",")
            key = line_list[0]
            values = line_list[1:]
            if format == "long":
                i.extend([key for _ in range(len(values))])
                d.extend(values)
            elif format == "wide":
                i.append(key)
                d.append(values)
            else:
                msg = (
                    f"The output format '{format}' for `{variable}` is not a valid option. "
                    f"The valid options are 'long' and 'wide'."
                )
                raise ValueError(msg)

        return pd.Series(data=d, index=i, name=variable)

    def get_csv_output(self, filename: str) -> pd.DataFrame:
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
        >>> df = run.get_csv_output('infections.csv')
        """
        path_to_csv = os.path.join(self.path_to_run, "CSV", filename)
        return _read_fred_csv(path_to_csv)

    def get_network(
        self,
        network: str,
        is_directed: bool = True,
        sim_day: int = None,
    ) -> nx.Graph:
        """
        Return a network as a Graph.

        Parameters
        ----------
        network : str
            a FRED network name

        is_directed : bool
            indicates whether the network to be loaded is directed. By default, a directed graph (nx.DiGraph) will be returned.

        sim_day : int
            the simulation day. By default, the last output will be returned.

        Returns
        -------
        G : nx.Graph
            a NetworkX Graph (or DiGraph) object whose nodes (with associate attributes) and edges (with associated weights) are defined by FRED in a .vna output file.
        """

        if sim_day is None:
            sim_day = len(self.sim_days)

        fname = f"{network}-{sim_day}.vna"
        fname = os.path.join(self.path_to_run, fname)

        if not os.path.isfile(fname):
            msg = (
                f"The requested output for the network `{network}` on day {sim_day} was not found in "
                f"{self.path_to_run}\n"
                f"You may need to either pass a different sim_day or adjust the value of `output_interval` for the network `{network}` in your FRED model."
            )
            raise FileNotFoundError(msg)

        # create a Graph or DiGraph object
        if is_directed:
            G = nx.DiGraph(name=network)
        else:
            G = nx.Graph(name=network)

        # read in data from file
        with open(fname, "r") as f:
            lines = f.readlines()

        tie_data_index = lines.index("*tie data\n")
        node_data = lines[:tie_data_index]
        tie_data = lines[tie_data_index:]

        # construct a list of nodes
        node_count = 0
        nodes = []
        node_attr_keys = node_data[1].strip().split(" ")[1:]
        for line in node_data[2:]:
            line_list = line.strip().split(" ")
            node_id = line_list[0]
            node_attrs = line_list[1:]
            nodes.append((node_id, dict(zip(node_attr_keys, node_attrs))))
            node_count += 1

        # construct a list of ties
        tie_count = 0
        ties = []
        tie_attr_keys = tie_data[1].strip().split(" ")[2:]
        for line in tie_data[2:]:
            line_list = line.strip().split(" ")
            from_id = line_list[0]
            to_id = line_list[1]
            tie_attrs = line_list[2:]
            ties.append((from_id, to_id, dict(zip(tie_attr_keys, tie_attrs))))
            tie_count += 1

        G.add_nodes_from(nodes)
        G.add_edges_from(ties)

        return G

    def __str__(self) -> str:
        return f"FREDRun(run_id={self.run_id}, path_to_run={self.path_to_run})"
