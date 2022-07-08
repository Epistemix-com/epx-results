# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic
Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## Added

- added `delete_snapshots()` method to `FREDJob` class.
- added `delete()` method to `Snapshot` class.
- added `get_network()` method to `FREDRun` class.
- added `networkx` as a package dependency.
- added `get_list_table_variable()` method to `FREDRun` class.
- added `get_population_size()` method to `FREDRun` class.
- added `get_job_population_size_table()` method to `FREDJob` class.

## Fixed

## [0.1.0] - 2022-04-20

## Added

- added `delete` method to `FREDJob` class.
- added a method to FREDRun, get_table_variable, that loads table varibale out for a FRED run.

## Fixed

- fixed a bug in the `insert._write_local_keys` function that cuased an error when
  deleting all jobs in a FRED results directory.

## [0.0.1] - 2022-02-28

### Added

- Support for retrieving snapshots for jobs from a `FREDJob` object, and
  `Snapshot` class added.
- `FREDJob` methods for retrieving data for Rt and Gt special FRED variables
  (`get_job_rt_table` and `get_job_gt_table`).
- `get_state` method added to `FREDRun` (series of state counts in a FRED
  condition)
- `get_variable` method added to `FREDRun`
- `get_list_variable` method added to `FREDRun`
- Tutorial in documentation for interacting with `FREDJob` to retrieve data for
  a global variable.

### Fixed

- Update Read the Docs config so documentation builds correctly
- update FREDRun class doc strings
