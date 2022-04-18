"""
tools to insert FRED jobs into a local FRED results directory
"""

import sys
import os
import shutil
from os import PathLike
from .utils import _path_to_results, return_job_id, load_local_job_keys


__all__ = ["merge_fred_results", "insert_fred_job"]
__author__ = ["Duncan Campbell"]


def merge_fred_results(
    source: PathLike,
    destination: PathLike = None,
    force: bool = False,
    verbose: bool = False,
    **kwargs,
) -> None:
    """
    Merge a `source` FRED results directory into a `destination`
    FRED results directory.

    Parameters
    ----------
    source : PathLike
        a path to a source FRED results directory

    destination : PathLike, optional
        a path to a destination FRED results directory

    force : bool, optional
        a flag indicting if jobs in local FRED results should be replaced
        if there is a matching job key in the `source` results

    verbose : bool, optional
        if True, print out additional information about the status of the
        merge process

    **kwargs : dict
        additional optional keyword arguments

    Notes
    -----
    If `destination` is not provided as a keyword argument, a local FRED
    results directory will be inferred from any additional keyword arguments
    in `**kwargs`. For details on how the path to a local FRED results
    directory is resolved, see :py:func:`epxresults.utils._path_to_results`.
    """

    source_keys = load_local_job_keys(FRED_RESULTS=source)

    if destination:
        FRED_RESULTS = destination
        kwargs["FRED_RESULTS"] = FRED_RESULTS
    else:
        FRED_RESULTS = _path_to_results(**kwargs)

    if source_keys == {}:
        msg = f"{source} is either empty or it does not contain a KEY file."
        raise RuntimeError(msg)

    for job_key in source_keys.keys():
        if verbose:
            print(f"Inserting {job_key} into {FRED_RESULTS} ...")
        path_to_job = os.path.join(source, f"JOB/{source_keys[job_key]}")
        insert_fred_job(
            path_to_job, job_key=job_key, force=force, verbose=verbose, **kwargs
        )

    if verbose:
        print("Done merging FRED results.")


def insert_fred_job(
    PATH_TO_JOB: PathLike,
    destination: PathLike = None,
    job_key: str = None,
    force: bool = False,
    verbose: bool = False,
    **kwargs,
) -> None:
    """
    Insert a FRED job into a local FRED results directory.

    Parameters
    ----------
    PATH_TO_JOB : PathLike
        path to a FRED job directory

    destination : PathLike, optional
        a path to a destination FRED results directory

    job_key : string, optional
        the FRED job key to use when inserting the job into the local
        FRED results directory. `job_key` defaults to the key originally
        associated with the job if not passed as a keyword argument.

    force : bool, optional
        a boolean flag indicating if a FRED job with the same job key
        in the local results directory should be repalced with the
        inserted job.

    verbose : bool, optional
        if True, print out additional information about the status of the
        merge process

    **kwargs : dict
        additional optional keyword arguments

    Notes
    -----
    If `destination` is not provided as a keyword argument, a local FRED
    results directory will be inferred from any additional keyword arguments
    in `**kwargs`. For details on how the path to a local FRED results
    directory is resolved, see :py:func:`epxresults.utils._path_to_results`.
    """

    if job_key is None:
        fname = os.path.join(PATH_TO_JOB, "META/KEY")
        if not os.path.isfile(fname):
            msg = f"{PATH_TO_JOB} does not contain 'META/KEY'."
            raise ValueError(msg)
        with open(fname) as f:
            job_key = f.read().strip()

    if not _is_valid_fred_job_key(job_key):
        msg = f"`job_key` is not a valid potential job key."
        raise ValueError(msg)

    if verbose:
        print(f"Inserting FRED job with job key: {job_key}.")

    if destination:
        FRED_RESULTS = destination
        kwargs["FRED_RESULTS"] = FRED_RESULTS
    else:
        FRED_RESULTS = _path_to_results(**kwargs)

    local_job_keys = load_local_job_keys(**kwargs)

    if (force is False) & (job_key in local_job_keys.keys()):
        msg = (
            f"FRED job key '{job_key}' is already present in\n",
            f"the local FRED results: {FRED_RESULTS}.\n",
            "To replace this job, set `force=True`.\n",
            "Otherwise, select a different job key.",
        )
        raise RuntimeError(msg)

    # set job ID
    try:
        job_id = return_job_id(job_key, **kwargs)
    except KeyError:
        if len(local_job_keys.keys()) == 0:
            job_id = 1
        else:
            job_id = max(local_job_keys.values()) + 1

    destination = os.path.join(FRED_RESULTS, "JOB", str(job_id))

    if os.path.exists(destination):
        if verbose:
            print(f"deleting {destination}...")
        shutil.rmtree(destination)

    local_job_keys[job_key] = job_id
    _write_local_keys(local_job_keys, **kwargs)

    # copy results into local FRED results directory
    if verbose:
        print(f"copying FRED job to {destination}...")
    shutil.copytree(PATH_TO_JOB, destination)
    if verbose:
        print(f"Done inserting job {job_key}.")


def _write_local_keys(job_keys, **kwargs) -> None:
    """
    Write a local FRED results job key map.

    Parameters
    ----------
    job_keys : dict
        a dictionary of FRED job key and FRED job ID pairs

    Notes
    -----
    This function will overwrite any existing KEY and/or ID
    file in a FRED results directory.
    """

    FRED_RESULTS = _path_to_results(**kwargs)

    job_keys = dict(sorted(job_keys.items(), key=lambda item: item[1]))

    # write KEY file
    filename = os.path.join(FRED_RESULTS, "KEY")
    with open(filename, "w") as f:
        for job_key in job_keys:
            value = job_keys[job_key]
            f.write("{0} {1}\n".format(job_key, value))

    # write ID file
    filename = os.path.join(FRED_RESULTS, "ID")
    with open(filename, "w") as f:
        if job_keys == {}:
            # all jobs have been deleted
            f.write("{0}\n".format(1))
        else:
            f.write("{0}\n".format(str(max(job_keys.values()) + 1)))


def _is_valid_fred_job_key(job_key: str) -> bool:
    """
    Determine if `job_key` is a valid potential FRED job key.

    Returns
    -------
    valid_job_key : bool
        boolean indicating if the FRED job key is valid.
    """

    if "\n" in job_key:
        return False
    elif len(job_key) > 1000:
        return False
    return True


def main():
    """ """
    source = sys.argv[1]
    FRED_RESULTS = _path_to_results()
    merge_fred_results(
        source=source, FRED_RESULTS=FRED_RESULTS, force=True, verbose=True
    )


if __name__ == "__main__":
    main()
