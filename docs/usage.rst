Usage
=====

.. contents:: :local:

Introduction
------------

Populus provides `populus` command line command and `populus` package. Besides this, Populus interally uses and exposes

* `web3.py <https://github.com/pipermerriam/web3.py>`__

* `py-solc <https://github.com/pipermerriam/py-solc>`__

* `py-geth <https://github.com/pipermerriam/py-geth>`__

Project Layout
--------------

By default Populus expects a project to be layed out as follows.

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


.. _init:

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

Programmatic use
----------------

You can use and import Python modules from :py:mod:`populus` package.

Gevent asynchronous event loop notice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Populus and underlying libraries (py-geth, web3.py) use  `gevent <http://www.gevent.org/>`_. gevent is a coroutine -based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libev event loop.
