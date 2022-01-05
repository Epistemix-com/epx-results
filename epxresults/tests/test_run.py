"""
testing suite for epistemixpy.results.run.FREDRun
"""

import pytest

import os
import numpy as np

from epxresults.run import (
    FREDRun
    )
from epxresults.utils import (
    return_job_id,
    return_job_run_ids
    )


###############################
# initializing FRED run objects
###############################


def test_1(pkg_test_env):
    """
    test init with job key and run ID
    """
    run = FREDRun(job_key='epx-results_simpleflu', run_id=1)
    assert run.run_id == 1

    run = FREDRun(job_key='epx-results_simpleflu', run_id=2)
    assert run.run_id == 2

    run = FREDRun(job_key='epx-results_simpleflu', run_id=3)
    assert run.run_id == 3


def test_2(pkg_test_env):
    """
    test init with job ID and run ID
    """
    test_job_id = return_job_id(job_key='epx-results_simpleflu')

    run = FREDRun(job_id=test_job_id, run_id=1)
    assert run.run_id == 1

    run = FREDRun(job_id=test_job_id, run_id=2)
    assert run.run_id == 2

    run = FREDRun(job_id=test_job_id, run_id=3)
    assert run.run_id == 3


def test_3(pkg_test_env):
    """
    test init with job key and run ID
    """
    FRED_RESULTS = os.environ['FRED_RESULTS']

    os.environ['FRED_RESULTS'] = ''

    run = FREDRun(job_key='epx-results_simpleflu', run_id=1, FRED_RESULTS=FRED_RESULTS)
    assert run.run_id == 1

    run = FREDRun(job_key='epx-results_simpleflu', run_id=2, FRED_RESULTS=FRED_RESULTS)
    assert run.run_id == 2

    run = FREDRun(job_key='epx-results_simpleflu', run_id=3, FRED_RESULTS=FRED_RESULTS)
    assert run.run_id == 3


def test_4(pkg_test_env):
    """
    test init with job ID and run ID
    """
    FRED_RESULTS = os.environ['FRED_RESULTS']
    test_job_id = return_job_id(job_key='epx-results_simpleflu')

    os.environ['FRED_RESULTS'] = ''

    run = FREDRun(job_id=test_job_id, run_id=1, FRED_RESULTS=FRED_RESULTS)
    assert run.run_id == 1

    run = FREDRun(job_id=test_job_id, run_id=2, FRED_RESULTS=FRED_RESULTS)
    assert run.run_id == 2

    run = FREDRun(job_id=test_job_id, run_id=3, FRED_RESULTS=FRED_RESULTS)
    assert run.run_id == 3
