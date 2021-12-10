"""
Python utilities for spx-results/scripts
"""

import os

__author__ = ['Duncan Campbell']
__all__ = ['is_docker_env', 'cd']


def is_docker_env() -> bool:
    """
    Is this current environment running in docker?
    """
    return os.path.exists('/.dockerenv') or _text_in_file('docker', '/proc/self/cgroup')


class cd:
    """
    Context manager for changing the current working directory
    """

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def _text_in_file(text, filename) -> bool:
    """
    if a file exists, test if it contains text
    """
    if os.path.isfile(filename):
        return any(text in line for line in open(filename))
    else:
        return False
