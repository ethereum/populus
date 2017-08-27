# POPULUS

[![Gitter chat](https://badges.gitter.im/pipermerriam/populus.png)](https://gitter.im/pipermerriam/populus "Gitter chat")
[![Build Status](https://travis-ci.org/pipermerriam/populus.png)](https://travis-ci.org/pipermerriam/populus)
[![Documentation Status](https://readthedocs.org/projects/populus/badge/?version=latest)](https://readthedocs.org/projects/populus/?badge=latest)
[![PyPi version](https://pypip.in/v/populus/badge.png)](https://pypi.python.org/pypi/populus)
[![PyPi downloads](https://pypip.in/d/populus/badge.png)](https://pypi.python.org/pypi/populus)


Ethereum Development Framework


[Documentation on ReadTheDocs](http://populus.readthedocs.org/en/latest/)


## Features

- compilation
- deployment
- testing (using pytest)
- management of test chains

## Config Changes
- "dir" key to chain, used as rel path to user's home, if none is provided by the caller


### Project
- location.contracts_source_dir: optional, if provided use relative path
- location.tests_dir: optional, if provided use relative path


## Tests
- Test a project with populus plugin
- Populus tests suite: $ py.test tests/
- Populus plugin tests: $ py.test tests_pytest_plugin

Note: Populus tests suite runs w/o the plugin. The plugin functionality is provided
 by the tests conftest.py file

## Testing options

Populus adds 3 pytest options, which are found as follows:

- command line
- pytest.in
- environment varaibles
- default

### Project
- cli: --populus-project
- ini: populus_project
- environ: POPULUS_PYTEST_PROJECT
- default: the pytest running root directory

### User Configuration
- cli: --populus-user-config
- ini: populus_user_config
- environ: POPULUS_PYTEST_USER_CONFIG
- default: ~/.populus

### Chain Name
- cli: --populus-chain-name
- ini: populus_chain_name
- environ: POPULUS_PYTEST_CHAIN_NAME
- default: tester




