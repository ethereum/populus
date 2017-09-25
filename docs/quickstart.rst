Quickstart
==========

Welcom to Populus! Populus has (almost) everything you need for Ethereum blockchain development.

.. contents:: :local:


System Dependencies
-------------------

Populus depends on the following system dependencies.

* The `Solidity`_ Compiler : Contracts are authored in the Solidity language, and then compiled to the bytecode of the Ethereum Virtual Machine (EVM).
* `Geth`_: The official Go implementation of the Ethereum protocol. The Geth client runs a blockchain node, lets you interact with the blockchain, and also runs and deploys to the test blockchains during development.

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


Install Populus
---------------

Populus can be installed using ``pip`` as follows.

.. code-block:: shell

   $ pip install populus

If you are installing on Ubuntu, and working with python3 (recommended):

.. code-block:: shell

    $ pip3 install populus


.. note::

    With Ubuntu, use Ubuntu's pip:

    ``$sudo apt-get install python-pip``

    or, for python 3:

    ``$sudo apt-get install python3-pip``

    You may need to install populus with sudo: ``$ sudo -H pip install populus``



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


Verify your installation

.. code-block:: shell

      $ populus

      Usage: populus [OPTIONS] COMMAND [ARGS]...

        Populus

      Options:
        -p, --project PATH  Specify a populus project directory
        -l, --logging TEXT  Specify the logging level.  Allowed values are
                            DEBUG/INFO or their numeric equivalents 10/20
        -h, --help          Show this message and exit.

      Commands:
        chain    Manage and run ethereum blockchains.
        compile  Compile project contracts, storing their...
        config   Manage and run ethereum blockchains.
        deploy   Deploys the specified contracts to a chain.
        init     Generate project layout with an example...


Great. Let's have the first populus project.




Initializing a New Project
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

Alternatively, you can init a new project by a directory:

.. code-block:: shell

    $ populus -p /path/to/my/project/ init


Compiling your contracts
------------------------

Before you compile our project, lets take a look at the ``Greeter`` contract
that is generated as part of the project initialization.

.. code-block:: shell

    $ nano contracts/Greeter.sol

.. note::

    Check your IDE for Solidity extention/package.


Here is the contract:

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

``Greeter`` is simple contract:

* The ``contract`` keyword starts a contract definition
* The contract has one public "state" variable, named ``greeting``.
* The contract constrator function, ``function Greeter()``, which has the same name of the contract, initializes with a default greeting of the string ``'Hello'``.
* The function ``greet`` is exposed, and returns whatever string is set as the greeting,
* Also, the ``setGreeting`` function is available,  and allows the greeting to be changed.

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

For compiling outside the project directory use:

.. code-block:: shell

    $ populus -p /path/to/my/project/ compile

The build/contracts.json file contains a lot of information that the Solidity compiler produced.
This is required to deploy and work with the contract. Some important info is the
application binary interface (ABI) of the contract, which will allow to call it's functions after it's compiled,
and the bytecode required to deploy the contract, and the bytecode that will run once the contract sits on the blockchain.

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
tests that we can set a custom greeting.

Note that both test functions accept a ``chain`` argument. This "chain" is actually py.test fixture, provided by the populus pytest plugin.
The chain in the tests is a populus "chain" object that runs a temporary blockchain called "tester". It quits after the test and saves nothing,
so obviously not usable for long term runnig contracts, but great for testing.

You can run tests using the
``py.test`` command line utility which was installed when you installed
populus.

.. code-block:: bash

    $ py.test tests/
    collected 2 items

    tests/test_greeter.py::test_greeter PASSED
    tests/test_greeter.py::test_custom_greeting PASSED

You should see something akin to the output above with three passing tests.

Finally, similarly to the tests deployment, test the same deployment from the command line:

.. code-block:: bash

    $ populus deploy --chain tester --no-wait-for-sync
    > Found 1 contract source files
    - contracts/Greeter.sol
    > Compiled 1 contracts
    - contracts/Greeter.sol:Greeter
    Please select the desired contract:

        0: Greeter

Type 0 at the prompt, and enter.

.. code-block:: bash


    Beginning contract deployment.  Deploying 1 total contracts (1 Specified, 0 because of library dependencies).

    Greeter
    Deploying Greeter
    Deploy Transaction Sent: 0x84d23fa8c38a09a3b29c4689364f71343058879639a617763ce675a336033bbe
    Waiting for confirmation...

    Transaction Mined
    =================
    Tx Hash      : 0x84d23fa8c38a09a3b29c4689364f71343058879639a617763ce675a336033bbe
    Address      : 0xc305c901078781c232a2a521c2af7980f8385ee9
    Gas Provided : 465729
    Gas Used     : 365729


    Verified contract bytecode @ 0xc305c901078781c232a2a521c2af7980f8385ee9
    Deployment Successful.

Nice. Of course, since this is an ad-hoc "tester" chain, it quits immediately, and nothing is really saved. But the deployment works and should
work on a permanent blockchain, like the mainnet or testnet.

Again, outside the project directory use:

.. code-block:: shell

    $ populus -p /path/to/my/project/ deploy --chain tester --no-wait-for-sync


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
specifically needs to be the ``release_0.4.13`` branch. Here's how to do that:

First, clone the repository and switch to the proper branch:

.. code-block:: bash

    $ git clone --recursive https://github.com/ethereum/solidity.git
    $ cd solidity
    $ git checkout release_0.4.13

You can also download the tar or zip file at:

    https://github.com/ethereum/solidity/releases

.. note::

    Use the tar.gz file to build from source, and make sure, after extracting the file, that the "deps" directory is not empty
    and actually contains the dependencies.

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





.. _Geth: https://github.com/ethereum/go-ethereum/
.. _Solidity: https://github.com/ethereum/solidity/
.. _PyEthereum: https://github.com/ethereum/pyethereum/
