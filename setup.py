#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages


DIR = os.path.dirname(os.path.abspath(__file__))


readme = open(os.path.join(DIR, 'README.md')).read()


setup(
    name='populus',
    version="1.6.4",
    description="""Ethereum Development Framework""",
    long_description=readme,
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/pipermerriam/populus',
    include_package_data=True,
    py_modules=['populus'],
    install_requires=[
        "anyconfig>=0.7.0",
        "click>=6.6",
        "contextlib2>=0.5.4",
        "eth-testrpc>=1.1.0",
        "ethereum-utils>=0.2.0",
        "jsonschema>=2.5.1",
        "py-geth>=1.7.1",
        "py-solc>=1.0.0",
        "pylru>=1.0.9",
        "pysha3>=0.3,!=1.0,>1.0.0",
        "pytest>=2.7.2",
        "toposort>=1.4",
        "watchdog>=0.8.3",
        "web3>=3.7.1",
    ],
    extras_require={
        'gevent': [
            "gevent>=1.1.2,<1.2.0",  # https://github.com/gevent/gevent/issues/916
            "web3[gevent]>=3.7.1",
            "eth-testrpc[gevent]>=1.1.0",
            "py-geth[gevent]>=1.7.1",
            "py-solc[gevent]>=1.0.0",
        ],
    },
    license="MIT",
    zip_safe=False,
    entry_points={
        'console_scripts': ["populus=populus.cli:main"],
        'pytest11': ['ethereum=populus.plugin'],
    },
    keywords='ethereum pytest',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
