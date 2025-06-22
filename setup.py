#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-random-order",
    author="Jazeps Basko",
    author_email="jazeps.basko@gmail.com",
    maintainer="Jazeps Basko",
    maintainer_email="jazeps.basko@gmail.com",
    license="MIT",
    url="https://github.com/jbasko/pytest-random-order",
    description="Randomise the order in which pytest tests are run with some control over the randomness",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    packages=[
        "random_order",
    ],
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "pytest",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="pytest random test order shuffle",
    entry_points={
        "pytest11": [
            "random_order = random_order.plugin",
        ],
    },
)
