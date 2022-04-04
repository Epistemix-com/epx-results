# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic
Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- added `delete` method to `FREDJob` class.

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
