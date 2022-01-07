"""Setup package dot

Requires python 3.5+ for the subprocess.run() command

For development, inside this directory, install with:
> pip install -e .

This will install an "editable" version so modifications to the source code
are immediately reflected in the installed package.

Note: Use a virtual environment to isolate your development environment.
"""
import subprocess
from typing import List
from setuptools import setup, find_namespace_packages


def readme() -> str:
    """Load the contents of the readme file to use as part of package metadata
    """
    try:
        with open('README.md', 'r') as readme_file:
            readme_str = readme_file.read()
    except (FileNotFoundError, IOError):
        return ""
    else:
        return readme_str.strip()

def requirements() -> List[str]:
    """Load requirements specified in requirements.txt

    These requirements are passed to the setup function so installing with `pip`
    will first install these requirements.
    """
    try:
        with open('requirements.txt', 'r') as requirements_file:
            requirements_list = [x.strip() for x in requirements_file.readlines()]
    except (FileNotFoundError, IOError):
        return []
    else:
        return requirements_list

def version() -> str:
    """Prepare a version number for the package

    A "version" file can be used to specify a version.
    If not found, a default from the git has will be used.
    """
    try:
        with open('version') as version_file:
            version_tag = version_file.read().strip()
    except (FileNotFoundError, IOError):
        try:
            proc = subprocess.run(["git", "describe", "--always"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            return "0.0.0"
        return str(proc.stdout).strip()
    else:
        return version_tag

setup(
    name="dot",
    version=version(),
    description="Utilities for DOT project",
    long_description=readme(),
    author="U.Group",
    packages=find_namespace_packages(),
    include_package_data=True,
    requirements=requirements()
)
