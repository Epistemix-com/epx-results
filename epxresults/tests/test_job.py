"""
a testing suite for epxresults.job module
"""
import os

import pandas as pd

from epxresults.job import (
    FREDJob
    )
from epxresults.utils import (
    return_job_id
    )


###############################
# initializing FRED job objects
###############################


def test_1(pkg_test_env):
    """
    test init with job key
    """
    job = FREDJob(job_key='epx-results_simpleflu')
    assert job.job_key == 'epx-results_simpleflu'


def test_2(pkg_test_env):
    """
    test init with job key and explicit FRED_RESULTS
    """
    FRED_RESULTS = os.environ['FRED_RESULTS']
    os.environ['FRED_RESULTS'] = ''
    job = FREDJob(FRED_RESULTS=FRED_RESULTS, job_key='epx-results_simpleflu')
    assert job.job_key == 'epx-results_simpleflu'


def test_3(pkg_test_env):
    """
    test init with job ID
    """
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    job = FREDJob(job_id=test_job_id)
    assert job.job_key == 'epx-results_simpleflu'


def test_4(pkg_test_env):
    """
    test init with job ID and explicit FRED_RESULTS
    """
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    FRED_RESULTS = os.environ['FRED_RESULTS']
    os.environ['FRED_RESULTS'] = ''
    job = FREDJob(FRED_RESULTS=FRED_RESULTS, job_id=test_job_id)
    assert job.job_key == 'epx-results_simpleflu'


def test_5(pkg_test_env):
    """
    test init with path to job
    """
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    FRED_RESULTS = os.environ['FRED_RESULTS']
    os.environ['FRED_RESULTS'] = ''
    PATH_TO_JOB = os.path.join(FRED_RESULTS, 'JOB', str(test_job_id))
    job = FREDJob(PATH_TO_JOB=PATH_TO_JOB)
    assert job.job_key == 'epx-results_simpleflu'


def test_job_get_job_date_table():
    job = FREDJob(job_key='epx-results_simpleflu')
    dates_df = job.get_job_date_table()
    assert dates_df.columns.to_list() == ['run', 'sim_day', 'sim_date']
    assert dates_df['sim_day'].dtype == 'int64'
    assert dates_df['sim_date'].dtype == '<M8[ns]'

    # Job contains 3 runs from 2020-01-01 to 2020-01-30. That's
    # 3 * 30 = 90 days in total
    assert len(dates_df.index) == 90
    assert dates_df.iloc[0]['sim_date'] == pd.Timestamp('2020-01-01')
    assert dates_df.iloc[-1]['sim_date'] == pd.Timestamp('2020-01-30')

    # Runs are 1-indexed
    assert dates_df.iloc[0]['run'] == 1
    assert dates_df.iloc[-1]['run'] == 3

    # sim days are 0-indexed
    assert dates_df.iloc[0]['sim_day'] == 0
    assert dates_df.iloc[-1]['sim_day'] == 29
