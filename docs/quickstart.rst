Quickstart
==========

.. contents:: :local:


System Dependencies
-------------------

Populus depends on the following system dependencies.

* `Solidity`_ : For contract compilation
* `Go Ethereum`_: For running test chains and contract deployment.

In addition, populus needs some system dependencies to be able to install the
`PyEthereum`_ library.

Debian, Ubuntu, Mint
~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

    sudo apt-get install libssl-dev


Fedora, CentOS, RedHat
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

    sudo yum install openssl-devel


OSX
~~~

.. code-block:: shell

    brew install pkg-config libffi autoconf automake libtool openssl


Installation
------------

Populus can be installed using ``pip`` as follows.

.. code-block:: shell

   $ pip install populus


By default populus will use standard library tools for io operations like
threading and subprocesses.  Populus can be configured to instead use
``gevent``.  To install with gevent support:

.. code-block:: shell

   $ pip install populus[gevent]

To enable ``gevent`` set the environment variable ``THREADING_BACKEND=gevent``.

Installation from source can be done from the root of the project with the
following command.

.. code-block:: shell

   $ python setup.py install


Initializing a new project
--------------------------

Populus can initialize your project using the ``$ populus init`` command.

.. code-block:: shell

    $ populus init
    Wrote default populus configuration to `./populus.json`.
    Created Directory: ./contracts
    Created Example Contract: ./contracts/Greeter.sol
    Created Directory: ./tests
    Created Example Tests: ./tests/test_greeter.py


Your project will now have a ``./contracts`` directory with a single Solidity
source file in it named ``Greeter.sol``, as well as a ``./tests`` directory
with a single test file named ``test_greeter.py``.

Compiling your contracts
------------------------

Before you compile our project, lets take a look at the ``Greeter`` contract
that is generated as part of the project initialization.


.. code-block:: solidity

    pragma solidity ^0.4.0;

    contract Greeter {
        string public greeting;

        function Greeter() {
            greeting = "Hello";
        }

        function setGreeting(string _greeting) public {
            greeting = _greeting;
        }

        function greet() constant returns (string) {
            return greeting;
        }
    }

``Greeter`` is simple contract that is initialized with a default greeting of
the string ``'Hello'``.  It exposes the ``greet`` function which returns
whatever string is set as the greeting, as well as a ``setGreeting`` function
which allows the greeting to be changed.

You can now compile the contract using ``$ populus compile``


.. code-block:: shell

    $ populus compile
    ============ Compiling ==============
    > Loading source files from: ./contracts

    > Found 1 contract source files
    - contracts/Greeter.sol

    > Compiled 1 contracts
    - Greeter

    > Wrote compiled assets to: ./build/contracts.json


Testing your contract
---------------------

Now that you have a basic contract you'll want to test that it behaves as
expected.  The project should already have a test module named
``test_greeter.py`` located in the ``./tests`` directory that looks like the
following.

.. code-block:: python

    def test_greeter(chain):
        greeter, _ = chain.provider.get_or_deploy_contract('Greeter')

        greeting = greeter.call().greet()
        assert greeting == 'Hello'

    def test_custom_greeting(chain):
        greeter, _ = chain.provider.get_or_deploy_contract('Greeter')

        set_txn_hash = greeter.transact().setGreeting('Guten Tag')
        chain.wait.for_receipt(set_txn_hash)

        greeting = greeter.call().greet()
        assert greeting == 'Guten Tag'


You should see two tests, one that tests the default greeting, and one that
tests that we can set a custom greeting.  You can run tests using the
``py.test`` command line utility which was installed when you installed
populus.

.. code-block:: bash

    $ py.test tests/
    collected 2 items

    tests/test_greeter.py::test_greeter PASSED
    tests/test_greeter.py::test_custom_greeting PASSED

You should see something akin to the output above with three passing tests.

Setup for development and contribution
--------------------------------------

In order to configure the project locally and get the whole test suite passing, you'll 
need to make sure you're using the proper version of the ``solc`` compiler. Follow these
steps to install all the dependencies:

Virtual environment
~~~~~~~~~~~~~~~~~~~
If you don't already have it, go ahead and install ``virtualenv`` with ``pip install virtualenv``.
You can then create and activate your Populus environment with the following commands:

.. code-block:: bash

    $ cd populus
    $ virtualenv populus
    $ source populus/bin/activate

This allows you to install the specific versions of the Populus dependencies without conflicting
with global installations you may already have on your machine.

Install dependencies
~~~~~~~~~~~~~~~~~~~~
Now, run the following commands to install all the dependencies specified in the project
except for ``solc``:

.. code-block:: bash

    $ pip install -r requirements-dev.txt
    $ pip install -r requirements-docs.txt
    $ pip install -r requirements-gevent.txt
    $ pip install -e .

Install Solidity
~~~~~~~~~~~~~~~~
Here's where the fun begins: you'll have to build Solidity from source, and it
specifically needs to be the ``release_0.4.8`` branch. Here's how to do that:

First, clone the repository and switch to the proper branch:

.. code-block:: bash

    $ git clone --recursive https://github.com/ethereum/solidity.git
    $ cd solidity
    $ git checkout release_0.4.8

If you're on a Mac, you may need to accept the Xcode license as well. Make sure
you have the latest version installed, and if you run into errors, try the following:

.. code-block:: bash

    $ sudo xcodebuild -license accept

If you're on Windows, make sure you have Git, CMake, and Visual Studio 2015.

Now, install all the external dependencies.
For Mac:

.. code-block:: bash

    $ ./scripts/install_deps.sh

Or, for Windows:

.. code-block:: bash

    $ scripts\install_deps.bat

Finally, go ahead and build Solidity.
For Mac:

.. code-block:: bash

    $ mkdir build
    $ cd build
    $ cmake .. && make

Or, for Windows:

.. code-block:: bash

    $ mkdir build
    $ cd build
    $ cmake -G "Visual Studio 14 2015 Win64" ..

The following command will also work for Windows:

.. code-block:: bash

    $ cmake --build . --config RelWithDebInfo

Confirm
~~~~~~~
This should have installed everything you need, but let's be sure. First, try running:

.. code-block:: bash

    $ which solc

If you didn't see any output, you'll need to move the ``solc`` executable file into
the directory specified in your ``PATH``, or add an accurate ``PATH`` in your ``bash``
profile. If you can't find the file, you may need to run:

.. code-block:: bash

    $ npm install -g solc

This should install the executable wherever your Node packages live.

Once you see output from the ``which solc`` command (and you're in the Populus
directory with the ``virtualenv`` activated), you're ready to run the tests.

.. code-block:: bash

    $ py.test tests/

At this point, all your tests should pass. If they don't, you're probably missing a dependency
somewhere. Just retrace your steps and you'll figure it out.





.. _Go Ethereum: https://github.com/ethereum/go-ethereum/
.. _Solidity: https://github.com/ethereum/solidity/
.. _PyEthereum: https://github.com/ethereum/pyethereum/
