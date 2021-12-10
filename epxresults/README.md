# Results

This is a submodule containing tools for interacting with local FRED results.


## Terminology

- **local FRED results directory** : a directory structure on disk which stores the results of FRED jobs. This is often found in `~/fred/results`.
- **FRED job key** : a unique string associated with a FRED job stored in a local results directory
- **FRED job ID** : a unique integer associated with a FRED job stored in a local results directory
- **FRED run ID** : a unique integer associated with a FRED run, part of a FRED job


## Developers

The `utils` module contains internal functions that are used to return the path to either a FRED result, job, or run directory on a user's system:

- `_path_to_results()`
- `_path_to_job()`
- `_path_to_run()`

All the user exposed functions in `utils` depend on these "internal use functions" to do the heavy lifting of resolving the appropiate location of the requested results.

In order to account for multiple use-cases, this submodule allows users to either use a FRED results directory defined by local environmental shell variables or by explicity pointing to a valid FRED results, job, or run directory. This pattern means that there are a variety of parameter(s) that can resolve a valid FRED results, job, or run directory.

A FRED results directory can be inferred from the environmental shell variables `FRED_RESULTS` or `FRED_HOME`. Users can also pass these as parameters without setting any environmental variables. A FRED job can be specified as part of a FRED results directory using a job key, `job_key`, or job ID, `job_id`, or a user may explicitly specify a path to a valid FRED job directory, `PATH_TO_JOB`. Similarly, a FRED run may be specified as part of a FRED job with a FRED run ID, `run_id`, or a user may specify an explicit path to a FRED run directory, `PATH_TO_RUN`.

To account for the varied methods of accesing results, this module makes extensive use of the `**kwargs` pattern in function defintions.  This allows for tidy, if somewhat obscured, handling of a significant number of optional arguments.

As a reminder to developers, the `func(**kwargs)` pattern takes any additional arguments passed as keyword arguments to `func` (not explicitly enumerated in the function signiture) and generates a dictionary called `kwargs`. 

For example, assuming there is a FRED results directory defined by environmental variables:

```
assert os.path.expanduser('~/fred/results') == os.environ.get('FRED_RESULTS')
```

that contains a job with job ID `1` with a run with run ID `1`. All of the following could be used to return a valid path to that FRED run.

```
PATH_TO_RUN = _path_to_run(PATH_TO_RUN='~/fred/results/JOB/1/OUT/RUN1')  # trivial
PATH_TO_RUN = _path_to_run(PATH_TO_JOB='~/fred/results/JOB/1', run_id=1)
PATH_TO_RUN = _path_to_run(FRED_RESULTS='~/fred/results, job_id=1, run_id=1)
PATH_TO_RUN = _path_to_run(job_id=1, run_id=1)
```

It should also be noted that there is an implicit heirarchy that is followed when resolving a path to results, jobs, or runs. Explicitly passed paths will always take precedence.  Passing `FRED_RESULTS` in a function call will take precedence over any environmental variables, passing `PATH_TO_JOB` will take precedence over `FRED_RESULTS`, etc.