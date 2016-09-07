#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


readme = open(os.path.join(DIR, 'README.md')).read()


setup(
    name='populus',
    version="1.0.0rc4",
    description="""Ethereum Development Framework""",
    long_description=readme,
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/pipermerriam/populus',
    include_package_data=True,
    py_modules=['populus'],
    install_requires=[
        "click>=6.6",
        "configparser==3.5.0",
        "contextlib2>=0.5.4",
        "eth-testrpc>=0.8.0",
        "ethereum-tester-client>=1.1.0",
        "gevent>=1.1.2",
        "py-geth>=1.1.0",
        "py-solc>=0.4.0",
        "pysha3>=0.3",
        "pytest>=2.7.2",
        "toposort>=1.4",
        "web3>=2.7.0",
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
