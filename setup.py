"""
"""

from pathlib import Path
import pip
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import sys
import subprocess

if int(pip.__version__.split('.')[0]) < 10:
    from pip import main as pip_main
else:
    # https://github.com/pypa/pip/issues/5080
    from pip._internal import main as pip_main

PACKAGENAME = "epx-results"
VERSION = "0.0"

setup(
    name=PACKAGENAME,
    version=VERSION,
    setup_requires=["pytest-runner"],
    author="Duncan Campbell",
    author_email="duncan.campbell@epistemix.com",
    description="Python tools for FRED simulation results manipulation",
    long_description=("A package which contains python tools for interacting "
                      "with local FRED simulation results"),
    install_requires=['pandas'],
    packages=find_packages(),
    url="https://github.com/Epistemix-com/epx-results",
    package_data={},
    cmdclass={},
)
