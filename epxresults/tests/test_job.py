"""
a testing suite for epxresults.job module
"""

import pytest
import sys
import os
import numpy as np

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
