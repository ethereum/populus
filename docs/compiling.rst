Compiling
=========

Running ``$ populus compile`` will compile all of the project contracts found
in the ``./contracts/`` directory.  The compiled assets are then written to
``./build/contracts.json``.

.. note::

    Populus currently only supports compilation of Solidity contracts.


Basic Compilation
-----------------

Basic usage to compile all of the contracts and libraries in your project can
be done as follows.

.. code-block:: bash

    $ populus compile
    ============ Compiling ==============
    > Loading source files from: ./contracts

    > Found 1 contract source files
    - contracts/Greeter.sol

    > Compiled 1 contracts
    - Greeter

    > Wrote compiled assets to: ./build/contracts.json


Outside the project directory use:

    $ populus -p /path/to/my/project/ compile




Watching
--------

This command can be used with the flag ``--watch/-w`` which will automatically
recompile your contracts when the source code changes.

.. code-block:: bash

    $ populus compile --watch
    ============ Compiling ==============
    > Loading source files from: ./contracts

    > Found 1 contract source files
    - contracts/Greeter.sol

    > Compiled 1 contracts
    - Greeter

    > Wrote compiled assets to: ./build/contracts.json
    Change detected in: contracts/Greeter.sol
    ============ Compiling ==============
    > Loading source files from: ./contracts

    > Found 1 contract source files
    - contracts/Greeter.sol

    > Compiled 1 contracts
    - Greeter

    > Wrote compiled assets to: ./build/contracts.json


Build Output
------------

Output is serialized as ``JSON`` and written to ``build/contracts.json``
relative to the root of your project.  It will be a mapping of your contract
names to the compiled assets for that contract.


.. code-block:: javascript

    {
        "Greeter": {
            "abi": [
                {
                    "constant": false,
                    "inputs": [
                        {
                            "name": "_greeting",
                            "type": "string"
                        }
                    ],
                    "name": "setGreeting",
                    "outputs": [],
                    "payable": false,
                    "type": "function"
                },
                {
                    "constant": true,
                    "inputs": [],
                    "name": "greet",
                    "outputs": [
                        {
                            "name": "",
                            "type": "string"
                        }
                    ],
                    "payable": false,
                    "type": "function"
                },
                {
                    "constant": true,
                    "inputs": [],
                    "name": "greeting",
                    "outputs": [
                        {
                            "name": "",
                            "type": "string"
                        }
                    ],
                    "payable": false,
                    "type": "function"
                },
                {
                    "inputs": [],
                    "payable": false,
                    "type": "constructor"
                }
            ],
            "bytecode": "0x6060604052....",
            "bytecode_runtime": "0x6060604052....",
            "metadata": {
                "compiler": {
                    "version": "0.4.8+commit.60cc1668.Darwin.appleclang"
                },
                "language": "Solidity",
                "output": {
                    "abi": [
                        {
                            "constant": false,
                            "inputs": [
                                {
                                    "name": "_greeting",
                                    "type": "string"
                                }
                            ],
                            "name": "setGreeting",
                            "outputs": [],
                            "payable": false,
                            "type": "function"
                        },
                        {
                            "constant": true,
                            "inputs": [],
                            "name": "greet",
                            "outputs": [
                                {
                                    "name": "",
                                    "type": "string"
                                }
                            ],
                            "payable": false,
                            "type": "function"
                        },
                        {
                            "constant": true,
                            "inputs": [],
                            "name": "greeting",
                            "outputs": [
                                {
                                    "name": "",
                                    "type": "string"
                                }
                            ],
                            "payable": false,
                            "type": "function"
                        },
                        {
                            "inputs": [],
                            "payable": false,
                            "type": "constructor"
                        }
                    ],
                    "devdoc": {
                        "methods": {}
                    },
                    "userdoc": {
                        "methods": {}
                    }
                },
                "settings": {
                    "compilationTarget": {
                        "contracts/Greeter.sol": "Greeter"
                    },
                    "libraries": {},
                    "optimizer": {
                        "enabled": true,
                        "runs": 200
                    },
                    "remappings": []
                },
                "sources": {
                    "contracts/Greeter.sol": {
                        "keccak256": "0xe7900e8d25304f64a90939d1d9f90bb21268c4755140dc396b8b4b5bdd21755a",
                        "urls": [
                            "bzzr://7d6c0ce214a43b81f423edff8b18e18ad7154b7f364316bbd3801930308c1984"
                        ]
                    }
                },
                "version": 1
            }
        }
    }


Configuration
-------------

The following configuration options can be set to control aspects of how
Populus compiles your project contracts.


* ``compilation.contracts_source_dir``

  Defaults to ``./contracts``.  This sets the root path where populus will
  search for contract source files.

* ``compilation.settings.optimize``

  Defaults to ``True``.  Determines if the optimizer will be enabled during compilation.
