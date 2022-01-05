"""
utilities for the epxresults sub-module
"""

import os
import re
from os import PathLike
from warnings import warn
from typing import (Dict, List, Optional, Tuple, Union)
from pathlib import Path
import pandas as pd


__all__ = ['load_local_job_keys', 'return_job_id', 'return_job_run_ids']
__author__ = ['Duncan Campbell']


def load_local_job_keys(**kwargs) -> Dict[str, int]:
    r"""
    Return a dictionary of FRED job key and job ID pairs

    Parameters
    ----------
    **kwargs : dict
        optional keyword arguments:

        FRED_RESULTS : PathLike, optional
            the path to a local FRED results directory
        FRED_HOME : PathLike, optional
            the path to a local FRED home directory

    Returns
    -------
    keys : dict
        a dictionary of FRED job key and FRED job ID pairs

    Examples
    --------
    If a FRED results directory is specified by environmental variables,
    a dictionary of job keys can be loaded easily. For example,

    >>> from epxresults import load_local_job_keys
    >>> job_keys = load_local_job_keys()
    >>> print(job_keys)
    {...}

    See the `Notes` section for details on how a local FRED results
    directory is specified.

    Notes
    -----
    An empty FRED results directory will not generally contain a ``KEY`` file,
    the location where job key-job ID pairs are stored. In this circumstance,
    we have chosen to return `keys` as an empty dictionary with a warning
    message instead of raising an exception.

    For details on how the path to a FRED results directoy is resolved,
    see :py:func:`epxresults.utils._path_to_results`.
    """

    FRED_RESULTS = _path_to_results(**kwargs)
    filename = os.path.join(FRED_RESULTS, 'KEY')

    if os.path.exists(filename) is False:
        msg = (f"{FRED_RESULTS} does not contain a KEY file. "
               "Returning an empty dictionary of job keys.")
        warn(msg)
        return {}

    keys = {}
    with open(filename, 'rb') as f:
        for line in f:
            key, value = line.strip().split()
            key = key.decode('utf-8')
            keys[key] = int(value)
    return keys


def return_job_id(job_key, **kwargs) -> int:
    """
    Return the FRED job ID associated with a FRED job key

    Parameters
    ----------
    job_key : string
        A valid FRED job key

    Other Parameters
    ----------------
    **kwargs : dict
        additonal optional keyword arguments:

        FRED_RESULTS : PathLike, optional
            the path to a local FRED results directory
        FRED_HOME : PathLike, optional
            the path to a local FRED home directory

    Returns
    -------
    job_id : int
        a FRED job ID corresponding to `job_key`

    Raises
    ------
    KeyError
        raised if a FRED job associated with `job_key` cannot be found
        in the indicated local FRED results directory

    Examples
    --------
    If a FRED results directory is specified by environmental variables,
    the FRED job ID assocoayed with a FRED job can easily be obtained.
    For example,

    >>> from epxresults import return_job_id
    >>> job_id = return_job_id('simpleflu')
    >>> print(f"The job ID assocaited with `simpleflu` is {job_id}")
    The job ID assocaited with `simpleflu` is ...

    See the `Notes` section for details on how a local FRED results
    directory is specified.

    Notes
    -----
    For details on how the path to a FRED results directoy is resolved,
    see :py:func:`epxresults.utils._path_to_results`.
    """

    fred_keys = load_local_job_keys(**kwargs)

    try:
        job_id = fred_keys[job_key]
    except KeyError:
        FRED_RESULTS = _path_to_results(**kwargs)
        msg = (f"The FRED job key '{job_key}' not found in {FRED_RESULTS}.")
        raise KeyError(msg)

    return job_id


def return_job_run_ids(**kwargs) -> List[int]:
    """
    Return the run IDs in a FRED job.

    Parameters
    ----------
    **kwargs : dict
        One of the following keyword parameters must be provided:

        job_id : int, optional
            a FRED job ID
        job_key : string, optional
            a FRED job key
        PATH_TO_JOB : PathLike, optional
            the path to a FRED job directory

    Other Parameters
    ----------------
    **kwargs : dict
        additonal optional keyword arguments:

        FRED_RESULTS : PathLike, optional
            the path to a local FRED results directory
        FRED_HOME : PathLike, optional
            the path to a local FRED home directory

    Returns
    -------
    runs : list
        a list of FRED run IDs

    Examples
    --------
    If a FRED results directory is specified by environmental variables,
    a list of FRED run IDs associated with a FRED job key can be loaded
    easily. For example,

    >>> from epxresults import return_job_run_ids
    >>> return_job_run_ids(job_key = 'simpleflu')
    [1, 2, 3]

    See the `Notes` section for details on how the the path to a local
    FRED job directory is resolved.

    Notes
    -----
    For details on how the path to a FRED job directoy is resolved,
    see :py:func:`epxresults.utils._path_to_job`.
    """

    PATH_TO_JOB = _path_to_job(**kwargs)

    job_dirs = os.listdir(os.path.join(PATH_TO_JOB, 'OUT'))
    run_dir_pattern = re.compile("RUN[0-9]+")

    runs = []
    for job_dir in job_dirs:
        if run_dir_pattern.match(job_dir):
            run = int(job_dir.replace('RUN', ''))
            runs.append(run)

    runs.sort()
    return runs


def _path_to_results(**kwargs) -> Path:
    """
    Return the full path to a local FRED results directory.

    Parameters
    ----------
    **kwargs : dict
        optional keyword arguments:

        FRED_RESULTS : PathLike
            the path to a local FRED results directory. If passed as an
            argument, this path is returned.
        FRED_HOME : PathLike
            the path to a local FRED home directory

    Returns
    -------
    FRED_RESULTS : Path
        a path to a local FRED results directory

    Raises
    ------
    FileNotFoundError
        raised if the indicated FRED results directory cannot be found
    ValueError
        raised if the keyword parameters are not sufficient to uniquely
        identify a FRED results directory

    Notes
    -----
    If `FRED_HOME` is passed as a keyword argument, a local FRED results
    directory is assumed to exist at ``os.path.join(FRED_HOME, 'results')``.

    If `FRED_RESULTS` or `FRED_HOME` are not passed as keyword arguments,
    this function will attempt to resolve the path to a local FRED results
    directory using the value of environmental variables of the same name.
    Similarly, if ``FRED_RESULTS`` is not set as an environmental variable,
    a local FRED results directory is assumed to exist at
    ``$FRED_HOME/results``.

    Users may check the value of these environmental variables:

    >>> import os
    >>> FRED_RESULTS = os.getenv('FRED_RESULTS')
    >>> FRED_HOME = os.getenv('FRED_HOME')
    >>>
    >>> print(f"FRED_RESULTS={FRED_RESULTS}")
    FRED_RESULTS=...
    >>> print(f"FRED_HOME={FRED_HOME}")
    FRED_HOME=...

    :meta public:
    """

    if 'FRED_RESULTS' in kwargs.keys():
        FRED_RESULTS = kwargs['FRED_RESULTS']
        if 'FRED_HOME' in kwargs.keys():
            msg = ("Both `FRED_HOME` and `FRED_RESULTS` "
                   "were passed as keyword arguments.\n"
                   f"Defaulting to `FRED_RESULTS`='{FRED_RESULTS}'")
            warn(msg)
    elif 'FRED_HOME' in kwargs.keys():
        FRED_HOME = kwargs['FRED_HOME']
        FRED_RESULTS = os.path.join(FRED_HOME, 'results')
    else:
        try:
            FRED_RESULTS = _inferred_path_to_results()
        except RuntimeError:
            msg = ("FRED_RESULTS` or `FRED_HOME` must be passed as a keyword "
                   "argument or set as a environmental variable.")
            raise ValueError(msg)

    FRED_RESULTS = os.path.abspath(FRED_RESULTS)

    if not os.path.isdir(FRED_RESULTS):
        msg = (f"`FRED_RESULTS`='{FRED_RESULTS}' is not a directory.")
        raise FileNotFoundError(msg)

    return FRED_RESULTS


def _inferred_path_to_results() -> None:
    """
    Return the path to a local FRED results directory inferred
    from environmental variables ``FRED_RESULTS`` or ``FRED_HOME``.

    Returns
    -------
    FRED_RESULTS : Path
        a path to a local FRED results directory

    Raises
    ------
    RuntimeError
        raised if no local FRED results directory can be inferred
    FileNotFoundError
        raised if the inferred local FRED results directory can not be found

    Notes
    -----
    If an environmental variable ``FRED_RESULTS`` is set, the value is used as
    the path to a local FRED results directory. Otherwise, a local FRED results
    directory is assumed to exist at ``$FRED_HOME/results``.
    """

    FRED_RESULTS = os.getenv('FRED_RESULTS')

    if FRED_RESULTS is None:
        FRED_HOME = os.getenv('FRED_HOME')
        if FRED_HOME is None:
            msg = (f"Neither 'FRED_RESULTS' nor 'FRED_HOME' are set "
                   f"as an environmental variable. As a result, the "
                   f"location of a local FRED results directory could "
                   f"not be inferred.")
            raise RuntimeError(msg)
        else:
            FRED_RESULTS = os.path.join(FRED_HOME, 'results')
            msg = (f"'FRED_RESULTS' is not set as an environmental variable. "
                   f"`FRED_RESULTS` will default to '$FRED_HOME/results'."
                   f"`FRED_RESULTS`='{FRED_RESULTS}'")
            warn(msg)
    else:
        pass

    if not os.path.isdir(FRED_RESULTS):
        msg = (f"`FRED_RESULTS`='{FRED_RESULTS}' is not a directory. "
               f"Ensure that the directory pointed to be the environmental "
               f"variables 'FRED_RESULTS' and/or 'FRED_HOME' exist on "
               f"your system.")
        raise FileNotFoundError(msg)

    return os.path.abspath(FRED_RESULTS)


def _path_to_job(**kwargs) -> Path:
    """
    Return the full path to the requested FRED job results directory.

    Parameters
    ----------
    **kwargs : dict
        One of the following keyword parameters must be provided:

        job_key : string
            a FRED job key name
        job_id : int
            a FRED job ID
        PATH_TO_JOB : PathLike
            a path to a FRED job. If passed as an argument, this path is
            returned.

    Other Parameters
    ----------------
    **kwargs: dict
        additonal optional keyword arguments:

        FRED_RESULTS : PathLike
            the full path to a local FRED results directory
        FRED_HOME : PathLike
            the full path to a local FRED home directory

    Returns
    -------
    PATH_TO_JOB : Path
        a path to a local FRED job directory

    Raises
    ------
    FileNotFoundError
        raised if the indicated FRED job directory cannot be found
    ValueError
        raised if the keyword parameters are not sufficient to uniquely
        identify a FRED job directory

    Notes
    -----
    For details on how the path to a FRED results directoy is resolved,
    see :py:func:`epxresults.utils._path_to_results`.

    :meta public:
    """

    if 'PATH_TO_JOB' in kwargs.keys():
        PATH_TO_JOB = os.path.abspath(kwargs['PATH_TO_JOB'])
        if not os.path.isdir(PATH_TO_JOB):
            msg = (f"`PATH_TO_JOB`='{PATH_TO_JOB}' does not exist.")
            raise FileNotFoundError(msg)
        return PATH_TO_JOB

    if 'job_id' in kwargs.keys():
        job_id = kwargs['job_id']
    elif 'job_key' in kwargs.keys():
        job_key = kwargs['job_key']
        job_id = return_job_id(**kwargs)
    else:
        msg = ("Either `job_key`, `job_id`, or `PATH_TO_JOB` must be passed "
               "as keyword arguments.")
        ValueError(msg)

    PATH_TO_RESULTS = _path_to_results(**kwargs)
    PATH_TO_JOB = os.path.join(PATH_TO_RESULTS, 'JOB/'+str(job_id))
    PATH_TO_JOB = os.path.abspath(PATH_TO_JOB)

    if not os.path.isdir(PATH_TO_JOB):
        msg = (f"FRED job ID: '{job_id}' is not present in {FRED_RESULTS}.")
        raise FileNotFoundError(msg)

    return os.path.abspath(PATH_TO_JOB)


def _path_to_run(run_id: int = 1, **kwargs) -> Path:
    """
    Return the full path to the requested FRED run results directory.

    Parameters
    ----------
    run_id : int, optional
        A FRED run ID

    **kwargs : dict
        One of the following keyword parameters must be provided:

        job_key : string
            A FRED job key
        job_id : int
            a FRED job ID
        PATH_TO_JOB : PathLike
            a path to a FRED job
        PATH_TO_RUN : PathLike
            a path to a FRED run. If passed as an argument, `PATH_TO_RUN` is
            returned.

    Other Parameters
    ----------------
    **kwargs: dict
        additonal optional keyword arguments:

        FRED_RESULTS : PathLike
            the full path to a local FRED results directory
        FRED_HOME : PathLike
            the full path to a local FRED home directory

    Returns
    -------
    PATH_TO_RUN : Path
        a path to a local FRED run directory

    Raises
    ------
    FileNotFoundError
        raised if the indicated FRED run directory cannot be found
    ValueError
        raised if the keyword parameters are not sufficient to uniquely
        identify a FRED run directory

    Notes
    -----
    For details on how the path to a FRED job is resolved,
    see :py:func:`epxresults.utils._path_to_job`.

    :meta public:
    """

    if 'PATH_TO_RUN' in kwargs.keys():
        PATH_TO_RUN = os.path.abspath(kwargs['PATH_TO_RUN'])
        if not os.path.isdir(PATH_TO_RUN):
            msg = (f"`PATH_TO_RUN`='{PATH_TO_RUN}' does not exist.")
            FileNotFoundError(msg)
        return PATH_TO_RUN

    try:
        PATH_TO_JOB = _path_to_job(**kwargs)
    except ValueError:
        msg = ("Either `job_key`, `job_id`, `PATH_TO_JOB`, "
               "or `PATH_TO_RUN` must be passed ",
               "as keyword arguments.")
        raise ValueError(msg)

    PATH_TO_RUN = os.path.join(PATH_TO_JOB, 'OUT/'+'RUN'+str(run_id)+'/')
    PATH_TO_RUN = os.path.abspath(PATH_TO_RUN)

    if not os.path.isdir(PATH_TO_RUN):
        msg = (f"Run {run_id} does not exist in "
               f"{os.path.join(PATH_TO_JOB,'/OUT')}.")
        raise FileNotFoundError(msg)

    return PATH_TO_RUN


def _value_str_to_value(s: str) -> Union[int, float, str]:
    """
    Convert FRED personal or global variable value strings into
    an apprioate python type.

    Parameters
    ----------
    s : string
        a string representation of a FRED parameter value

    Returns
    -------
    value : int, float, string
        the converted value

    Notes
    -----
    If the value is consistent with being an integer, an integer is
    returned. Otherwise, if the value is consistent with being a float,
    a float is returned. If the value is neither an integer or a float,
    the string is returned un-altered.
    """

    # integer
    try:
        return int(s)
    except ValueError:
        pass

    # float
    try:
        return float(s)
    except ValueError:
        pass

    # else return string
    return s


def _read_fred_csv(filepath: Path) -> pd.DataFrame:
    """
    load a FRED CSV output into a pandas DataFrame.

    Parameters
    ----------
    filepath : PathLike
        a filepath to a FRED CSV output file

    Returns
    -------
    df : pd.DataFrame
        a data frame containing the specified CSV output file contents
    """

    return pd.read_csv(filepath, sep=',', header=0)


def _read_list_variable_file(
        list_variable_file: Path,
        list_variable_name: str
        ) -> pd.DataFrame:
    """
    """

    with open(list_variable_file, 'r') as f:
        list_data = f.readlines()

    if list_data[0].strip() != list_variable_name:
        raise ValueError(
            f'Expected file {list_variable_file} to have '
            f'{list_variable_name} as first line but found {list_data[0]}.'
            ' Check results.'
        )

    df = pd.DatFrame(np.array([float(x) for x in list_data[1:]]))

    return df
