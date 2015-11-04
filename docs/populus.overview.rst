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
    │   ├── contracts
    │   |   ├── MyContract.sol
    |   |   ├── ....
    │   ├── libraries
    │   |   ├── MyLibrary.sol
    |   |   ├── ....
    │   ├── tests
    │   |   ├── test_my_contract.py
    │   |   ├── test_some_other_tests.py
    |   |   ├── ....
    │   ├── html
    │   │   └── index.html
    │   └── assets
    │       └── ....


Command Line Options
--------------------

.. code-block:: shell

    $ populus --help
    Usage: populus [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      attach   Enter a python shell with contracts and...
      chain    Wrapper around `geth`.
      compile  Compile project contracts, storing their...
      deploy   Deploy contracts.
      init     Generate project layout with an example...
      web      HTML/CSS/JS tooling.


Initialize
~~~~~~~~~~

Running ``$ populus init`` will initialize the current directory with the
default project layout that populus uses.

* ``./contracts/``
* ``./contracts/Example.sol``
* ``./tests/test_examply.py``
* ``./html/index.html``
* ``./assets/``


Attach
~~~~~~

Running ``$ populus attach`` with place you in an interactive python shell with
your contract classes and an RPC client available in the local namespace.


.. code-block:: shell

    $ populus attach
    Python: 2.7.10 (default, Jul 13 2015, 12:05:58)

    Populus: v0.5.2

    Project Path: /path/to/my-project/

    contracts  -> Contract classes
    client     -> Blockchain client (json-rpc)

    Contracts: Example, AnotherExample

    ... > 


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


Deploy
~~~~~~

.. code-block:: shell

    $ populus deploy --help
    Usage: populus deploy [OPTIONS] [CONTRACTS_TO_DEPLOY]...

      Deploys the specified contracts via the RPC client.

    Options:
      -d, --dry-run                  Do a dry run deploy first.  When doing a
                                     production deploy, you should always do a dry
                                     run so that deploy gas prices can be known.
      -n, --dry-run-chain-name TEXT  Specifies the chain name that should be used
                                     for the dry run deployment.  Defaults to
                                     'default'
      -p, --production               Deploy to a production chain (RPC server must
                                     be run manually)
      --confirm / --no-confirm       Bypass any confirmation prompts
      --help                         Show this message and exit.

Running ``$ populus deploy`` will deploy all specifed contracts to either the
default test chain or to a running JSON-RPC server depending on whether
``--production`` was specified.

If the ``--dry-run`` flag is specified, then the gas value supplied for each
contract's deployment will be determined based on how much gas was used during
the dry run deployment.

When using the ``--production`` flag populus will not run the JSON-RPC for you.
You are expected to have an RPC server running with an unlocked account.  Doing
a production deploy without ``--dry-run`` is not advisable.  Doing a dry run
ensures that all of your contracts are deployable as well as allowing the
production deployment to supply gas values determined from the dry run
deployments.

.. note::
    When using libraries, populus will try to link your libraries.  This
    functionality is experimental and could still have bugs.


Chain
~~~~~

Populus provides a wrapper around ``geth`` to facilitate management of
ephemeral test chains.  These commands are accessed through ``$ populus chain``

The blockchains that populus manages for you are stored in ``./chains`` in the
projec root.  All ``chain`` commands will operate on the 'default' chain.  You
can specify alternate chains by adding a name to the end of the command.

Each blockchain will have one account generated for it.

* ``$ populus chain run`` - Run a geth node backed by the 'default' test chain.
* ``$ populus chain run test1`` - Run a geth node backed by the 'test1' test
  chain which will be stored at ``./chains/test1/`` relative to your project
  root.
* ``$ populus chain reset`` - Reset the 'default' chain (truncates the
  blockchain, preserves accounts)
* ``$ populus chain reset test01`` - Reset the 'test1' chain (truncates the
  blockchain, preserves accounts)


Web
~~~

Populus provides utilies for running a development webserver for DApp
development.  These commands are accessed via ``$ populus web``

Initialization
^^^^^^^^^^^^^^

You can initialize the html/css/js portions of your project with ``$populus web init``.

This will create ``html`` and ``assets`` directories in your project root. As
well as an ``./html/index.html`` document.


.. code-block:: shell
    ├── project root
    │   ├── html
    │   │   └── index.html
    │   └── assets
    │       └── ....


Runserver
^^^^^^^^^

Use ``$ populus web runserver`` to run the development server.

.. note:: This feature is extremely new and under active development.  Your contracts, while available as web3 contracts, are not automatically deployed.  Next steps in developing this will include running one of the test chains in the background and having your contracts auto-deployed to that chain.


Static assets
"""""""""""""

The development server is a simple flask application that serves your
``./html/index.html`` document as well as providing access to the static assets
in the ``./assets/`` directory.  All of the assets in that directory can be
accessed in your html document prefixed with the url ``/static/``.  For
example, the css file ``./assets/css/base.css`` would be accessible with the
url ``/static/css/base.css``.

The ``runserver`` command also watches for changes to your contracts and
assets, recompiling, or recollecting assets as necessary.

web3.js
"""""""

Populus includes a vendored version of ``web3.js``.  If you would like to
provide your own, simply place it at ``./assets/js/web3.js`` and your version
will be used instead.


javascript contracts
""""""""""""""""""""

All of your contracts are accessible via the ``contracts`` object which is
available in the global javascript scope.  This is provided by a generated
``js/contracts.js`` file.

.. warning:: if you place a file at ``./assets/js/contracts.js`` then you will have overridden the generated javascript file that provides access to your contracts.
