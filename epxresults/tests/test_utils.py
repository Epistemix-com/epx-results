"""
unit tests of the results.utils submodule
"""

import os
from pathlib import Path
import pytest

from ..utils import (
    return_job_id,
    _path_to_results,
    _path_to_job,
    _path_to_run
    )

PKG_DIRECTORY = Path(os.path.abspath(__file__)).parent.parent.parent
PKG_TESTS_DIRECTORY = Path(os.path.join(PKG_DIRECTORY, 'tests'))
PKG_FRED_RESULTS = os.path.join(f'{PKG_TESTS_DIRECTORY}', 'fred-results')


################################
# resolve FRED results directory
################################

def test_1(pkg_test_env):
    """
    resolve FRED results with FRED_RESULTS environmental variable
    """
    p = _path_to_results()
    assert p == PKG_FRED_RESULTS


def test_2(pkg_test_env):
    """
    resolve FRED results with explicit FRED_RESULTS
    """
    FRED_RESULTS = os.environ['FRED_RESULTS']
    os.environ['FRED_RESULTS'] = ''
    p = _path_to_results(FRED_RESULTS=FRED_RESULTS)
    assert p == FRED_RESULTS


############################
# resolve FRED job directory
############################

def test_3(pkg_test_env):
    """
    resolve FRED job with job key
    """
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    p = _path_to_job(job_key='epx-results_simpleflu')
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id))


def test_4(pkg_test_env):
    """
    resolve FRED job with job ID
    """
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    p = _path_to_job(job_id=test_job_id)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id))


def test_5(pkg_test_env):
    """
    resolve FRED job with job key with explicit FRED_RESULTS
    """
    FRED_RESULTS = os.environ['FRED_RESULTS']
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    os.environ['FRED_RESULTS'] = ''
    p = _path_to_job(job_key='epx-results_simpleflu', FRED_RESULTS=FRED_RESULTS)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id))


def test_6(pkg_test_env):
    """
    resolve FRED job with job ID with explicit FRED_RESULTS
    """
    FRED_RESULTS = os.environ['FRED_RESULTS']
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    os.environ['FRED_RESULTS'] = ''
    p = _path_to_job(job_id=test_job_id, FRED_RESULTS=FRED_RESULTS)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id))


############################
# resolve FRED run directory
############################

def test_7(pkg_test_env):
    """
    resolve FRED run with job key
    """
    test_job_id = return_job_id(job_key='epx-results_simpleflu')

    p = _path_to_run(job_key='epx-results_simpleflu', run_id=1)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{1}')

    p = _path_to_run(job_key='epx-results_simpleflu', run_id=2)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{2}')

    p = _path_to_run(job_key='epx-results_simpleflu', run_id=3)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{3}')


def test_8(pkg_test_env):
    """
    resolve FRED run with job ID
    """
    test_job_id = return_job_id(job_key='epx-results_simpleflu')

    p = _path_to_run(job_id=test_job_id, run_id=1)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{1}')

    p = _path_to_run(job_id=test_job_id, run_id=2)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{2}')

    p = _path_to_run(job_id=test_job_id, run_id=3)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{3}')


def test_9(pkg_test_env):
    """
    resolve FRED run with job key and explicit FRED_RESULTS
    """
    FRED_RESULTS = os.environ['FRED_RESULTS']
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    os.environ['FRED_RESULTS'] = ''

    p = _path_to_run(job_key='epx-results_simpleflu', run_id=1, FRED_RESULTS=FRED_RESULTS)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{1}')

    p = _path_to_run(job_key='epx-results_simpleflu', run_id=2, FRED_RESULTS=FRED_RESULTS)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{2}')

    p = _path_to_run(job_key='epx-results_simpleflu', run_id=3, FRED_RESULTS=FRED_RESULTS)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{3}')


def test_10(pkg_test_env):
    """
    resolve FRED run with job ID and explicit FRED_RESULTS
    """
    FRED_RESULTS = os.environ['FRED_RESULTS']
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    os.environ['FRED_RESULTS'] = ''

    p = _path_to_run(job_id=test_job_id, run_id=1, FRED_RESULTS=FRED_RESULTS)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{1}')

    p = _path_to_run(job_id=test_job_id, run_id=2, FRED_RESULTS=FRED_RESULTS)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{2}')

    p = _path_to_run(job_id=test_job_id, run_id=3, FRED_RESULTS=FRED_RESULTS)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{3}')


def test_11(pkg_test_env):
    """
    resolve FRED run with path to FRED run
    """
    FRED_RESULTS = os.environ['FRED_RESULTS']
    test_job_id = return_job_id(job_key='epx-results_simpleflu')
    os.environ['FRED_RESULTS'] = ''

    PATH_TO_RUN = os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{3}')

    p = _path_to_run(PATH_TO_RUN=PATH_TO_RUN)
    assert p == os.path.join(PKG_FRED_RESULTS, 'JOB', str(test_job_id), 'OUT', f'RUN{3}')
