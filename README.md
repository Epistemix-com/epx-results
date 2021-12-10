# epx-results

epx-results is a Python package for interacting with FRED simulation results.


## Requirements

In order to use the functions in this package, you will need the following python packages installed:

- [Pandas](https://pandas.pydata.org)


## Installation

epx-results may be installed from source using [pip](https://pypi.org/project/pip/):

```terminal
$user: pip install .
```

You may then import epx-results in Python,

```python
>>> import epxresults
```

## Developers

### Local Development

When actively working on this package, it is often convenient to install epx-results in
an environment in "editable" mode using the `-e` opiton to `pip`:

```terminal
$user: pip install -e .
```

### Local Development with Docker

You can develop locally via [Docker](https://www.docker.com).

```terminal
$user: ./scripts/dev
```

This will start a Bash session **inside a container** with all dependencies installed and the local epx-results source code mounted as a volume. This allows you to edit code on your machine and execute it within the container.

---
**NOTE**

You will need to be authenticated to our AWS Docker Registry (ECR) to pull the base image. You can find
[additional information on Confluence](https://epistemix.atlassian.net/wiki/spaces/ES/pages/23265384/AWS)
or reach out to doug.difilippo@epistemix.com

---

#### Accessing Synthetic Population Data

We store synthetic population data files on AWS s3.
The docker container has scripts which access that data but require AWS credentials to do so.
[Confluence](https://epistemix.atlassian.net/wiki/spaces/ES/pages/23265384/AWS)
explains how to request the credentials.

Once you have credentials create `./.env` with the following

```bash
AWS_ACCESS_KEY_ID=<your access key>
AWS_SECRET_ACCESS_KEY=<your secret access key>
```

These credentials may be stored in `~/.aws/credentials` on your system.


### Testing Suite

This package comes with a testing suite. To run the testing suite, execute:

```terminal
./tests/run_tests
```

---
**NOTE**

To run the testing suite in a Docker environment, execute:

```terminal
ecr-login
./scripts/dev
```

This will place you in a Docker environmet. If this fails, please make sure you have completed the steps in the section above about developing in Docker.

Within this environment,
you can then execute:

```terminal
./tests/run_tests
```

to run the testing suite.

---

In order to run many of the tests in this package, you must generate some example FRED simulation output. This si done autmaticaly when running the full testing suite, but you can regenerate this data yourself by running:

```terminal
python ./scripts/generate-test-data.py
```

This script runs example model(s), generating an example FRED results directory in `./tests/fred-results`.
