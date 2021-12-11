"""
This script generates test FRED model data into a local FREED results
directory, PKG_TESTS_DIRECTORY, (which is .gitignore'd) so that the unit
tests in this package have realistic data to work against.

If you wish to run this via Docker run the following from the root of
the project:
   docker build -t epistemixpy .
   docker run --rm --env AWS_ACCESS_KEY_ID=<KEY> \
   --env AWS_SECRET_ACCESS_KEY=<SECRET> \
   -v $(pwd):/models epistemixpy ./scripts/generate-fred-result-data
"""

import os
from pathlib import Path
import subprocess
from unittest.mock import patch
from utils import is_docker_env, cd


__author__ = ['Andrew Lane', 'Duncan Campbell']
__all__ = ['main']


# paths
PKG_DIRECTORY = Path(os.path.abspath(__file__)).parent.parent
PKG_TESTS_DIRECTORY = Path(os.path.join(PKG_DIRECTORY, 'tests'))
PKG_FRED_RESULTS = os.path.join(f'{PKG_TESTS_DIRECTORY}', 'fred-results')

# FRED model tests
test_models = {'simpleflu': 'epx-results_simpleflu'}
locations = ['Jefferson_County_PA']
num_runs = 3
num_cores = 1


def main():
    """
    """

    if is_docker_env():
        print(f"Running in a docker environment...")
        if os.environ.keys() <= ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
            print("The `AWS_ACCESS_KEY_ID` env variable must be non-empty.")
            print("The `AWS_SECRET_ACCESS_KEY` env variable must be non-empty.")
        p = subprocess.run(['fred_install_location_codes.py', 'Jefferson_County_PA'])
        if p.returncode == 0:
            print("Sucesfully downloaed location data.")
        else:
            print("Failed to download location data. Make sure that the"
                  "`fred_install_location_codes.py` script is availabe in "
                  "your Docker environment.")

    print(f"Running FRED model(s) to generate test data in `{PKG_FRED_RESULTS}`.")

    with patch.dict('os.environ', {'FRED_RESULTS': PKG_FRED_RESULTS}):

        for test in test_models.keys():

            location = test
            job_key = test_models[location]

            # delete any previously run test job
            args = ['fred_delete', '-f', '-k', job_key]
            p = subprocess.run(args, capture_output=True)

            # run test job
            with cd(os.path.join(PKG_TESTS_DIRECTORY, location)):
                args = ['fred_job', '-k', job_key, '-p',
                        'main.fred', '-n', str(num_runs), '-m', str(num_cores)]
                p = subprocess.run(args, capture_output=True)

            if p.returncode != 0:
                print("Failed to generate all FRED test data.")

    print("Done.")


if __name__ == "__main__":
    main()
