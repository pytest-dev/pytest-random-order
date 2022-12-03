#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-random-order',
    version='1.1.0',
    author='Jazeps Basko',
    author_email='jazeps.basko@gmail.com',
    maintainer='Jazeps Basko',
    maintainer_email='jazeps.basko@gmail.com',
    license='MIT',
    url='https://github.com/jbasko/pytest-random-order',
    description='Randomise the order in which pytest tests are run with some control over the randomness',
    long_description=read('README.rst'),
    packages=[
        'random_order',
    ],
    include_package_data=True,
    python_requires=">=3.5.0",
    install_requires=[
        'pytest>=3.0.0',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='pytest random test order shuffle',
    entry_points={
        'pytest11': [
            'random_order = random_order.plugin',  # >=1.0.0
        ],
    },
)
