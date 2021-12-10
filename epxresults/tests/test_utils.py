"""
unit tests of the results.utils submodule
"""

import os
import pytest

from ..utils import _path_to_results, _path_to_job, _path_to_run

default_fred_home = '/fred'
default_fred_results = '/fred/results'


@pytest.fixture(autouse=True)
def set_fred_env_vars(monkeypatch):
    monkeypatch.setenv('FRED_HOME', default_fred_home)
    monkeypatch.setenv('FRED_RESULTS', default_fred_results)


#####
# test _path_to_results()
#####


def test_path_to_results_defaults_to_fred_results_environment_variable(monkeypatch):
    """
    confirm that FRED results directory defaults to the 'FRED_RESULTS'
    environmental variable
    """
    monkeypatch.setattr(os.path, 'isdir', lambda x: True)
    assert(_path_to_results() == default_fred_results)


def test_path_to_results_with_results_dir_param_exists(monkeypatch):
    """
    confirm that FRED results directory uses the the `FRED_RESULTS`
    parameter
    """
    mocked_abs_path = '/abs/path/to/results'
    monkeypatch.setattr(os.path, 'isdir', lambda x: True)
    monkeypatch.setattr(os.path, 'abspath', lambda x: mocked_abs_path)
    assert(_path_to_results(FRED_RESULTS="../results") == mocked_abs_path)


def test_path_to_results_with_results_dir_param_does_not_exist(monkeypatch):
    """
    confirm that a FileNotFoundError is rasied if the requested FRED results
    directory does not exist.
    """
    monkeypatch.setattr(os.path, 'isdir', lambda x: False)
    with pytest.raises(FileNotFoundError, match=r".*not a directory"):
        _path_to_results(FRED_RESULTS="../results")


def test_path_to_results_with_fred_home_param(monkeypatch):
    """
    confirm that FRED results directory defaults to the `FRED_HOME`/results
    if only FRED_HOME is passed as a keyword argument
    """
    monkeypatch.setattr(os.path, 'isdir', lambda x: True)
    monkeypatch.setattr(os, 'getenv', lambda x: None)
    assert(_path_to_results(FRED_HOME="/fred/home") == "/fred/home/results")


def test_path_to_results_with_fred_results_param(monkeypatch):
    """
    confirm that FRED results directory defaults to `FRED_HOME`/results
    if only FRED_HOME is passed as a keyword argument
    """
    monkeypatch.setattr(os.path, 'isdir', lambda x: True)
    assert(_path_to_results(FRED_RESULTS="/home/fred/results") == "/home/fred/results")


def test_path_to_results_with_all_params_uses_results_dir(monkeypatch):
    """
    confirm that FRED results directory uses the the `FRED_RESULTS`
    parameter if both FRED_RESULTS and FRED_HOME are passed as keyword
    arguments
    """
    mocked_abs_path = '/abs/path/to/results'
    monkeypatch.setattr(os.path, 'isdir', lambda x: True)
    monkeypatch.setattr(os.path, 'abspath', lambda x: mocked_abs_path)
    results = _path_to_results(
        FRED_RESULTS="/params/fred/results",
        FRED_HOME="/params/fred/home"
    )
    assert(results == mocked_abs_path)


def test_path_to_results_with_all_env_vars_set_uses_fred_results_param(monkeypatch):
    """
    confirm that FRED results directory defaults to the 'FRED_RESULTS'
    environmental variable is both 'FRED_RESULTS' and 'FRED_HOME' are set
    as environmental variables
    """
    monkeypatch.setattr(os.path, 'isdir', lambda x: True)
    results = _path_to_results(
        FRED_RESULTS="/params/fred/results",
        FRED_HOME="/params/fred/home",
    )
    assert(results == "/params/fred/results")
