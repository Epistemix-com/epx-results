"""
a testing suite for epxresults.job module
"""
import os

import pandas as pd

from epxresults.job import FREDJob
from epxresults.utils import return_job_id


###############################
# initializing FRED job objects
###############################


def test_1(pkg_test_env):
    """
    test init with job key
    """
    job = FREDJob(job_key="simpleflu")
    assert job.job_key == "simpleflu"


def test_2(pkg_test_env):
    """
    test init with job key and explicit FRED_RESULTS
    """
    FRED_RESULTS = os.environ["FRED_RESULTS"]
    os.environ["FRED_RESULTS"] = ""
    job = FREDJob(FRED_RESULTS=FRED_RESULTS, job_key="simpleflu")
    assert job.job_key == "simpleflu"


def test_3(pkg_test_env):
    """
    test init with job ID
    """
    test_job_id = return_job_id(job_key="simpleflu")
    job = FREDJob(job_id=test_job_id)
    assert job.job_key == "simpleflu"


def test_4(pkg_test_env):
    """
    test init with job ID and explicit FRED_RESULTS
    """
    test_job_id = return_job_id(job_key="simpleflu")
    FRED_RESULTS = os.environ["FRED_RESULTS"]
    os.environ["FRED_RESULTS"] = ""
    job = FREDJob(FRED_RESULTS=FRED_RESULTS, job_id=test_job_id)
    assert job.job_key == "simpleflu"


def test_5(pkg_test_env):
    """
    test init with path to job
    """
    test_job_id = return_job_id(job_key="simpleflu")
    FRED_RESULTS = os.environ["FRED_RESULTS"]
    os.environ["FRED_RESULTS"] = ""
    PATH_TO_JOB = os.path.join(FRED_RESULTS, "JOB", str(test_job_id))
    job = FREDJob(PATH_TO_JOB=PATH_TO_JOB)
    assert job.job_key == "simpleflu"


def test_get_job_state_table():
    job = FREDJob(job_key="simpleflu")
    tot_inf_e_df = job.get_job_state_table("INFLUENZA", "Exposed", "cumulative")
    new_inf_is_df = job.get_job_state_table("INFLUENZA", "InfectiousSymptomatic", "new")
    count_inf_ia_df = job.get_job_state_table("INFLUENZA", "InfectiousAsymptomatic", "count")

    assert tot_inf_e_df.columns.to_list() == ["run", "sim_day", "cumulative"]
    assert new_inf_is_df.columns.to_list() == ["run", "sim_day", "new"]
    assert count_inf_ia_df.columns.to_list() == ["run", "sim_day", "count"]

    test_dfs = [tot_inf_e_df, new_inf_is_df, count_inf_ia_df]
    for df in test_dfs:
        assert df["run"].dtype == "int64"
        assert df["sim_day"].dtype == "int64"
        data_col = [x for x in df.columns if x not in ["run", "sim_day"]][0]
        assert df[data_col].dtype == "int64"

        # Job contains 2 runs from 2020-01-01 to 2020-05-01. That's
        # 2 * 122 = 244 days in total
        print(len(df.index))
        assert len(df.index) == 244

        # Runs are 1-indexed
        assert df.iloc[0]["run"] == 1
        assert df.iloc[-1]["run"] == 2

        # sim days are 0-indexed
        assert df.iloc[0]["sim_day"] == 0
        assert df.iloc[-1]["sim_day"] == 121



def test_get_job_variable_table():
    job = FREDJob(job_key="simpleflu_with_vaccine")
    recovered_df = job.get_job_variable_table("flu_delay")

    assert recovered_df.columns.to_list() == ["run", "sim_day", "flu_delay"]
    assert recovered_df["run"].dtype == "int64"
    assert recovered_df["sim_day"].dtype == "int64"
    assert recovered_df["flu_delay"].dtype == "float64"

    # Job contains 3 runs from 2020-01-01 to 2020-05-01. That's
    # 3 * 122 = 366 days in total
    assert len(recovered_df.index) == 1008

    # Runs are 1-indexed
    assert recovered_df.iloc[0]["run"] == 1
    assert recovered_df.iloc[-1]["run"] == 3

    # sim days are 0-indexed
    assert recovered_df.iloc[0]["sim_day"] == 0
    assert recovered_df.iloc[-1]["sim_day"] == 335


def test_job_get_job_date_table():
    job = FREDJob(job_key="simpleflu")
    dates_df = job.get_job_date_table()
    assert dates_df.columns.to_list() == ["run", "sim_day", "sim_date"]
    assert dates_df["sim_day"].dtype == "int64"
    assert dates_df["sim_date"].dtype == "<M8[ns]"

    # Job contains 2 runs from 2020-01-01 to 2020-05-01. That's
    # 2 * 122 = 244 days in total
    assert len(dates_df.index) == 244
    assert dates_df.iloc[0]["sim_date"] == pd.Timestamp("2020-01-01")
    assert dates_df.iloc[-1]["sim_date"] == pd.Timestamp("2020-05-01")

    # Runs are 1-indexed
    assert dates_df.iloc[0]["run"] == 1
    assert dates_df.iloc[-1]["run"] == 2

    # sim days are 0-indexed
    assert dates_df.iloc[0]["sim_day"] == 0
    assert dates_df.iloc[-1]["sim_day"] == 121


def test_get_job_rt_table():
    job = FREDJob(job_key="simpleflu")
    rt_wide_df = job.get_job_rt_table("INFLUENZA", format="wide")
    assert rt_wide_df.columns.tolist() == ["RUN1", "RUN2"]
    assert rt_wide_df.index.name == "sim_day"
    assert rt_wide_df.index.max() == 121

    rt_long_df = job.get_job_rt_table("INFLUENZA")  # long format is default
    assert rt_long_df.columns.tolist() == ["run", "sim_day", "Rt"]
    assert len(rt_long_df.index) == 244


def test_get_job_gt_table():
    job = FREDJob(job_key="simpleflu")
    gt_wide_df = job.get_job_gt_table("INFLUENZA", format="wide")
    assert gt_wide_df.columns.tolist() == ["RUN1", "RUN2"]
    assert gt_wide_df.index.name == "sim_day"
    assert gt_wide_df.index.max() == 121

    gt_long_df = job.get_job_gt_table("INFLUENZA")  # long format is default
    assert gt_long_df.columns.tolist() == ["run", "sim_day", "Gt"]
    assert len(gt_long_df.index) == 244
