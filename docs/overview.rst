Overview
========

Populus is a framework for developing applications for Ethereum.


Installation
------------

install ``populus``

.. code-block:: shell

   $ pip install populus

Populus has one dependency that cannot be bundled with the package until
upstream changes are merged into the respective repository.  You can install
this dependencies directly with the following commands.

.. code-block:: shell

    $ pip install https://github.com/ethereum/ethash/archive/v23.1.tar.gz

See https://github.com/ethereum/ethash/issues/72 for detailed information on the
upstream changes that these two direct installs address.


Project Layout
--------------

By default populus expects a project to be layed out as follows.

.. code-block:: shell

    ├── project root
    │   ├── build
    │   │   └── contracts.json
    │   └── contracts
    │       ├── MyContract.sol
    |       ├── ....
    │   └── tests
    │       ├── test_my_contract.py
    │       ├── test_some_other_tests.py
    |       ├── ....


Command Line Options
--------------------

.. code-block:: shell

    $ populus --help
    Usage: populus [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      compile  Compile contracts.
      deploy   Deploy contracts.
      test     Test contracts (wrapper around py-test)
      watch    Watch the project contracts directory and...


``compile``
~~~~~~~~~~~

Running ``$ populus compile`` will compile all of the contracts found in the
project.  The compiled projects are stored in ``./build/contracts.json``.

* ``$ populus compile Example`` - compiles all contracts named Example.
* ``$ populus compile contracts/Example.sol`` - compiles all contracts in the specified file.
* ``$ populus compile contracts/Example.sol:Example`` - compiles all contracts named Example in in the specified file.

.. code-block:: javascript

    {
        "Example": {
            "code": "0x60606040525b5b600a8060136000396000f30060606040526008565b00",
            "info": {
                "abiDefinition": [
                    {
                        "inputs": [],
                        "type": "constructor"
                    }
                ],
                "compilerVersion": "0.9.73",
                "developerDoc": null,
                "language": "Solidity",
                "languageVersion": "0",
                "source": "contract Example {\n        function Example() {\n        }\n}\n",
                "userDoc": null
            }
        }
    }

.. note::

    Populus currently only supports compilation of Solidity contracts.


deploy``
~~~~~~~~~~


Running ``$ populus deploy`` will deploy all compiled contracts found in
``./build/contracts.json``.  Deployment requires an Ethereum JSON RPC server to
be running on ``localhost:8545``.  For testing, you can use the ``eth-testrpc``
python library.

This deployment uses the account returned by ``eth_coinbase`` as the ``from``
address for the transaction.

.. code-block:: shell

    $ populus deploy
    Example    : addr: 0xc305c901078781c232a2a521c2af7980f8385ee9 via txn:0xbba0f1cc96adb3c31a14bd5271d9a8c82b6aa1ddac2c7161bcb52ef6f3b9f813


``test``
~~~~~~~~~~


Running ``$ populus test`` will run all of the tests found in the ``./tests``
directory of your project using the compiled contracts currently found in the
``./build`` directory of your project.


.. code-block:: shell

    $ populus test
    =================================== test session starts ===================================
    platform darwin -- Python 2.7.10 -- py-1.4.30 -- pytest-2.7.2 -- /usr/bin/python
    rootdir: /path/to/my-project, inifile: pytest.ini
    plugins: populus, capturelog, timeout
    collected 2 items

    tests/test_example.py::test_contracts_has_correct_functions PASSED
    tests/test_example.py::test_contract_function_return_values PASSED

    ================================ 2 passed in 0.82 seconds =================================


``watch``
~~~~~~~~~~


Running ``$ populus watch`` will watch the ``./contracts`` directory of your
project and recompile all contracts when any of your contracts change.


.. code-block:: shell

    ============ Watching ==============
    
    # Then you save a file....

    ============ Detected Change ==============
    > modified => /Users/pipermerriam/Sites/populus/tmp/contracts/Example.sol
    > recompiling...
    > watching...
