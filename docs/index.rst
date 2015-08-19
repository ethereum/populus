.. Populus documentation master file, created by
   sphinx-quickstart on Thu Oct 16 20:43:24 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Populus
=======

Populus is a framework for developing applications for Ethereum.


Installation
------------

install ``populus``

.. code-block:: shell

   $ pip install populus


Project Layout
--------------

By default populus expects a project to be layed out as follows.

.. code-block::

    ├── project root
    │   ├── build
    │   │   └── contracts.json
    │   └── contracts
    │       └── MyContract.sol
    |       ├── ....


Command Line Options
--------------------

.. code-block::

    $ populus
    Usage: populus [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      compile  Compile contracts.
      deploy   Deploy contract(s).


``compile``
~~~~~~~~~~~

Running ``$ populus compile`` will compile all of the contracts found in the
project.  The compiled projects are stored in ``./build/contracts.json``.

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


``deploy``
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


Contents:

.. toctree::
   :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
