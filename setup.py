#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='populus',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='2.2.0',
    description="""Ethereum Development Framework""",
    long_description_markdown_filename='README.md',
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/ethereum/populus',
    include_package_data=True,
    py_modules=['populus'],
    setup_requires=['setuptools-markdown'],
    python_requires='>=3.4,<4',
    install_requires=[
        "anyconfig>=0.7.0",
        "click>=6.6",
        "contextlib2>=0.5.4",
        "eth-tester[py-evm]==0.1.0-beta.26",
        "eth-utils>=1.0.3,<2.0.0",
        "jsonschema>=2.5.1",
        "py-geth>=1.9.0",
        "py-solc>=1.2.0",
        "pylru>=1.0.9",
        "pysha3>=0.3,!=1.0,>1.0.0",
        "pytest>=2.7.2,!=3.3.*",
        "semantic_version>=2.6.0",
        "cytoolz>=0.8.2",
        "toposort>=1.4",
        "watchdog>=0.8.3",
        "web3>=4.4.0,<5",
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
