#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

version = '0.1.4'

readme = open(os.path.join(DIR, 'README.md')).read()


setup(
    name='populus',
    version=version,
    description="""Ethereum Development Framework""",
    long_description=readme,
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/pipermerriam/populus',
    include_package_data=True,
    py_modules=['populus'],
    install_requires=[
        "click>=5.0",
        # Until https://github.com/ethereum/ethash/issues/72 is resolved
        # "ethash>=23.1",
        "ethereum>=0.9.73",
        "requests>=2.7.0",
        # Until https://github.com/ConsenSys/eth-testrpc/pull/16 is merged and
        # released.
        # "eth-testrpc>=0.1.15",
        "pytest>=2.7.2",
        "ethereum-rpc-client>=0.1.0",
    ],
    dependency_links=[
        # Until https://github.com/ConsenSys/eth-testrpc/pull/16 is merged and
        # released.
        "https://github.com/pipermerriam/eth-testrpc/archive/v0.1.15b.tar.gz",
        # Until https://github.com/ethereum/ethash/issues/72 is resolved
        "https://github.com/ethereum/ethash/archive/v23.1.tar.gz",
    ],
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
