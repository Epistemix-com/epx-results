# Standard imports
import logging
import os
import re

# Vendor imports
from git.refs.tag import TagReference
from git.repo.base import Repo

# Internal imports
import metadata

logging.getLogger().setLevel(logging.DEBUG)

def execute():
    # Get version from file
    version_from_file: str
    version_file_path = os.path.join(metadata.ROOTPATH.parent, "epxresults/VERSION")
    with open(version_file_path) as f:
        version_from_file = f.read().strip()

    # Get release tags
    logging.debug(f'metadata.ROOTPATH.parent: {metadata.ROOTPATH.parent}')
    repo = Repo(metadata.ROOTPATH.parent)
    logging.debug(f'repo: {repo}')
    re_str = r"v([0-9]+)\.([0-9]+)\.([0-9]+)"
    release_tags = []
    for tagref in TagReference.list_items(repo):
        tag = str(tagref)
        match = re.match(re_str, tag)
        if match:
            release_tags.append(tag)
    # Get latest release tag
    latest_tag = release_tags[0]
    for curr_tag in release_tags[1:]:
        latest_re = re.match(re_str, latest_tag)
        curr_re = re.match(re_str, curr_tag)
        # Compare major, minor, then patch versions
        for latest, curr in zip(latest_re.groups(), curr_re.groups()):
            if curr > latest:
                latest_tag = curr_tag
                break
    # Create valid version list
    version_nums = re.match(re_str, latest_tag)
    major = int(version_nums[1])
    minor = int(version_nums[2])
    patch = int(version_nums[3])
    valid_versions = [
        f"{major + 1}.0.0",
        f"{major}.{minor + 1}.0",
        f"{major}.{minor}.{patch + 1}",
    ]

    # Check that version from file matches a valid version
    if version_from_file not in valid_versions:
        print(
            f"VERSION file is invalid: {version_from_file}.\n"
            + f"Expecting one of the following: {valid_versions}"
        )
        os._exit(1)
    else:
        print(f"VERSION file is valid: {version_from_file}")
        os._exit(0)
