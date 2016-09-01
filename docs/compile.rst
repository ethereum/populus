Compile
=======

Running ``$ populus compile`` will compile all of the project contracts found
in the ``./contracts/`` directory.  The compiled assets are then written to
``./build/contracts.json``.


Basic Compilation
-----------------

Basic usage to compile all of the contracts and libraries in your project can
be done as follows.

.. code-block:: shell

    $ populus compile
    ============ Compiling ==============
    > Loading source files from: ./contracts

    > Found 1 contract source files
    - contracts/Greeter.sol

    > Compiled 1 contracts
    - Greeter

    > Wrote compiled assets to: ./build/contracts.json


Watching
--------

This command can be used with the flag ``--watch`` which will automatically
recompile your contracts when the source code changes.

.. code-block:: shell

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
                    "constant": true,
                    "inputs": [
                        {
                            "name": "name",
                            "type": "bytes"
                        }
                    ],
                    "name": "greet",
                    "outputs": [
                        {
                            "name": "",
                            "type": "bytes"
                        }
                    ],
                    "type": "function"
                },
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
                    "type": "function"
                },
                {
                    "inputs": [],
                    "type": "constructor"
                }
            ],
            "code": "0x...",
            "code_runtime": "0x...",
            "meta": {
                "compilerVersion": "0.3.5-9da08ac3",
                "language": "Solidity",
                "languageVersion": "0"
            },
            "source": null
        }
    }

.. note::

    Populus currently only supports compilation of Solidity contracts.
