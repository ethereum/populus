Compile
~~~~~~~

Running ``$ populus compile`` will compile all of the contracts found in the
``./contracts/`` directory as well as all libraries found in the
``./libraries/`` directory.  The compiled projects are stored in
``./build/contracts.json``.

.. note::

    Currently, populus only supports import statemens for solidity files found
    in the ``./libraries/`` directory.  These should be in the format ``import
    "libraries/MyLibrary.sol";``.

Basic usage to compile all of the contracts and libraries in your project can
be done as follows.

.. code-block:: shell

    $ populus compile
    ============ Compiling ==============
    > Loading contracts from: /var/projects/my-project/contracts
    > Found 2 contract source files
    - mortal.sol
    - owned.sol

    > Compiled 3 contracts
    - Immortal
    - Mortal
    - owned

    > Outfile: /var/projects/my-project/build/contracts.json


If you only want to build a sub-set of your contracts you can specify paths to
source files, or the names of contracts in source files, or a combination of
the two separated by a ``:``.

* ``$ populus compile Example`` - compiles all contracts named Example.
* ``$ populus compile contracts/Example.sol`` - compiles all contracts in the
  specified file.
* ``$ populus compile contracts/Example.sol:Example`` - compiles all contracts
  named Example in in the specified file.


Additionally, you can pass in ``--watch`` to have Populus watch your contract
source files and automatically rebuild them when those files change.

.. code-block:: shell

    $ populus compile --watch
    ============ Compiling ==============
    > Loading contracts from: /var/projects/my-project/contracts
    > Found 2 contract source files
    - mortal.sol
    - owned.sol

    > Compiled 3 contracts
    - Immortal
    - Mortal
    - owned

    > Outfile: /var/projects/my-project/build/contracts.json
    ============ Watching ==============

    # Then you save a file....

    ============ Detected Change ==============
    > modified => /var/projects/my-project/contracts/mortal.sol
    > recompiling...
    > watching...


Output is serialized as ``JSON`` and written to ``build/contracts.json``
relative to the root of your project.

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