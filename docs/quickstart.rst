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

Installation from source can be done from the root of the project with the
following command.

.. code-block:: shell

   $ python setup.py install


Initializing a new project
--------------------------

Populus can initialize your project using the ``$ populus init`` command.

.. code-block:: shell

    $ populus init
    Created Directory: ./contracts
    Created Example Contract: ./contracts/Example.sol
    Created Directory: ./tests
    Created Example Tests: ./tests/test_example.py


Your project will now have a ``./contracts`` directory with a single Solidity
source file in it named ``Example.sol``, as well as a ``./tests`` directory
with a single test file named ``test_example.py``.

Compiling your contracts
------------------------

Before we compile our project, lets modify the example contract a little to
make it more interesting.  Modify the ``Example.sol`` file to have the
following contents.


.. code-block:: solidity

    contract Greeter {
        string public greeting;

        function Example() {
            greeting = "Hello!";
        }

        function changeGreeting(string _greeting) public {
            greeting = _greeting;
        }

        function greetMe() constant returns (string) {
            return greeting;
        }
    }


We can now compile our contract using ``$ populus compile``


.. code-block:: shell

    $ populus compile
    ============ Compiling ==============
    > Loading contracts from: ./contracts
    > Found 1 contract source files
    - contracts/Example.sol

    > Compiled 1 contracts
    - Greeter

    > Outfile: ./build/contracts.json




Usage
-----

See :doc:`usage`.

Tutorial
--------

See :doc:`tutorial`.

Compile
-------

See :doc:`compile`.

Blockchain management
---------------------

See :doc:`chain`.

DApp development environment
----------------------------

See :doc:`devenv`.


.. _Go Ethereum: https://github.com/ethereum/go-ethereum/
.. _Solidity: https://github.com/ethereum/solidity/
.. _PyEthereum: https://github.com/ethereum/pyethereum/
