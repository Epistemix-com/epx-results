"""Fixtures for tests in ``./epistemixpy/fredio/tests``"""
import logging
from pathlib import Path
from typing import Optional
import os

import pytest


@pytest.fixture(scope='session')
def fred_results() -> Path:
    """Path to testing data results directory.

    These results are generated by running
    <project-root>/test-setup/generate-fred-result-data.
    """
    p = Path(os.path.abspath('fred-results'))
    if not p.is_dir():
        raise ValueError(f'{p} does not exist. Check you have run '
                         '`generate-fred-result-data`')
    if len(list(p.iterdir())) == 0:
        raise ValueError(f'{p} is empty. Check you have run '
                         '`generate-fred-result-data`')
    return p


@pytest.fixture(scope='session')
def simpleflu_job_results_dir(fred_results) -> Path:
    """Path to the results directory for the simpleflu test job.

    I.e. `<project-root>/fred-results/JOB/<simple-flu-job-id>`
    """
    def _read_simpleflu_job_id() -> Optional[int]:
        try:
            with open(fred_results / 'KEY', 'r') as f:
                for line in f:
                    key, job_id = line.split()
                    if key == 'epistemixpy_simpleflu':
                        return int(job_id)
                raise ValueError('epistemixpy_simpleflu key not found in test data')
        except FileNotFoundError:
            logging.error(
                "Could not find fred_results / 'KEY'. Check test data has been "
                "generated with `generate-fred-result-data` script."
            )
            return None

    return fred_results / ('JOB/' + str(_read_simpleflu_job_id()))


@pytest.fixture(scope='session')
def simpleflu_run1_results_dir(simpleflu_job_results_dir) -> Path:
    """Path to the results directory for run 1 of the simpleflu test job.

    I.e. `<project-root>/fred-results/JOB/<simple-flu-job-id>/OUT/RUN1`
    """
    return simpleflu_job_results_dir / 'OUT/RUN1'
