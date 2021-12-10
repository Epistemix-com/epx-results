"""
testing suire for epistemixpy.results.job.FREDJob
"""

import pytest

import os
import numpy as np

from epistemixpy.results.job import (
    FREDJob
)

default_fred_results = os.path.abspath('./fred-results')


@pytest.fixture(autouse=True)
def set_fred_env_vars(monkeypatch):
    monkeypatch.setenv('FRED_RESULTS', default_fred_results)


def test_job_init_1(simpleflu_job_results_dir):
    """
    test init with path to job
    """
    job = FREDJob(PATH_TO_JOB=str(simpleflu_job_results_dir))
    assert job.path_to_job == str(simpleflu_job_results_dir)


def test_job_init_2(fred_results):
    """
    test init with path to results
    """
    job = FREDJob(job_id=1,
                  FRED_RESULTS=str(fred_results))
    assert job.path_to_job == str(fred_results)+'/JOB/1'

    job = FREDJob(job_key='epistemixpy_simpleflu',
                  FRED_RESULTS=str(fred_results))
    assert job.path_to_job == str(fred_results)+'/JOB/1'


def test_job_init_3(monkeypatch):
    """
    test init with environmental FRED_RESULTS
    """
    job = FREDJob(job_id=1)
    assert job.path_to_job == str(default_fred_results)+'/JOB/1'

    job = FREDJob(job_key='epistemixpy_simpleflu')
    assert job.path_to_job == str(default_fred_results)+'/JOB/1'
