#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

with open(here / "README.md", encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(here / 'requirements.txt') as f:
    required = f.read().splitlines()

setup(
    author="Greg Michael",
    author_email="ggmichael@users.noreply.github.com",
    python_requires=">=3.8, <4",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="Craterstats - a tool to analyse and plot crater count data for planetary surface dating",
    entry_points={
        "console_scripts": [
            'craterstats=craterstats.cli:main',
        ],
    },
    license="BSD license",
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords=["craters"],
    name="craterstats",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "craterstats": ["config/*.txt", "config/*.plt", "sample/*.diam", "sample/*.r", "sample/*.scc",  "sample/*.binned", "sample/*.stat", "sample/README.md"]
    },
    test_suite="tests",
    tests_require=required,
    install_requires=required,
    url="https://github.com/ggmichael/craterstats",
    version="3.0.13",
)
