"""
testing suite for epistemixpy.results.run.FREDRun
"""

import pytest

import os
import numpy as np

from epistemixpy.results.run import (
    FREDRun
)

default_fred_results = os.path.abspath('./fred-results')


@pytest.fixture(autouse=True)
def set_fred_env_vars(monkeypatch):
    monkeypatch.setenv('FRED_RESULTS', default_fred_results)


def test_run_init_1(simpleflu_run1_results_dir):
    """
    test init with path to run
    """
    run = FREDRun(run_id=1, PATH_TO_RUN=str(simpleflu_run1_results_dir))
    assert run.path_to_run == str(simpleflu_run1_results_dir)


def test_run_init_2(simpleflu_job_results_dir):
    """
    test init with path to job
    """
    run = FREDRun(run_id=1,
                  PATH_TO_JOB=str(simpleflu_job_results_dir))
    assert run.path_to_run == str(simpleflu_job_results_dir)+'/OUT/RUN1'

    run = FREDRun(run_id=1,
                  PATH_TO_JOB=str(simpleflu_job_results_dir))
    assert run.path_to_run == str(simpleflu_job_results_dir)+'/OUT/RUN1'


def test_run_init_3(fred_results):
    """
    test init with path to results
    """
    run = FREDRun(run_id=1, job_id=1,
                  FRED_RESULTS=str(fred_results))
    assert run.path_to_run == str(fred_results)+'/JOB/1/OUT/RUN1'

    run = FREDRun(run_id=1, job_key='epistemixpy_simpleflu',
                  FRED_RESULTS=str(fred_results))
    assert run.path_to_run == str(fred_results)+'/JOB/1/OUT/RUN1'


def test_run_init_4(monkeypatch):
    """
    test init with environmental FRED_RESULTS
    """
    run = FREDRun(run_id=1, job_id=1)
    assert run.path_to_run == str(default_fred_results)+'/JOB/1/OUT/RUN1'

    run = FREDRun(run_id=1, job_key='epistemixpy_simpleflu')
    assert run.path_to_run == str(default_fred_results)+'/JOB/1/OUT/RUN1'
