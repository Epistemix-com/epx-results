.. _reading_variables:

*********************************************
Reading global variables with ``epx-results``
*********************************************

``epx-results`` provides a Python interface to retrieve FRED global variable
data as a ``pandas.DataFrame`` object. This is provided by the
:meth:`epxresults.FREDJob.get_job_variable_table` method. First instantiate a
:class:`epxresults.FREDJob` object representing your job.

.. code-block:: python

    >>> from epxresults import FREDJob
    >>> job = FREDJob(job_key="simpleflu")

The ``simpleflu`` model contains a global variable called ``Infected``. This can
be read by calling the :meth:`epxresults.FREDJob.get_job_variable_table` method.

.. code-block:: python

    >>> infected_df = job.get_job_variable_table("Infected")
    >>> infected_df
        run  sim_day  Infected
    0     1        0       0.0
    1     1        1       6.0
    2     1        2      10.0
    3     1        3      10.0
    4     1        4      12.0
    ..  ...      ...       ...
    85    3       25    1279.0
    86    3       26    1412.0
    87    3       27    1605.0
    88    3       28    2162.0
    89    3       29    2635.0

    [90 rows x 3 columns]

For other options, including how to retrieve data at a weekly (rather than
daily) interval, see documentation for
:meth:`epxresults.FREDJob.get_job_variable_table`.

Notice that in the output for the example above, time is represented by the
simulation ``sim_day`` rather than the calendar date that each daily value
corresponds to. A common pattern is to:

1. Retrieve the simulation dates corresponding to each sim day using the
   :meth:`epxresults.FREDJob.get_job_date_table` method
2. Join these into the variable table using :meth:`pandas.DataFrame.merge`.
3. Calculate the median value of the variable for each simulation date over
   all model runs

This can be achieved with the following code snippet.

.. code-block:: python

    >>> import numpy as np
    >>> dates_df = job.get_job_date_table()
    >>> median_infected_s = (
    ...     infected_df.merge(dates_df, on=['run', 'sim_day'], how='outer')
    ...     .groupby('sim_date')['Infected'].apply(np.median)
    ... )
    >>> median_infected_s.head()
    sim_date
    2020-01-01     0.0
    2020-01-02     6.0
    2020-01-03    10.0
    2020-01-04    10.0
    2020-01-05    12.0
    Name: Infected, dtype: float64
