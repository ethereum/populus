Overview
========

.. contents:: :local:

Introduction
------------

The primary interface to populus is the command line command ``$ populus``.


Command Line Options
--------------------

.. code-block:: shell

    $ populus
    Usage: populus [OPTIONS] COMMAND [ARGS]...

      Populus

    Options:
      -p, --project DIRECTORY  Specify a populus project directory to be used.
      -h, --help             Show this message and exit.

    Commands:
      chain          Manage and run ethereum blockchains.
      compile        Compile project contracts, storing their...
      deploy         Deploys the specified contracts to a chain.
      init           Generate project layout with an example...
      makemigration  Generate an empty migration.
      migrate        Run project migrations


Project Layout
--------------

By default Populus expects a project to be laid out as follows:

.. code-block:: shell

    └── project root
        ├── populus.json
        ├── build (automatically created during compilation)
        │   └── contracts.json
        ├── contracts
        |   ├── MyContract.sol
        |   ├── ....
        └── tests
            ├── test_my_contract.py
            ├── test_some_other_tests.py
            ├── ....
            └── ....


.. _init:


Initialize
~~~~~~~~~~

.. code-block:: shell

    $ populus init --help
    Usage: populus init [OPTIONS]

      Generate project layout with an example contract.

    Options:
      -h, --help  Show this message and exit.

Running ``$ populus init`` will initialize the current directory with the
default project layout that populus uses. If ``-p`` argument is provided, populus will init to that directory

* ``./contracts/``
* ``./contracts/Greeter.sol``
* ``./tests/test_greeter.py``

You can also init a project from another directory with:

.. code-block:: shell

    $ populus -p /path/to/my/project/ init

