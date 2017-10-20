Part 3: First Test
==================

.. contents:: :local:

Tests and Chains
----------------

For testing, we will use the ``tester`` chain again. It's very convinient blockchain for tests,
because it reset on each run, and the state is saved only in memory and cleared after each run.
In a way, this is a similar idea to running tests against a DB,
where you create an ad-hoc temporary DB for the tests.

You will run Populus tests with ``py.test``, which was installed when you installed Populus.

Add a test file:

.. code-block:: bash

  $ nano tests/test_donator.py

.. note::

    py.test collects all the tests that follow
    it's `naming conventions <https://pytest.readthedocs.io/en/reorganize-docs/new-docs/user/naming_conventions.html>`_

We don't need the Greeter example for this project, so delete it:

.. code-block:: bash

  $ rm contracts/Greeter
  4 rm tests/test_greeter.py

Now, before we start writing tests, pause for a moment: What are we actually testing? Obviously a contract, but what *is* a contract?

.. _what_is_a_contract

What is a Contract?
-------------------

The simplest definition of a contract is a compiled program that runs on the Ethereum blockchain.
It's a bytecode of instructions, saved on the blockchain, that a blockchain node can run.
The node gives this program a sandbox, a closed environment, to execute.

In a way, if the blockchain is the OS, then a contract is an executable that runs by the OS.
Everything else: syncing nodes, consensus, mining, is OS stuff. Yes, it's a smart
OS that magically syncs a lot of nodes, but the contract doesn't care - it just runs, and is allowed to use the API that the OS
gives it.

However, the term *contract* can be confusing, since it's used for several different things:

#. A bytecode program that is saved on the blockchain
#. A ``contract`` code in a Solidity source file
#. A Web3 ``contract`` object

Luckily, it can be even more confusing. You may have a Solidity source file of the ``Donator`` contract. If you deployed it
to ``testnet``, then we have another "contract", the code that sits on ``testnet``. When you deploy to ``mainnet``,
which is another blockchain, we now have three contracts: the source file, the bytecode on ``testnet``, and the bytecode on ``mainnet``.

But wait, there is more! To interact with an *existing* contract on say ``mainnet``, we need a Web3 "contract" *object*. This object does
not need the solidity source, since the bytcode is alreadt compiled and deployed. It does need the ABI,  the functions
and arguments structure of the *bytecode* contract's interface, and the address of this *bytecode* contract
on the mainnet.

.. note::
  To deploy a *new* ``Donator`` contract, maybe to another blockchain, or to another address on the same blockchain,
  we also need a Web3 contract *object*, but this time the object does require a compiled
  "contract"

Actually when we say ""contract", we deal with three different things:

#. **Contract Instance**: Bytecode on a blockchain
#. **Solidiy Source**: A Solidity contract definition, like ``contract Donator {...}``
#. **Web3 Object**: An object that provides methods to deploy a new contract instance, or interact with an existing one


Testing a Contract
------------------

Get the contract object
'''''''''''''''''''''''

The answer to the question "what are we actually testing" is: We test a bytecode program that runs on a blockchain. We test
a contract *instance*.

Ideally, for testing, we would need to take the Solidity source file, compile it, deploy it to a blockchain, create a Web3 contract
object that points to this instance, and handover this object to the test function so we can test it.

And here is where you will start to appreciate Populus, **which does all that for you in one line of code.**

Add the first test:

.. code-block:: shell

  $ nano tests/test_donatory.py

The test file should look as follows:

.. code-block:: python

  def test_default_usd_rate(chain):
      donator, deploy_tx_hash _ = chain.provider.get_or_deploy_contract('Donator')
      default_usd_rate = donator.call().default_usd_rate()
      assert default_usd_rate == 350


The magic happens with ``get_or_deploy_contract``. This function gets an existing contract if it exists on the blockchain, and if it
doesn't, it compiles the Solidity source, deploys it to the blockchain, creates a ``Contract`` object, exposes the deployed contract
as a *python object with python functions*, and returns this object to the test function.

From this point onward, you have a *Python* object, with *Python* methods, that correspond to the original deployed contract
bytecode on the blockchain. Cool, isn't it?

.. note::

    For the contract name you use the Solidity contract name, ``Donator``, and *not* the file name, ``Donator.sol``.
    A Solidity source file can include more than one contract definition (as a Python file can include more than one class definition).

Get the blockchain
''''''''''''''''''

Another bonus is the ``chain``, at ``def test_default_usd_rate(chain)``. It gives the test function a Python object
that corresponds to a running blockchain, the ``tester`` blockchain.
Reminder: The ``tester`` chain is ephemeral, saved only in memory, and will reset on every test run.

The ``chain`` argument is a py.test *fixture*: in py.test world it's a special argument that the test function can accept.
You don't have to declare or assign it, it's just ready and available for your function.

The Populus testing fixtures comes from the Populus py.test plug-in, which prepares for you several useful fixtures: ``project``,
``chain``, ``provider``, ``registrar`` and ``web3``. All these fixtures are part of the Populus API. See :ref:`populus_testing`

.. note::

  The tester chain creates and unlocks new accounts in each run, so you don't have to supply a private key or a wallet.


Run the First Test: Public State Variable
-----------------------------------------

We are ready for the first test: we have a test function that runs the ``tester`` chain, and using ``get_or_deploy_contract('Donator')``
it compiles ``Donator.sol``, deploys it to the ``tester`` chain, gets a Python contract object that wraps the actual contract's
bytecode on the chain, and assign this object to a variable, ``donator``.

Once we have the ``donator`` contract as a Python object, we can call any function of this contract. You get the *contract's*
interface with ``call()``. Reminder: ``call`` behaves exactly as a transaction, but does not alter state. It's like a "dry-run".
It's also useful to query the current state, without changing it.

The first test important line is:

.. code-block:: python

  default_usd_rate = donator.call().default_usd_rate()

In the Solidity source code we had:

.. code-block:: solidity

  ...
  uint public default_usd_rate;
  ...
  function Donator() {
    default_usd_rate = 350;
  }
  ...

To recap, ``default_usd_rate`` is a ``public`` variable, hence the compiler automatically created
an accessor function, a "get", that returns this variable. The test just used this function.


What is the expected retrun value? It's 350. We assigned to it 350 in the *constructor*, the function that runs once,
when the contract is created. The test function should deploy ``Donator`` on the ``tester`` chain, but nothing else is called afterwards,
so the initial value should not be changed.

Run the test:

.. code-block:: shell

  $ py.test --disable-pytest-warnings

  platform linux -- Python 3.5.2, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
  rootdir: /home/mary/projects/donations, inifile:
  plugins: populus-1.8.0, hypothesis-3.14.0
  collected 1 item s

  tests/test_donator.py .

  ================================================= 1 passed, 5 warnings in 0.29 seconds ======


Interim Summary
---------------

Congrats. Your first project test just passed.

Continue to a few more.

