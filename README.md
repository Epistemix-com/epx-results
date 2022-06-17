# epx-results

epx-results is a Python package for interacting with FRED simulation results. The documentation for this projected is hosted by Read the Docs [here](https://epistemix-epx-results.readthedocs-hosted.com/en/latest/index.html), including installation instructions, a quickstart guide, and a complete API reference.


## Requirements

In order to use the functions in this package, you will need the following Python packages installed:

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

To set up a fresh development environment to to work on `epx-results`, we
recommend using Python's built in
[`venv`](https://docs.python.org/3/library/venv.html) module to create a fresh
virtual environment. This helps to ensure that if something stops working in
the development environment, the explanation is inside the `epx-results`
repository itself, rather than because of some other software installed in a
general purpose environment.

Start by activating a Python environment containing a Python
executable with the same version you want to use for package development (e.g.
3.8).

```shell
$ python -m venv .venv
$ source .venv/bin/activate
$ which python
/Users/username/Projects/epx-results/.venv/bin/python
```

When actively working on this package, it is often convenient to install
epx-results in an environment in "editable" mode using the `-e` option to `pip`:

```shell
pip install -e .
```

### Local Development with Docker

You can develop locally via [Docker](https://www.docker.com). It is also
recommended to install [Docker
Compose](https://docs.docker.com/compose/gettingstarted/) to streamline local
development with Docker.

To develop inside a container, run the following:
```terminal
docker-compose run --rm dev
```

This will start a Bash session **inside a container** with all dependencies installed and the local epx-results source code mounted as a volume. This allows you to edit code on your machine and execute it within the container.

---
**NOTE**

You will need to be authenticated to our AWS Docker Registry (ECR) to pull the base image. You can find
[additional information on Confluence](https://epistemix.atlassian.net/wiki/spaces/ES/pages/23265384/AWS)
or reach out to bob.frankeny@epistemix.com.

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
docker-compose run --rm dev
```

This will place you in a Docker environment. If this fails, please make sure you
have completed the steps in the section above about developing in Docker.

Within this environment, you can then execute:

```terminal
./tests/run_tests
```

to run the testing suite.

---

In order to run many of the tests in this package, you must generate some
example FRED simulation output. This is done automatically when running the full
testing suite, but you can regenerate this data yourself by running:

```terminal
python ./scripts/generate-test-data.py
```

This script runs example model(s), generating an example FRED results directory in `./tests/fred-results`.

### Release Process
We use [Semantic Versioning](https://semver.org/spec/v2.0.0.html), and keep a
`CHANGELOG.md` file to track changes to `epx-results`.

Create a new pull request into `main` with the label "release". This will
trigger a GitHub Actions workflow to verify the validity of the
`epxresults/VERSION` file. The workflow will fail if the version number is
invalid. Once the workflow succeeds, the release PR can be successfully merged
into the `main` branch. Also update the `CHANGELOG.md` as necessary.

Create the release on GitHub. From the `epx-results` [repo
page](https://github.com/Epistemix-com/epx-results) click:
- 'Releases'
- 'Draft a new release'
- Select the newly created tag from the 'Select a tag' dropdown

Name the release something like 'epx-results v1.0.0', and copy the release
notes from the `CHANGELOG.md` into the description box.
