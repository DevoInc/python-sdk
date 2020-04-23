#!/usr/bin/env python3
import codecs
import os
import sys
import re
from setuptools import setup, find_packages
from run_tests import TestCommand

META_PATH = os.path.join("devo", "__version__.py")
HERE = os.path.abspath(os.path.dirname(__file__))
PACKAGES = find_packages()
KEYWORDS = ["devo", "sdk", "developers"]
CLASSIFIERS = [
    "Programming Language :: Python",
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
INSTALL_REQUIRES = ['requests==2.23.0', 'click==7.1.1', 'PyYAML==5.3.1']
CLI = ['devo-sender=devo.sender.scripts.sender_cli:cli',
       'devo-api=devo.api.scripts.client_cli:cli']


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author="Devo, Inc.",
    author_email="support@devo.com",
    description="Devo Software Development Kit for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=find_meta("license"),
    name="devo-sdk",
    url="https://github.com/DevoInc/python-sdk",
    version=find_meta("version"),
    classifiers=CLASSIFIERS,
    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
    entry_points={
            'console_scripts': CLI
        }
)
