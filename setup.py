#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = "iacr-dl"
URL = "https://github.com/znewman01/iacr-dl"
EMAIL = "znewman01@gmail.com"
AUTHOR = "Zachary Newman"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = "0.1.0"
DESCRIPTION = "`iacr-dl` is a package for accessing the Cryptology ePrint Archive."


here = os.path.abspath(os.path.dirname(__file__))


def read_requirements(fname):
    with io.open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
        return f.read().splitlines()


REQUIRED = read_requirements("requirements.txt")
TEST_REQUIRED = read_requirements("requirements-test.txt")

with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = "\n" + f.read()

# Load the package's __version__.py module as a dictionary.
about = {"__version__": VERSION}


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    py_modules=["iacr"],
    install_requires=REQUIRED,
    tests_require=TEST_REQUIRED,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    # $ setup.py publish support.
    cmdclass={"upload": UploadCommand},
)
