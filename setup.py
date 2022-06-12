"""
"""

from pathlib import Path
import pip
from setuptools import setup, find_packages
import os
from setuptools.command.install import install
from setuptools.command.develop import develop
import sys
import subprocess

if int(pip.__version__.split(".")[0]) < 10:
    from pip import main as pip_main
else:
    # https://github.com/pypa/pip/issues/5080
    from pip._internal import main as pip_main

PACKAGENAME = "epx-results"


def read(file_name):
    """Read a text file and return the content as a string."""
    with open(
        os.path.join(os.path.dirname(__file__), file_name), encoding="utf-8"
    ) as f:
        return f.read()


VERSION = read("epxresults/VERSION").strip()

dev_requirements = ["tox"]

setup(
    name=PACKAGENAME,
    version=VERSION,
    setup_requires=["pytest-runner"],
    author="Duncan Campbell",
    author_email="duncan.campbell@epistemix.com",
    description="Python tools for FRED simulation results manipulation",
    long_description=(
        "A package which contains python tools for interacting "
        "with local FRED simulation results"
    ),
    install_requires=["pandas", "pytest", "networkx"],
    extras_require={"dev": dev_requirements},
    packages=find_packages(),
    url="https://github.com/Epistemix-com/epx-results",
    package_data={"epxresults": ["VERSION"]},
    cmdclass={},
)
